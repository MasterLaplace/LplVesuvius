/**
 * @file main.cpp
 * @brief Flying through a scanned scroll, live, with the ground streaming in behind the eye.
 *
 * @warning **This app contains no rendering.** Every pixel is produced by `lpl::voxel::march` --
 * the same function the headless tool calls, with the same parameters -- and OpenGL is a BLITTER:
 * one textured quad. Drawing the volume a second time in GL would be a second renderer, free to
 * disagree with the one that writes the reproducible images somebody will draw conclusions from.
 * Same decision, and the same reasoning, as the desktop client in the engine tree.
 *
 * @warning **The camera does not collide with anything.** The subject is a scan, not a place with
 * floors, and an instrument whose operator can be stopped by a wall is a worse instrument. Flight
 * is the mode, not a cheat.
 *
 * @author MasterLaplace
 * @version 0.1.0
 * @copyright MIT License
 */

// @warning Engine headers FIRST. Xlib defines `None`, `Bool`, `Status` and `Success` as bare
// macros, and the engine has enumerators by those names -- including one in `history::Predicate`.
// Including X11 first turns an enum member into `0L` and the error points at a file this app never
// touches. Every project that mixes the two hits it once.
#include <lpl/scroll/HttpStore.hpp>
#include <lpl/scroll/Streamer.hpp>
#include <lpl/scroll/Volpkg.hpp>
#include <lpl/voxel/Raymarch.hpp>
#include <lpl/voxel/Minimap.hpp>
#include <lpl/voxel/Sheet.hpp>
#include <lpl/voxel/Surface.hpp>
#include <lpl/zarr/Array.hpp>

#include <GL/gl.h>
#include <GL/glx.h>
#include <X11/XKBlib.h>
#include <X11/Xatom.h>
#include <X11/Xlib.h>
#include <X11/Xutil.h>

#include <atomic>
#include <memory>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <ctime>
#include <string>
#include <thread>
#include <vector>

namespace {

using namespace lpl;

double seconds()
{
    timespec ts{};
    clock_gettime(CLOCK_MONOTONIC, &ts);
    return static_cast<double>(ts.tv_sec) + static_cast<double>(ts.tv_nsec) * 1e-9;
}

struct Options final {
    std::string volume = "PHerc0172/volumes/20241024131838-7.910um-53keV-masked.zarr";
    std::string bucket = scroll::kOpenDataBucket;
    std::string cache = std::string(std::getenv("HOME") ? std::getenv("HOME") : ".") + "/.cache/lpl-scroll";
    core::f32 corridor = 3.0f;
    core::i64 at[3]{-1, -1, -1};
    core::u32 width = 720u;
    core::u32 height = 450u;
    core::u32 finest = 1u;
    core::u32 coarsest = 4u;
    core::i32 radius = 1;
    core::u32 budget = 128u;
    core::f32 quantile = 0.133f;
    core::f32 window = 1.0f;
    core::u32 threads = 0u; ///< Zero means "as many as the machine has".
    core::u32 minimap = 220u;       ///< Panel edge in pixels; zero turns it off.
    core::u32 renderScale = 2u;
    /**< March at 1/N of the window and let the texture filter scale it up.

         @warning **The cost of this renderer is pixels, so this is the only lever with a factor of
         four in it.** Measured: 900x560 is 0.94 s a frame on twenty-two threads; at half that it
         is a quarter of the rays. The engine's own desktop client does exactly this and says why
         -- it rasterises small and scales up, so the host pays for an upload rather than a scene.
         One renders at full window size for a screenshot worth keeping. */
};

void usage()
{
    std::printf(
        "lpl-scrollfly — fly through a scanned scroll, live\n\n"
        "  --volume KEY / --bucket URL / --cache DIR   where the samples come from\n"
        "  --at Z Y X        start position in level-0 samples (default: the middle)\n"
        "  --size W H        window\n"
        "  --levels F C      finest and coarsest pyramid level (default 1 4)\n"
        "  --radius N        bricks around the eye per level (default 1)\n"
        "  --budget N        cap on resident bricks (default 128)\n"
        "  --corridor M      metres the gap between two sheets is staged at (default 3)\n"
        "  --quantile Q --window D   density curve (default 0.133, 1.0)\n"
        "  --threads N       marching threads (default: all cores)\n"
        "  --minimap N       size of the corner panel in pixels, 0 for none (default 220). It\n"
        "                    shows a cross-section of the WHOLE scroll from the coarsest pyramid\n"
        "                    level -- 37 MB for PHerc0172, loaded once -- with where you are and\n"
        "                    which way you face on it\n"
        "  --render-scale N  march at 1/N of the window and scale up (default 2). The cost is in\n"
        "                    pixels, so this is the one lever with a factor of four in it; 1 is\n"
        "                    full resolution, for a screenshot worth keeping\n\n"
        "In flight:  W/S or Z/S forward-back   A/D or Q/D strafe   R/F up-down   arrows look\n"
        "            (both QWERTY and AZERTY spellings are bound: the keysym follows the layout)\n"
        "            Shift faster, Ctrl slower   [ ] density window   , . quantile\n"
        "            T trace the sheet ahead of you   Y forget it\n"
        "            G shading   B boundary opacity   X x-ray the trace   P screenshot   Esc quit\n\n"
        "A screenshot writes the pose beside it, so the headless tool can reproduce it exactly.\n");
}

bool fetchText(zarr::IZarrStore &store, const char *key, std::string &out)
{
    std::vector<core::u8> buffer(1u << 20);
    const zarr::FetchResult r = store.read(key, buffer.data(), buffer.size());
    if (!r.ok())
        return false;
    out.assign(reinterpret_cast<const char *>(buffer.data()), r.size);
    return true;
}

} // namespace

int main(int argc, char **argv)
{
    Options o{};
    for (int i = 1; i < argc; ++i)
    {
        const std::string a = argv[i];
        auto next = [&](int n) { return i + n < argc ? argv[i + n] : nullptr; };
        if (a == "--help" || a == "-h") { usage(); return 0; }
        else if (a == "--volume" && next(1)) { o.volume = next(1); ++i; }
        else if (a == "--bucket" && next(1)) { o.bucket = next(1); ++i; }
        else if (a == "--cache" && next(1)) { o.cache = next(1); ++i; }
        else if (a == "--at" && next(3)) { for (int k = 0; k < 3; ++k) o.at[k] = std::atoll(next(k + 1)); i += 3; }
        else if (a == "--size" && next(2)) { o.width = static_cast<core::u32>(std::atoi(next(1)));
                                             o.height = static_cast<core::u32>(std::atoi(next(2))); i += 2; }
        else if (a == "--levels" && next(2)) { o.finest = static_cast<core::u32>(std::atoi(next(1)));
                                               o.coarsest = static_cast<core::u32>(std::atoi(next(2))); i += 2; }
        else if (a == "--radius" && next(1)) { o.radius = std::atoi(next(1)); ++i; }
        else if (a == "--budget" && next(1)) { o.budget = static_cast<core::u32>(std::atoi(next(1))); ++i; }
        else if (a == "--corridor" && next(1)) { o.corridor = static_cast<core::f32>(std::atof(next(1))); ++i; }
        else if (a == "--quantile" && next(1)) { o.quantile = static_cast<core::f32>(std::atof(next(1))); ++i; }
        else if (a == "--window" && next(1)) { o.window = static_cast<core::f32>(std::atof(next(1))); ++i; }
        else if (a == "--threads" && next(1)) { o.threads = static_cast<core::u32>(std::atoi(next(1))); ++i; }
        else if (a == "--render-scale" && next(1)) { o.renderScale = static_cast<core::u32>(std::atoi(next(1))); ++i; }
        else if (a == "--minimap" && next(1)) { o.minimap = static_cast<core::u32>(std::atoi(next(1))); ++i; }
        else { std::fprintf(stderr, "unknown argument '%s'\n\n", a.c_str()); usage(); return 2; }
    }

    const std::string prefix = o.bucket + "/" + o.volume;
    const std::string cacheRoot = o.cache + "/" + o.volume;
    scroll::HttpStore store(prefix.c_str(), cacheRoot.c_str());
    if (!store.valid())
    {
        std::fprintf(stderr, "no HTTP transport: this build has no libcurl\n");
        return 1;
    }

    const std::size_t slash = o.volume.find_last_of('/');
    const std::string leaf = slash == std::string::npos ? o.volume : o.volume.substr(slash + 1);
    const scroll::VolumeName name = scroll::parseVolumeName(leaf.c_str());
    if (!name.parsed)
    {
        std::fprintf(stderr, "'%s' carries no resolution in its name — refusing rather than\n"
                             "putting this scroll at somebody else's scale\n", leaf.c_str());
        return 1;
    }

    std::string attrs;
    core::u32 levels = fetchText(store, ".zattrs", attrs)
                           ? zarr::countMultiscaleLevels(attrs.c_str(), attrs.size()) : 0u;
    if (levels == 0u)
        levels = 1u;
    if (o.coarsest >= levels) o.coarsest = levels - 1u;
    if (o.finest > o.coarsest) o.finest = o.coarsest;

    std::vector<zarr::ArrayMeta> meta(levels);
    for (core::u32 lv = 0u; lv < levels; ++lv)
    {
        char key[64];
        std::snprintf(key, sizeof(key), "%u/.zarray", lv);
        std::string doc;
        if (!fetchText(store, key, doc) || !zarr::parseArrayMeta(doc.c_str(), doc.size(), meta[lv]))
        {
            std::fprintf(stderr, "level %u will not open\n", lv);
            return 1;
        }
    }

    const voxel::VolumeGeometry geometry = scroll::geometryOf(meta[0].shape, levels, name, o.corridor);
    if (!geometry.valid()) { std::fprintf(stderr, "unusable geometry\n"); return 1; }

    core::i64 startSample[3]{o.at[0], o.at[1], o.at[2]};
    for (core::u32 k = 0u; k < 3u; ++k)
        if (startSample[k] < 0) startSample[k] = geometry.samples[k] / 2;

    std::printf("%s — %.3f um, staged x%.0f, %.2f x %.2f x %.2f km walked, %u levels\n", leaf.c_str(),
                static_cast<double>(geometry.voxelMicrometres), static_cast<double>(geometry.metresPerMicrometre),
                static_cast<double>(geometry.extentMetres(0) / 1000.0f),
                static_cast<double>(geometry.extentMetres(1) / 1000.0f),
                static_cast<double>(geometry.extentMetres(2) / 1000.0f), levels);

    scroll::VolumeStreamer streamer(store, geometry, meta);
    voxel::ResidencyParams residency{};
    residency.finestLevel = o.finest;
    residency.coarsestLevel = o.coarsest;
    residency.ringRadius = o.radius;
    residency.budget = o.budget;
    const scroll::StreamReport first = streamer.update(residency, startSample);
    std::printf("resident %u bricks (%u loaded, %u all-fill), %.1f MB\n", streamer.residentCount(), first.loaded,
                first.absent, static_cast<double>(first.bytes) / 1e6);
    if (streamer.residentCount() == 0u) { std::fprintf(stderr, "nothing resident\n"); return 1; }

    voxel::DensityProfile profile = streamer.measureProfile(o.quantile, o.window);
    const scroll::PapyrusMetrics metrics{};
    const core::f32 sheetSamples = metrics.sheetMicrometres / geometry.voxelMicrometres;
    auto rebuildCurve = [&]() {
        return voxel::rampTransfer(profile.floorSample, profile.sheetSample,
                                   voxel::alphaForOpaqueAfter(sheetSamples, 0.85f));
    };
    voxel::TransferFunction transfer = rebuildCurve();

    // ── the window ─────────────────────────────────────────────────────────
    Display *display = XOpenDisplay(nullptr);
    if (display == nullptr) { std::fprintf(stderr, "no X display\n"); return 1; }
    int attributes[] = {GLX_RGBA, GLX_DOUBLEBUFFER, None};
    XVisualInfo *visual = glXChooseVisual(display, DefaultScreen(display), attributes);
    if (visual == nullptr) { std::fprintf(stderr, "no GLX visual\n"); return 1; }

    XSetWindowAttributes swa{};
    swa.colormap = XCreateColormap(display, RootWindow(display, visual->screen), visual->visual, AllocNone);
    swa.event_mask = ExposureMask | KeyPressMask | KeyReleaseMask | StructureNotifyMask;
    Window window = XCreateWindow(display, RootWindow(display, visual->screen), 0, 0, o.width, o.height, 0,
                                  visual->depth, InputOutput, visual->visual, CWColormap | CWEventMask, &swa);

    // WSLg derives an application identity from WM_CLASS, and Xlib does not set it: without this
    // the window is created, mapped and reported viewable, and never appears on any screen.
    XClassHint classHint{};
    char instanceName[] = "lplscrollfly";
    char className[] = "Lplwin";
    classHint.res_name = instanceName;
    classHint.res_class = className;
    XSetClassHint(display, window, &classHint);
    XStoreName(display, window, "lpl-scrollfly");

    Atom deleteWindow = XInternAtom(display, "WM_DELETE_WINDOW", False);
    XSetWMProtocols(display, window, &deleteWindow, 1);
    XMapWindow(display, window);
    GLXContext context = glXCreateContext(display, visual, nullptr, GL_TRUE);
    glXMakeCurrent(display, window, context);

    GLuint texture = 0;
    glGenTextures(1, &texture);
    glBindTexture(GL_TEXTURE_2D, texture);
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR);
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR);
    glEnable(GL_TEXTURE_2D);

    if (o.renderScale == 0u)
        o.renderScale = 1u;
    const core::u32 renderWidth = o.width / o.renderScale > 0u ? o.width / o.renderScale : 1u;
    const core::u32 renderHeight = o.height / o.renderScale > 0u ? o.height / o.renderScale : 1u;
    std::vector<core::u32> frame(static_cast<std::size_t>(renderWidth) * renderHeight, 0u);
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, static_cast<GLsizei>(renderWidth), static_cast<GLsizei>(renderHeight), 0,
                 GL_BGRA, GL_UNSIGNED_BYTE, frame.data());
    std::printf("window %ux%u, marching %ux%u (scale %u)\n", o.width, o.height, renderWidth, renderHeight,
                o.renderScale);

    const core::f32 mps = geometry.metresPerSample();
    // ── the atlas: the whole subject at its coarsest level, loaded once ────
    // Not the bricks the walk uses. Those cover the few metres already on screen, which is the one
    // thing somebody lost does not need. The coarsest level of this volume is 37 MB against 1.2 TB
    // for its finest, so the whole scroll is resident permanently and costs nothing to consult.
    std::vector<core::u8> sliceSamples;
    std::vector<core::u8> longSamples;
    voxel::VolumeSlice lengthwise{};
    std::unique_ptr<scroll::VolumeStreamer> atlas;
    voxel::VolumeSlice slice{};
    if (o.minimap > 0u)
    {
        // A pointer, because a streamer holds a reference to its store and so cannot be moved --
        // which a vector insists on being able to do.
        atlas = std::make_unique<scroll::VolumeStreamer>(store, geometry, meta);
        voxel::ResidencyParams whole{};
        whole.finestLevel = levels - 1u;
        whole.coarsestLevel = levels - 1u;
        // Enough rings to reach every corner from the middle, whatever the shape.
        core::i32 reach = 1;
        for (core::u32 axis = 0u; axis < 3u; ++axis)
            reach = reach > geometry.bricksAtLevel(axis, levels - 1u) ? reach : geometry.bricksAtLevel(axis, levels - 1u);
        whole.ringRadius = reach;
        whole.budget = voxel::kMaxResidentBricks;
        const core::i64 middle[3]{geometry.samples[0] / 2, geometry.samples[1] / 2, geometry.samples[2] / 2};
        const scroll::StreamReport atlasReport = atlas->update(whole, middle);
        std::printf("atlas   level %u: %u bricks, %u all-fill, %.1f MB\n", levels - 1u, atlasReport.loaded,
                    atlasReport.absent, static_cast<double>(atlasReport.bytes) / 1e6);
        if (atlas->residentCount() == 0u)
        {
            // Said rather than shown blank: a panel that draws nothing looks exactly like a panel
            // whose subject is empty.
            std::printf("        (nothing resident at that level -- no minimap)\n");
            atlas.reset();
        }
        else
        {
            slice.width = 192u;
            slice.height = 192u;
            sliceSamples.assign(static_cast<std::size_t>(slice.width) * slice.height, 0u);
            slice.samples = sliceSamples.data();
            slice.axis = voxel::SliceAxis::Z;

            longSamples.assign(256u * 96u, 0u);
            lengthwise.samples = longSamples.data();
            lengthwise.width = 256u;
            lengthwise.height = 96u;
            lengthwise.axis = voxel::SliceAxis::Y;
        }
    }

    voxel::FreeCamera camera;
    camera.position = {static_cast<core::f32>(startSample[2]) * mps, static_cast<core::f32>(startSample[1]) * mps,
                       static_cast<core::f32>(startSample[0]) * mps};

    voxel::MarchParams march{};
    march.maxDistanceMetres = geometry.extentMetres(0);

    core::u32 threadCount = o.threads;
    if (threadCount == 0u)
        threadCount = std::thread::hardware_concurrency();
    if (threadCount == 0u)
        threadCount = 1u;
    std::printf("marching on %u threads. W/S A/D R/F to move, arrows to look, P for a screenshot.\n", threadCount);

    // The live trace: a seed dropped ahead of the eye, walked, and drawn where it was walked.
    // Rasterised into the frame's own projection every frame, because the camera moves and a
    // surface projected once would slide off the samples it came from.
    std::vector<lpl::math::Vec3<core::f32>> patchPoints;
    std::vector<core::u32> patchIndices;
    std::vector<core::f32> surfaceDepth;
    std::vector<core::f32> surfaceFacing;
    voxel::SheetPatch patch{};
    std::vector<lpl::math::Vec3<core::f32>> tracedNormals;
    voxel::SurfaceMesh traced{};
    bool xray = false;

    bool held[8]{};
    enum { kFwd, kBack, kLeft, kRight, kUp, kDown, kFast, kSlow };
    bool running = true;
    double last = seconds();
    core::u32 shots = 0u;
    core::i64 residentAt[3]{startSample[0], startSample[1], startSample[2]};

    while (running)
    {
        while (XPending(display) > 0)
        {
            XEvent event;
            XNextEvent(display, &event);
            if (event.type == ClientMessage && static_cast<Atom>(event.xclient.data.l[0]) == deleteWindow)
                running = false;
            else if (event.type == KeyPress || event.type == KeyRelease)
            {
                const bool down = event.type == KeyPress;
                const KeySym sym = XkbKeycodeToKeysym(display, static_cast<KeyCode>(event.xkey.keycode), 0, 0);
                switch (sym)
                {
                // ⚠ **Both layouts, because the keysym follows the LAYOUT and not the key.**
                // XkbKeycodeToKeysym asks for group zero, which on a French keyboard is AZERTY:
                // the key in the W position reports `z` and the one in the A position reports `q`.
                // Binding only WASD leaves the controls dead on that keyboard with nothing to say
                // why -- the window opens, the mouse works, and walking does nothing. Accepting
                // both spellings costs four lines and no ambiguity: none of z, q, w or a is bound
                // to anything else here.
                case XK_w: case XK_W: case XK_z: case XK_Z: held[kFwd] = down; break;
                case XK_s: case XK_S: held[kBack] = down; break;
                case XK_a: case XK_A: case XK_q: case XK_Q: held[kLeft] = down; break;
                case XK_d: case XK_D: held[kRight] = down; break;
                case XK_r: case XK_R: held[kUp] = down; break;
                case XK_f: case XK_F: held[kDown] = down; break;
                case XK_Shift_L: case XK_Shift_R: held[kFast] = down; break;
                case XK_Control_L: case XK_Control_R: held[kSlow] = down; break;
                case XK_Left: if (down) camera.turn(-0.08f, 0.0f); break;
                case XK_Right: if (down) camera.turn(0.08f, 0.0f); break;
                case XK_Up: if (down) camera.turn(0.0f, 0.06f); break;
                case XK_Down: if (down) camera.turn(0.0f, -0.06f); break;
                case XK_bracketleft: if (down) { o.window = o.window > 0.2f ? o.window - 0.1f : 0.1f;
                                                 profile = streamer.measureProfile(o.quantile, o.window);
                                                 transfer = rebuildCurve();
                                                 std::printf("window %.1f sd -> %u..%u\n",
                                                             static_cast<double>(o.window), profile.floorSample,
                                                             profile.sheetSample); } break;
                case XK_bracketright: if (down) { o.window += 0.1f;
                                                  profile = streamer.measureProfile(o.quantile, o.window);
                                                  transfer = rebuildCurve();
                                                  std::printf("window %.1f sd -> %u..%u\n",
                                                              static_cast<double>(o.window), profile.floorSample,
                                                              profile.sheetSample); } break;
                case XK_comma: if (down) { o.quantile = o.quantile > 0.015f ? o.quantile - 0.01f : 0.005f;
                                           profile = streamer.measureProfile(o.quantile, o.window);
                                           transfer = rebuildCurve();
                                           std::printf("quantile %.3f -> %u..%u\n", static_cast<double>(o.quantile),
                                                       profile.floorSample, profile.sheetSample); } break;
                case XK_period: if (down) { o.quantile += 0.01f;
                                            profile = streamer.measureProfile(o.quantile, o.window);
                                            transfer = rebuildCurve();
                                            std::printf("quantile %.3f -> %u..%u\n", static_cast<double>(o.quantile),
                                                        profile.floorSample, profile.sheetSample); } break;
                case XK_g: case XK_G: if (down) { march.shading = march.shading > 0.0f ? 0.0f : 0.85f;
                                                  std::printf("shading %s\n", march.shading > 0.0f ? "on" : "off"); }
                                      break;
                case XK_b: case XK_B: if (down) { march.boundaryOpacity = march.boundaryOpacity > 0.0f ? 0.0f : 0.7f;
                                                  std::printf("boundary opacity %s\n",
                                                              march.boundaryOpacity > 0.0f ? "on" : "off"); }
                                      break;
                case XK_p: case XK_P:
                    if (down)
                    {
                        char path[256];
                        std::snprintf(path, sizeof(path), "scrollfly-%03u.ppm", shots++);
                        std::FILE *f = std::fopen(path, "wb");
                        if (f != nullptr)
                        {
                            std::fprintf(f, "P6\n%u %u\n255\n", renderWidth, renderHeight);
                            for (core::u32 p : frame)
                            {
                                const unsigned char rgb[3]{static_cast<unsigned char>((p >> 16) & 0xFFu),
                                                           static_cast<unsigned char>((p >> 8) & 0xFFu),
                                                           static_cast<unsigned char>(p & 0xFFu)};
                                std::fwrite(rgb, 1, 3, f);
                            }
                            std::fclose(f);
                            // The pose beside the picture: a screenshot nobody can reproduce is a
                            // souvenir, and this tool is supposed to produce measurements.
                            std::printf("wrote %s\n  lpl-scrollwalk --volume %s --at %lld %lld %lld "
                                        "--yaw %.4f --pitch %.4f --size %u %u --levels %u %u --radius %d "
                                        "--quantile %.4f --window %.2f\n",
                                        path, o.volume.c_str(),
                                        static_cast<long long>(camera.position.z / mps),
                                        static_cast<long long>(camera.position.y / mps),
                                        static_cast<long long>(camera.position.x / mps), static_cast<double>(camera.yaw),
                                        static_cast<double>(camera.pitch), renderWidth, renderHeight, o.finest, o.coarsest,
                                        o.radius, static_cast<double>(o.quantile), static_cast<double>(o.window));
                        }
                    }
                    break;
                case XK_x: case XK_X: if (down) { xray = !xray; std::printf("x-ray %s\n", xray ? "on" : "off"); }
                                      break;
                case XK_y: case XK_Y: if (down) { patch = voxel::SheetPatch{}; traced = voxel::SurfaceMesh{};
                                                  std::printf("trace forgotten\n"); } break;
                case XK_t: case XK_T:
                    if (down)
                    {
                        // Five metres ahead: far enough to be looking at the sheet rather than
                        // standing in it, near enough to be inside the resident bricks.
                        const voxel::Eye at = camera.eye();
                        const lpl::math::Vec3<core::f32> ahead{at.position.x + at.forward.x * 5.0f,
                                                               at.position.y + at.forward.y * 5.0f,
                                                               at.position.z + at.forward.z * 5.0f};
                        voxel::SheetTraceParams trace{};
                        trace.floorSample = static_cast<core::u8>(profile.mean);
                        constexpr core::u32 kRows = 32u;
                        constexpr core::u32 kColumns = 64u;
                        patchPoints.resize(static_cast<std::size_t>(kRows) * kColumns);
                        patch = voxel::traceSheetPatch(streamer.mosaic(),
                                                       lpl::math::Vec3<core::f32>{ahead.x / mps, ahead.y / mps,
                                                                                  ahead.z / mps},
                                                       trace, kRows, kColumns, patchPoints.data());
                        if (patch.rows == 0u)
                        {
                            // Refused rather than drawn flat: a seed with no sheet under it has no
                            // surface, and showing one would be the tool inventing the answer.
                            std::printf("no sheet ahead: the samples there carry no usable normal\n");
                            traced = voxel::SurfaceMesh{};
                            break;
                        }
                        patchIndices.resize(static_cast<std::size_t>(kRows) * kColumns * 6u);
                        const core::u32 written = voxel::patchIndices(patch, patchIndices.data(),
                                                                      static_cast<core::u32>(patchIndices.size()));
                        traced.points = patch.points;
                        traced.indices = patchIndices.data();
                        traced.pointCount = patch.rows * patch.columns;
                        traced.indexCount = written;
                        tracedNormals.resize(traced.pointCount);
                        voxel::computeVertexNormals(traced, tracedNormals.data());
                        traced.normals = tracedNormals.data();
                        surfaceDepth.assign(static_cast<std::size_t>(renderWidth) * renderHeight, voxel::kNoSurface);
                        surfaceFacing.assign(surfaceDepth.size(), 0.0f);
                        static const char *kWhy[5]{"budget", "left the matter", "left the bricks",
                                                   "would have jumped", "no usable normal"};
                        std::printf("traced %ux%u, %u triangles, %u short rows, %u refused;", patch.rows,
                                    patch.columns, written / 3u, patch.shortRows, patch.refusedJumps);
                        for (core::u32 i = 0u; i < 5u; ++i)
                            if (patch.stops[i] != 0u)
                                std::printf(" %u %s,", patch.stops[i], kWhy[i]);
                        std::printf("\n");
                    }
                    break;
                case XK_Escape: running = false; break;
                default: break;
                }
            }
        }

        const double now = seconds();
        const core::f32 dt = static_cast<core::f32>(now - last > 0.25 ? 0.25 : now - last);
        last = now;

        core::f32 speed = 6.0f;
        if (held[kFast]) speed *= 6.0f;
        if (held[kSlow]) speed *= 0.2f;
        camera.move(static_cast<core::f32>(held[kFwd]) - static_cast<core::f32>(held[kBack]),
                    static_cast<core::f32>(held[kRight]) - static_cast<core::f32>(held[kLeft]),
                    static_cast<core::f32>(held[kUp]) - static_cast<core::f32>(held[kDown]), speed * dt);
        const voxel::Eye eye = camera.eye();

        // Restream only when the eye has left the brick it was planned around: replanning every
        // frame would ask the store the same questions sixty times a second, and the store is a
        // network.
        const core::i64 nowSample[3]{static_cast<core::i64>(camera.position.z / mps), static_cast<core::i64>(camera.position.y / mps),
                                     static_cast<core::i64>(camera.position.x / mps)};
        const core::i64 span = voxel::brickSpanInBaseSamples(o.finest) / 2;
        bool moved = false;
        for (core::u32 k = 0u; k < 3u; ++k)
        {
            const core::i64 d = nowSample[k] - residentAt[k];
            if ((d < 0 ? -d : d) > span)
                moved = true;
        }
        if (moved)
        {
            const scroll::StreamReport r = streamer.update(residency, nowSample);
            for (core::u32 k = 0u; k < 3u; ++k)
                residentAt[k] = nowSample[k];
            if (r.loaded != 0u || r.released != 0u)
                std::printf("stream: +%u -%u =%u  (%.1f MB)\n", r.loaded, r.released, r.kept,
                            static_cast<double>(r.bytes) / 1e6);
        }

        // Re-rasterised each frame into this frame's projection.
        march.surfaceCount = 0u;
        if (traced.valid() && !surfaceDepth.empty())
        {
            voxel::SurfaceDepth target{surfaceDepth.data(), surfaceFacing.data(), nullptr, nullptr, renderWidth,
                                       renderHeight};
            voxel::clearSurfaceDepth(target);
            (void) voxel::rasteriseSurface(traced, geometry, eye, target);
            voxel::SurfaceLayer &slot = march.surfaces[march.surfaceCount++];
            slot.depth = surfaceDepth.data();
            slot.facing = surfaceFacing.data();
            slot.throughMatter = xray;
        }

        const double tMarch = seconds();
        if (threadCount == 1u)
        {
            (void) voxel::march(streamer.mosaic(), geometry, profile, transfer, eye, march, frame.data(),
                                renderWidth, renderHeight, 0u, renderHeight);
        }
        else
        {
            // Bands, which the marcher already supports and the tests already assert renders the
            // same frame as one pass. A thread that changed the picture would be a second renderer.
            std::vector<std::thread> pool;
            // ⚠ Interleaved rows, not contiguous slabs. A frame's cost is wildly uneven top to
            // bottom -- a ray that leaves the volume immediately costs nothing, one down the
            // length of a sheet costs everything -- so slabs leave most threads waiting on the one
            // that got the expensive half.
            for (core::u32 t = 0u; t < threadCount; ++t)
            {
                pool.emplace_back([&, t]() {
                    for (core::u32 row = t; row < renderHeight; row += threadCount)
                        (void) voxel::march(streamer.mosaic(), geometry, profile, transfer, eye, march, frame.data(),
                                            renderWidth, renderHeight, row, 1u);
                });
            }
            for (std::thread &t : pool)
                t.join();
        }
        const double marchSeconds = seconds() - tMarch;

        // The panel is drawn into the frame AFTER the march, so it costs one small blit and never
        // competes with the volume for rays.
        if (atlas && o.minimap > 0u)
        {
            // Two panels: the cross-section says which turn of the spiral you are in, the long
            // view says how far along the scroll -- and neither can be read off the other.
            const core::u32 panel = o.minimap / o.renderScale > 32u ? o.minimap / o.renderScale : 32u;

            slice.at = static_cast<core::i64>(eye.position.z / mps);
            (void) voxel::extractSlice(atlas->mosaic(), geometry, slice);
            voxel::MinimapStyle across{};
            across.width = panel < renderWidth ? panel : renderWidth;
            across.height = panel < renderHeight ? panel : renderHeight;
            across.left = renderWidth - across.width;
            across.top = 0u;
            voxel::drawMinimap(frame.data(), renderWidth, renderHeight, across, slice, geometry, eye);

            lengthwise.at = static_cast<core::i64>(eye.position.y / mps);
            (void) voxel::extractSlice(atlas->mosaic(), geometry, lengthwise);
            voxel::MinimapStyle along{};
            along.width = across.width;
            along.height = across.width / 3u > 20u ? across.width / 3u : 20u;
            along.left = across.left;
            along.top = across.height + 4u;
            if (along.top + along.height <= renderHeight)
                voxel::drawMinimap(frame.data(), renderWidth, renderHeight, along, lengthwise, geometry, eye);
        }

        glTexSubImage2D(GL_TEXTURE_2D, 0, 0, 0, static_cast<GLsizei>(renderWidth), static_cast<GLsizei>(renderHeight),
                        GL_BGRA, GL_UNSIGNED_BYTE, frame.data());
        glMatrixMode(GL_PROJECTION);
        glLoadIdentity();
        glOrtho(0.0, 1.0, 1.0, 0.0, -1.0, 1.0); // y down: row 0 of the frame is the top row.
        glMatrixMode(GL_MODELVIEW);
        glLoadIdentity();
        glBegin(GL_QUADS);
        glTexCoord2f(0.0f, 0.0f); glVertex2f(0.0f, 0.0f);
        glTexCoord2f(1.0f, 0.0f); glVertex2f(1.0f, 0.0f);
        glTexCoord2f(1.0f, 1.0f); glVertex2f(1.0f, 1.0f);
        glTexCoord2f(0.0f, 1.0f); glVertex2f(0.0f, 1.0f);
        glEnd();
        glXSwapBuffers(display, window);

        static double reported = 0.0;
        if (now - reported > 2.0)
        {
            reported = now;
            std::printf("%.1f fps (%.0f ms marching), %u bricks resident, sample (%lld, %lld, %lld)\n",
                        1.0 / (marchSeconds > 1e-6 ? marchSeconds : 1e-6), marchSeconds * 1000.0,
                        streamer.residentCount(), static_cast<long long>(nowSample[0]),
                        static_cast<long long>(nowSample[1]), static_cast<long long>(nowSample[2]));
        }
    }

    glXMakeCurrent(display, None, nullptr);
    glXDestroyContext(display, context);
    XDestroyWindow(display, window);
    XCloseDisplay(display);
    return 0;
}
