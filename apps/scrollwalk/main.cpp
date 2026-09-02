/**
 * @file main.cpp
 * @brief Flying through a real scanned scroll, and writing down what the eye saw.
 *
 * @warning **A pose in, an image out, and nothing else.** No window, no input loop, no clock: the
 * same pose renders the same frame, so a picture from this tool is a measurement somebody else can
 * repeat rather than a screenshot somebody happened to take. The interactive window is a different
 * program that will call the same functions.
 *
 * @warning **Nothing here decides anything about papyrus.** The renderer is `lpl::voxel`, the
 * format is `lpl::zarr`, the transport is `lpl::scroll::HttpStore` and the physical constants are
 * `lpl::scroll::PapyrusMetrics`. This file is the wiring, and its length is the honest measure of
 * how much of the work the engine already does.
 *
 * @author MasterLaplace
 * @version 0.1.0
 * @copyright MIT License
 */

#include <lpl/scroll/HttpStore.hpp>
#include <lpl/scroll/Streamer.hpp>
#include <lpl/scroll/Segment.hpp>
#include <lpl/scroll/Volpkg.hpp>
#include <lpl/voxel/Raymarch.hpp>
#include <lpl/voxel/Minimap.hpp>
#include <lpl/voxel/Sheet.hpp>
#include <lpl/voxel/Surface.hpp>
#include <lpl/voxel/Residency.hpp>
#include <lpl/zarr/Array.hpp>

#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <ctime>
#include <memory>
#include <string>
#include <thread>
#include <vector>

namespace {

using namespace lpl;

struct Options final {
    std::string volume = "PHerc0172/volumes/20241024131838-7.910um-53keV-masked.zarr";
    std::string bucket = scroll::kOpenDataBucket;
    std::string cache = std::string(std::getenv("HOME") ? std::getenv("HOME") : ".") + "/.cache/lpl-scroll";
    std::string out = "scrollwalk.ppm";
    core::f32 corridor = 3.0f;      ///< Metres between two sheets. The staging decision.
    core::i64 at[3]{-1, -1, -1};    ///< Eye, in level-0 samples. Negative means "the middle".
    core::f32 yaw = 0.0f;           ///< Radians about the vertical.
    core::f32 pitch = 0.0f;
    core::u32 width = 640u;
    core::u32 height = 400u;
    core::u32 finest = 1u;          ///< Best level to request. Level 0 is 1.2 TB; start one up.
    core::u32 coarsest = 4u;
    core::i32 radius = 1;
    core::u32 budget = 96u;
    core::f32 quantile = 0.133f;    ///< Sheet duty cycle: 40 um of sheet per 300 um of pitch.
    core::f32 window = 1.0f;        ///< Window width below that, in measured deviations.
    core::f32 shading = 0.85f;      ///< Gradient lighting, 0 to 1.
    core::f32 boundary = 0.7f;      ///< Gradient-magnitude opacity modulation, 0 to 1.
    core::f32 blend = 24.0f;        ///< Level-blend band, in level-0 samples.
    core::f32 step = 1.0f;          ///< March step, in level-0 samples.
    std::string debug;              ///< level | gradient | shade | steps
    std::string ink;                ///< A co-registered prediction volume, off unless asked for.
    core::f32 inkConfidence = 0.0f; ///< What that map is actually worth, measured elsewhere.
    core::i64 traceFrom[3]{-1, -1, -1}; ///< Seed a sheet trace here, in level-0 samples.
    core::u32 traceRows = 48u;
    core::u32 traceColumns = 96u;
    core::f32 traceJump = 0.0f;     ///< Zero keeps the module default, which carries its own reasoning.
    core::i32 traceRadius = 2;      ///< Structure-tensor window.
    core::f32 surfaceOpacity = 0.55f;
    core::u8 traceFloor = 0u;       ///< Zero means "the measured mean".
    bool surfaceThrough = false;    ///< X-ray the traced sheet through the matter in front of it.
    std::string segment;            ///< A published segment mesh to put beside our own trace.
    core::f32 segmentScale = 1.0f;  ///< Nothing in an OBJ says which resolution it was written for.
    std::string traceExport;        ///< Write our own trace out, in the corpus's own format.
    std::string segmentInk;         ///< A prediction painted on the segment, in its own flattening.
    core::f32 segmentInkConfidence = 0.0f;
    core::f32 traceRelax = 0.0f;    ///< Pull the patch toward its own neighbourhood. Alters geometry.
    core::u32 traceRelaxPasses = 4u;
    core::i32 traceSmooth = -1;     ///< Negative keeps the module default.
    core::u32 threads = 1u;         ///< Marching threads. One keeps the tool reproducible by default.
    core::u32 repeat = 1u;          ///< Render the frame N times and report the best: a bench mode.
    core::u32 minimap = 0u;         ///< Corner panel edge in pixels; zero for none.
};

void usage()
{
    // The surface IS the documentation: a flag whose meaning is only in a README is a flag that
    // drifts from it.
    std::printf(
        "lpl-scrollwalk — fly through a scanned scroll and write down what the eye saw\n\n"
        "  --volume KEY      volume path inside the bucket\n"
        "                    (default: PHerc0172/volumes/20241024131838-7.910um-53keV-masked.zarr)\n"
        "  --bucket URL      base URL (default: the Vesuvius Challenge open data bucket)\n"
        "  --cache DIR       where fetched chunks are kept. NOT a tmpfs: /tmp is memory on many\n"
        "                    systems, so a cache there is the thing it exists to avoid\n"
        "  --out FILE.ppm    image to write\n"
        "  --at Z Y X        eye position in level-0 samples (default: the middle of the volume)\n"
        "  --yaw R --pitch R look direction, radians\n"
        "  --size W H        framebuffer\n"
        "  --levels F C      finest and coarsest pyramid level to request (default 1 4)\n"
        "  --radius N        bricks around the eye per level (default 1)\n"
        "  --budget N        hard cap on bricks fetched (default 96)\n"
        "  --corridor M      metres the gap between two sheets is staged at (default 3)\n"
        "  --quantile Q      fraction of matter treated as sheet (default 0.133)\n"
        "  --window D        window width below it, in measured deviations (default 1.0).\n"
        "  --shading D       gradient lighting, 0 disables (default 0.85)\n"
        "  --boundary D      gradient-magnitude opacity, 0 disables (default 0.7)\n"
        "  --blend N         level-blend band in samples, 0 disables (default 24)\n"
        "  --step N          march step in level-0 samples (default 1)\n"
        "  --threads N       marching threads (default 1: a measurement should not depend on\n"
        "                    how busy the machine is)\n"
        "  --repeat N        render N times and report the best; for measuring, not for looking\n"
        "  --minimap N       draw a cross-section of the WHOLE scroll in the corner, N pixels\n"
        "                    across, with where the eye is and which way it faces. Off by default:\n"
        "                    an image meant as a measurement should not carry furniture\n"
        "  --debug WHAT      paint an intermediate instead of the picture:\n"
        "                    level | gradient | shade | steps | normal\n"
        "  --ink KEY         a co-registered prediction volume, painted over the scan\n"
        "  --ink-confidence D  what that map is worth, in [0,1], from a measurement made\n"
        "                    elsewhere. It MULTIPLIES the tint: a map worth 0.55 must not\n"
        "                    look as solid as one worth 0.95. Zero, the default, shows the\n"
        "                    scan and nothing else\n"
        "  --trace-from Z Y X  walk the sheet passing through this point and draw it inside\n"
        "                    the scan. Where no segment exists, this is how one comes to be:\n"
        "                    the walk refuses to step onto the neighbouring sheet and says so\n"
        "  --trace-size R C  rows and columns of the patch (default 48 96)\n"
        "  --trace-jump D    recentring beyond D samples is a CHANGE OF SHEET and is refused\n"
        "                    (default 3, and the reasoning is in the module). Raising it lets the\n"
        "                    half the spacing between sheets and it will happily follow the\n"
        "                    wrong one, smoothly and plausibly\n"
        "  --trace-relax D   pull the patch toward its own neighbourhood, in [0,1]. ALTERS the\n"
        "                    traced geometry, so it is off by default and the roughness is\n"
        "                    printed before and after -- a surface that looks crumpled and a\n"
        "                    sheet that IS crumpled are different claims\n"
        "  --trace-relax-passes N  repeats (default 4)\n"
        "  --trace-smooth N  radius of the average taken when looking for the ridge (default 1).\n"
        "                    This is not smoothing the result: it is asking the same question of\n"
        "                    a less noisy field, which is where the corrugation comes from\n"
        "  --trace-radius N  structure-tensor window (default 2). Smaller and noise orients the\n"
        "                    normal; larger and the window spans two sheets\n"
        "  --trace-floor N   below this sample value the walk has left the sheet. Defaults to the\n"
        "                    measured mean, NOT the render window: that window keeps only the\n"
        "                    brightest few per cent so the picture reads, and a walk needs the\n"
        "                    whole ridge\n"
        "  --surface-opacity D  how solidly the traced sheet paints (default 0.55). Under one on\n"
        "                    purpose: a surface you can see through is one you can check\n"
        "  --segment FILE.obj  load a published segment and draw it beside our own trace, in a\n"
        "                    different colour. With --trace-from, the distance between the two is\n"
        "                    measured and printed -- median, worst, and how much of ours found\n"
        "                    anything to compare against at all\n"
        "  --trace-export F.obj  write our trace out as OBJ, in level-0 sample coordinates and\n"
        "                    the same axis order the corpus writes -- so it can be loaded back,\n"
        "                    compared, or handed to other tooling\n"
        "  --segment-ink F.pgm  a prediction painted ON the segment, read through the texture\n"
        "                    coordinates the OBJ carries -- which is where the corpus's ink maps\n"
        "                    actually live. PGM or PPM: PNG needs a decompressor this would carry\n"
        "                    forever, and the conversion is one line of Pillow\n"
        "  --segment-ink-confidence D  what that map is worth, in [0,1]. It MULTIPLIES the tint\n"
        "  --segment-scale S  multiplier on its vertices; nothing in an OBJ says which resolution\n"
        "                    it was written for, so this is a parameter rather than a guess\n"
        "  --surface-through  draw the sheet THROUGH the matter in front of it. Off by default,\n"
        "                    because a picture where the inference is never hidden by the\n"
        "                    evidence is a picture that cannot disagree with it\n"
        "                    Wide paints fog; narrow paints structure against a clear medium\n\n"
        "The same arguments always produce the same image; that is what makes it a measurement.\n");
}

bool fetchText(scroll::HttpStore &store, const char *key, std::string &out)
{
    std::vector<core::u8> buffer(1u << 20);
    const zarr::FetchResult r = store.read(key, buffer.data(), buffer.size());
    if (!r.ok())
        return false;
    out.assign(reinterpret_cast<const char *>(buffer.data()), r.size);
    return true;
}

double seconds()
{
    timespec ts{};
    clock_gettime(CLOCK_MONOTONIC, &ts);
    return static_cast<double>(ts.tv_sec) + static_cast<double>(ts.tv_nsec) * 1e-9;
}

} // namespace

int main(int argc, char **argv)
{
    Options o{};
    for (int i = 1; i < argc; ++i)
    {
        const std::string a = argv[i];
        auto next = [&](int n) { return i + n < argc ? argv[i + n] : nullptr; };
        if (a == "--help" || a == "-h")
        {
            usage();
            return 0;
        }
        else if (a == "--volume" && next(1)) { o.volume = next(1); ++i; }
        else if (a == "--bucket" && next(1)) { o.bucket = next(1); ++i; }
        else if (a == "--cache" && next(1)) { o.cache = next(1); ++i; }
        else if (a == "--out" && next(1)) { o.out = next(1); ++i; }
        else if (a == "--at" && next(3))
        {
            for (int k = 0; k < 3; ++k)
                o.at[k] = std::atoll(next(k + 1));
            i += 3;
        }
        else if (a == "--yaw" && next(1)) { o.yaw = static_cast<core::f32>(std::atof(next(1))); ++i; }
        else if (a == "--pitch" && next(1)) { o.pitch = static_cast<core::f32>(std::atof(next(1))); ++i; }
        else if (a == "--size" && next(2))
        {
            o.width = static_cast<core::u32>(std::atoi(next(1)));
            o.height = static_cast<core::u32>(std::atoi(next(2)));
            i += 2;
        }
        else if (a == "--levels" && next(2))
        {
            o.finest = static_cast<core::u32>(std::atoi(next(1)));
            o.coarsest = static_cast<core::u32>(std::atoi(next(2)));
            i += 2;
        }
        else if (a == "--radius" && next(1)) { o.radius = std::atoi(next(1)); ++i; }
        else if (a == "--budget" && next(1)) { o.budget = static_cast<core::u32>(std::atoi(next(1))); ++i; }
        else if (a == "--corridor" && next(1)) { o.corridor = static_cast<core::f32>(std::atof(next(1))); ++i; }
        else if (a == "--quantile" && next(1)) { o.quantile = static_cast<core::f32>(std::atof(next(1))); ++i; }
        else if (a == "--window" && next(1)) { o.window = static_cast<core::f32>(std::atof(next(1))); ++i; }
        else if (a == "--shading" && next(1)) { o.shading = static_cast<core::f32>(std::atof(next(1))); ++i; }
        else if (a == "--boundary" && next(1)) { o.boundary = static_cast<core::f32>(std::atof(next(1))); ++i; }
        else if (a == "--blend" && next(1)) { o.blend = static_cast<core::f32>(std::atof(next(1))); ++i; }
        else if (a == "--step" && next(1)) { o.step = static_cast<core::f32>(std::atof(next(1))); ++i; }
        else if (a == "--threads" && next(1)) { o.threads = static_cast<core::u32>(std::atoi(next(1))); ++i; }
        else if (a == "--repeat" && next(1)) { o.repeat = static_cast<core::u32>(std::atoi(next(1))); ++i; }
        else if (a == "--minimap" && next(1)) { o.minimap = static_cast<core::u32>(std::atoi(next(1))); ++i; }
        else if (a == "--debug" && next(1)) { o.debug = next(1); ++i; }
        else if (a == "--ink" && next(1)) { o.ink = next(1); ++i; }
        else if (a == "--trace-from" && next(3)) { for (int k = 0; k < 3; ++k) o.traceFrom[k] = std::atoll(next(k + 1)); i += 3; }
        else if (a == "--surface-through") { o.surfaceThrough = true; }
        else if (a == "--segment" && next(1)) { o.segment = next(1); ++i; }
        else if (a == "--trace-export" && next(1)) { o.traceExport = next(1); ++i; }
        else if (a == "--segment-ink" && next(1)) { o.segmentInk = next(1); ++i; }
        else if (a == "--segment-ink-confidence" && next(1)) { o.segmentInkConfidence = static_cast<core::f32>(std::atof(next(1))); ++i; }
        else if (a == "--segment-scale" && next(1)) { o.segmentScale = static_cast<core::f32>(std::atof(next(1))); ++i; }
        else if (a == "--trace-floor" && next(1)) { o.traceFloor = static_cast<core::u8>(std::atoi(next(1))); ++i; }
        else if (a == "--trace-jump" && next(1)) { o.traceJump = static_cast<core::f32>(std::atof(next(1))); ++i; }
        else if (a == "--trace-radius" && next(1)) { o.traceRadius = std::atoi(next(1)); ++i; }
        else if (a == "--trace-relax" && next(1)) { o.traceRelax = static_cast<core::f32>(std::atof(next(1))); ++i; }
        else if (a == "--trace-relax-passes" && next(1)) { o.traceRelaxPasses = static_cast<core::u32>(std::atoi(next(1))); ++i; }
        else if (a == "--trace-smooth" && next(1)) { o.traceSmooth = std::atoi(next(1)); ++i; }
        else if (a == "--surface-opacity" && next(1)) { o.surfaceOpacity = static_cast<core::f32>(std::atof(next(1))); ++i; }
        else if (a == "--trace-size" && next(2)) { o.traceRows = static_cast<core::u32>(std::atoi(next(1)));
                                                   o.traceColumns = static_cast<core::u32>(std::atoi(next(2))); i += 2; }
        else if (a == "--ink-confidence" && next(1)) { o.inkConfidence = static_cast<core::f32>(std::atof(next(1))); ++i; }
        else
        {
            std::fprintf(stderr, "unknown argument '%s'\n\n", a.c_str());
            usage();
            return 2;
        }
    }

    // Checked here rather than where the overlay is built: refusing after minutes of downloading
    // is a refusal the operator pays for.
    if (!o.segmentInk.empty() && !(o.segmentInkConfidence > 0.0f))
    {
        std::fprintf(stderr, "--segment-ink needs --segment-ink-confidence: a prediction with no stated\n"
                             "worth would be painted as though it were the scan\n");
        return 2;
    }
    if (!o.ink.empty() && !(o.inkConfidence > 0.0f))
    {
        std::fprintf(stderr, "--ink needs --ink-confidence: a prediction with no stated worth would be\n"
                             "painted as though it were the scan\n");
        return 2;
    }

    const std::string prefix = o.bucket + "/" + o.volume;
    const std::string cacheRoot = o.cache + "/" + o.volume;
    scroll::HttpStore store(prefix.c_str(), cacheRoot.c_str());
    if (!store.valid())
    {
        std::fprintf(stderr, "no HTTP transport: this build has no libcurl\n");
        return 1;
    }

    // ── what the volume says about itself ─────────────────────────────────
    const std::size_t slash = o.volume.find_last_of('/');
    const std::string leaf = slash == std::string::npos ? o.volume : o.volume.substr(slash + 1);
    const scroll::VolumeName name = scroll::parseVolumeName(leaf.c_str());
    if (!name.parsed)
    {
        std::fprintf(stderr, "'%s' carries no resolution in its name, and the metadata does not hold one\n"
                             "either -- refusing rather than putting this scroll at somebody else's scale\n",
                     leaf.c_str());
        return 1;
    }

    std::string attrs;
    core::u32 levels = fetchText(store, ".zattrs", attrs)
                           ? zarr::countMultiscaleLevels(attrs.c_str(), attrs.size())
                           : 0u;
    if (levels == 0u)
        levels = 1u;
    if (o.coarsest >= levels)
        o.coarsest = levels - 1u;
    if (o.finest > o.coarsest)
        o.finest = o.coarsest;

    std::vector<zarr::ArrayMeta> meta(levels);
    for (core::u32 lv = 0u; lv < levels; ++lv)
    {
        char key[64];
        std::snprintf(key, sizeof(key), "%u/.zarray", lv);
        std::string doc;
        if (!fetchText(store, key, doc) || !zarr::parseArrayMeta(doc.c_str(), doc.size(), meta[lv]))
        {
            std::fprintf(stderr, "level %u will not open: %s\n", lv,
                         doc.empty() ? "no .zarray" : "unreadable or unsupported codec");
            return 1;
        }
    }

    const voxel::VolumeGeometry geometry = scroll::geometryOf(meta[0].shape, levels, name, o.corridor);
    if (!geometry.valid())
    {
        std::fprintf(stderr, "the volume's shape and name do not make a usable geometry\n");
        return 1;
    }

    std::printf("volume    %s\n", leaf.c_str());
    std::printf("  sample  %.3f um, staged at %.0f x -> %.4f m per sample\n",
                static_cast<double>(geometry.voxelMicrometres), static_cast<double>(geometry.metresPerMicrometre),
                static_cast<double>(geometry.metresPerSample()));
    std::printf("  extent  %lld x %lld x %lld samples = %.2f x %.2f x %.2f km walked\n",
                static_cast<long long>(geometry.samples[0]), static_cast<long long>(geometry.samples[1]),
                static_cast<long long>(geometry.samples[2]), static_cast<double>(geometry.extentMetres(0) / 1000.0f),
                static_cast<double>(geometry.extentMetres(1) / 1000.0f),
                static_cast<double>(geometry.extentMetres(2) / 1000.0f));
    std::printf("  pyramid  %u levels, codec %s\n", levels, zarr::codecName(meta[0].codec));

    core::i64 eye[3]{o.at[0], o.at[1], o.at[2]};
    for (core::u32 k = 0u; k < 3u; ++k)
    {
        if (eye[k] < 0)
            eye[k] = geometry.samples[k] / 2;
    }
    std::printf("  eye     level-0 sample (%lld, %lld, %lld)\n", static_cast<long long>(eye[0]),
                static_cast<long long>(eye[1]), static_cast<long long>(eye[2]));

    // ── residency ──────────────────────────────────────────────────────────
    voxel::ResidencyParams residency{};
    residency.finestLevel = o.finest;
    residency.coarsestLevel = o.coarsest;
    residency.ringRadius = o.radius;
    residency.budget = o.budget;

    // Loading is the streamer's job, not this file's: it is the same bookkeeping the interactive
    // window needs, and two copies of "which bricks should be in memory" would be two answers.
    scroll::VolumeStreamer streamer(store, geometry, meta);
    const double t0 = seconds();
    const scroll::StreamReport stream = streamer.update(residency, eye);
    const double tLoad = seconds() - t0;

    std::printf("  plan    %u bricks, levels %u..%u, radius %d\n", stream.wanted, o.finest, o.coarsest, o.radius);
    std::printf("  loaded  %u/%u in %.2f s  (%llu from cache, %llu fetched, %u all-fill, %u failed, %.1f MB)\n",
                stream.loaded, stream.wanted, tLoad, static_cast<unsigned long long>(store.hits()),
                static_cast<unsigned long long>(store.fetches()), stream.absent, stream.failed,
                static_cast<double>(stream.bytes) / 1e6);

    if (streamer.residentCount() == 0u)
    {
        std::fprintf(stderr, "nothing resident: an image now would be a picture of the background\n"
                             "pretending to be a scroll\n");
        return 1;
    }

    // ── the curve, measured from what is actually resident ─────────────────
    const voxel::DensityProfile profile = streamer.measureProfile(o.quantile, o.window);
    if (!profile.valid())
    {
        std::fprintf(stderr, "the resident bricks carry no measurable density\n");
        return 1;
    }
    std::printf("  density mean %.1f, deviation %.1f, window %u..%u\n", static_cast<double>(profile.mean),
                static_cast<double>(profile.deviation), profile.floorSample, profile.sheetSample);
    std::printf("  spread ");
    for (core::u32 lv = 0u; lv < geometry.levels && lv < voxel::kMaxPyramidLevels; ++lv)
        std::printf("L%u %.3f  ", lv, static_cast<double>(profile.spreadRatio[lv]));
    std::printf("\n");

    // A sheet at this scale is about `sheetMicrometres / voxelMicrometres` samples thick, and a
    // sheet you can see through is not a sheet. Deriving the peak from that beats picking one.
    const scroll::PapyrusMetrics metrics{};
    const core::f32 sheetSamples = metrics.sheetMicrometres / geometry.voxelMicrometres;
    const core::f32 peak = voxel::alphaForOpaqueAfter(sheetSamples, 0.85f);
    const voxel::TransferFunction transfer = voxel::rampTransfer(profile.floorSample, profile.sheetSample, peak);
    std::printf("  transfer sheet is %.1f samples thick -> peak opacity %.3f\n", static_cast<double>(sheetSamples),
                static_cast<double>(peak));

    // ── the overlay, if one was asked for ──────────────────────────────────
    // Held here so its bricks outlive the frame. Kept OUT of the render unless a confidence was
    // given: a prediction shown at full strength with no stated worth is the failure mode this
    // whole path exists to avoid.
    std::unique_ptr<scroll::HttpStore> inkStore;
    std::unique_ptr<scroll::VolumeStreamer> inkStreamer;
    std::vector<zarr::ArrayMeta> inkMeta;
    if (!o.ink.empty())
    {
        const std::string inkPrefix = o.bucket + "/" + o.ink;
        inkStore = std::make_unique<scroll::HttpStore>(inkPrefix.c_str(), (o.cache + "/" + o.ink).c_str());
        std::string inkAttrs;
        core::u32 inkLevels = fetchText(*inkStore, ".zattrs", inkAttrs)
                                  ? zarr::countMultiscaleLevels(inkAttrs.c_str(), inkAttrs.size()) : 1u;
        if (inkLevels == 0u)
            inkLevels = 1u;
        inkMeta.resize(inkLevels);
        bool ok = true;
        for (core::u32 lv = 0u; lv < inkLevels && ok; ++lv)
        {
            char key[64];
            std::snprintf(key, sizeof(key), "%u/.zarray", lv);
            std::string doc;
            ok = fetchText(*inkStore, key, doc) && zarr::parseArrayMeta(doc.c_str(), doc.size(), inkMeta[lv]);
        }
        if (!ok) { std::fprintf(stderr, "the prediction volume '%s' will not open\n", o.ink.c_str()); return 1; }
        inkStreamer = std::make_unique<scroll::VolumeStreamer>(*inkStore, geometry, inkMeta);
        voxel::ResidencyParams inkResidency = residency;
        inkResidency.finestLevel = o.finest < inkLevels ? o.finest : inkLevels - 1u;
        inkResidency.coarsestLevel = o.coarsest < inkLevels ? o.coarsest : inkLevels - 1u;
        const scroll::StreamReport ir = inkStreamer->update(inkResidency, eye);
        std::printf("  ink     %s — %u bricks, confidence %.2f\n", o.ink.c_str(), ir.loaded,
                    static_cast<double>(o.inkConfidence));
    }

    // ── the eye ────────────────────────────────────────────────────────────
    const core::f32 mps = geometry.metresPerSample();
    voxel::Eye camera{};
    camera.position = {static_cast<core::f32>(eye[2]) * mps, static_cast<core::f32>(eye[1]) * mps,
                       static_cast<core::f32>(eye[0]) * mps};

    // The camera is the engine's, not a second one: its angle wrapping is the fix for a bug this
    // project already shipped, where a cheap sine without range reduction froze past a hundred
    // degrees and a body kept walking the way it faced there.
    voxel::FreeCamera fly;
    fly.position = camera.position;
    fly.turn(o.yaw, o.pitch);
    camera = fly.eye();

    // ── the traced sheet, and anybody else's, if either was asked for ──────
    struct Layer final {
        std::vector<core::f32> depth;
        std::vector<core::f32> facing;
        std::vector<core::f32> u;
        std::vector<core::f32> v;
        core::f32 red{0.35f};
        core::f32 green{0.85f};
        core::f32 blue{1.00f};
        const core::u8 *ink{nullptr};
        core::u32 inkWidth{0};
        core::u32 inkHeight{0};
        core::f32 inkConfidence{0.0f};
    };
    std::vector<Layer> layers;

    // A shared rasterisation step, so the two surfaces land in the same projection. Deriving one
    // separately is how a comparison ends up measuring a difference in the camera.
    const auto addLayer = [&](const voxel::SurfaceMesh &mesh, core::f32 r, core::f32 g, core::f32 b,
                              const char *label) -> Layer & {
        Layer layer{};
        layer.red = r;
        layer.green = g;
        layer.blue = b;
        layer.depth.assign(static_cast<std::size_t>(o.width) * o.height, voxel::kNoSurface);
        layer.facing.assign(layer.depth.size(), 0.0f);
        // Texture coordinates only when the mesh carries a flattening: a traced surface has
        // geometry and no flattening, and asking for coordinates it does not have would write
        // zeroes that a prediction lookup would happily read.
        if (mesh.textured())
        {
            layer.u.assign(layer.depth.size(), 0.0f);
            layer.v.assign(layer.depth.size(), 0.0f);
        }
        const voxel::SurfaceDepth target{layer.depth.data(), layer.facing.data(),
                                         mesh.textured() ? layer.u.data() : nullptr,
                                         mesh.textured() ? layer.v.data() : nullptr, o.width, o.height};
        const core::u32 drawn = voxel::rasteriseSurface(mesh, geometry, camera, target);
        std::printf("  %-7s %u of %u triangles cover pixels from here\n", label, drawn, mesh.indexCount / 3u);
        layers.push_back(std::move(layer));
        return layers.back();
    };

    std::vector<lpl::math::Vec3<core::f32>> patchPoints;
    std::vector<core::u32> patchIndices;
    std::vector<lpl::math::Vec3<core::f32>> ourNormals;
    std::vector<lpl::math::Vec3<core::f32>> segmentNormals;
    voxel::SheetPatch patch{};
    voxel::SurfaceMesh ourMesh{};
    if (o.traceFrom[0] >= 0)
    {
        voxel::SheetTraceParams trace{};
        // ⚠ **The trace floor is NOT the render window's floor**, and using it was a real mistake:
        // the window isolates the brightest few per cent so the picture shows sheets against a
        // clear medium, while a walk has to stay on a ridge that is much broader than that. With
        // the render floor every row stopped on its first step -- reported honestly as short rows,
        // and completely useless. The mean is the honest line: below it, the walk has certainly
        // left the sheet.
        trace.floorSample = o.traceFloor != 0u ? o.traceFloor : static_cast<core::u8>(profile.mean);
        if (o.traceJump > 0.0f)
            trace.maximumRecentre = o.traceJump;
        trace.tensorRadius = o.traceRadius;
        if (o.traceSmooth >= 0)
            trace.ridgeSmoothing = o.traceSmooth;
        patchPoints.resize(static_cast<std::size_t>(o.traceRows) * o.traceColumns);
        const lpl::math::Vec3<core::f32> seed{static_cast<core::f32>(o.traceFrom[2]),
                                              static_cast<core::f32>(o.traceFrom[1]),
                                              static_cast<core::f32>(o.traceFrom[0])};
        patch = voxel::traceSheetPatch(streamer.mosaic(), seed, trace, o.traceRows, o.traceColumns,
                                       patchPoints.data());
        if (patch.rows == 0u)
        {
            // Refused rather than drawn empty: a seed with no sheet under it has no surface, and
            // showing a flat one at the seed would be the tool inventing the answer.
            std::fprintf(stderr, "no sheet passes through (%lld, %lld, %lld): the samples there carry no\n"
                                 "usable normal, so there is nothing to follow\n",
                         static_cast<long long>(o.traceFrom[0]), static_cast<long long>(o.traceFrom[1]),
                         static_cast<long long>(o.traceFrom[2]));
            return 1;
        }
        // Printed before and after, always: the number is what separates "the trace looks
        // crumpled" from "the sheet is crumpled", and only one of those is about the scroll.
        const core::f32 roughBefore = voxel::patchRoughness(patch);
        if (o.traceRelax > 0.0f)
        {
            // On-ridge: smooth AND still where the matter is. Plain relaxation would eventually
            // flatten the patch into its own average plane, which scores perfectly on roughness
            // and is no longer the sheet.
            voxel::relaxPatchOnRidge(streamer.mosaic(), patch, trace, o.traceRelax, o.traceRelaxPasses);
            std::printf("  relax   roughness %.4f -> %.4f samples (%.1f%% of a sample), %u passes at %.2f\n",
                        static_cast<double>(roughBefore), static_cast<double>(voxel::patchRoughness(patch)),
                        static_cast<double>(voxel::patchRoughness(patch) * 100.0f), o.traceRelaxPasses,
                        static_cast<double>(o.traceRelax));
        }
        else
        {
            std::printf("  rough   %.4f samples between a point and its neighbours' average\n",
                        static_cast<double>(roughBefore));
        }

        patchIndices.resize(static_cast<std::size_t>(patch.rows) * patch.columns * 6u);
        const core::u32 written =
            voxel::patchIndices(patch, patchIndices.data(), static_cast<core::u32>(patchIndices.size()));
        std::printf("  trace   %ux%u patch, %u triangles, %u short rows, %u refused jumps\n", patch.rows,
                    patch.columns, written / 3u, patch.shortRows, patch.refusedJumps);
        // A refusal is information, not a fault: it is the walk saying the sheet it was on stopped
        // being followable rather than quietly stepping onto the one beside it.
        // Why the walks ended, not just how many were short: those are four different problems.
        static const char *kWhy[5]{"budget", "left the matter", "left the bricks", "would have jumped",
                                   "no usable normal"};
        std::printf("          ended:");
        for (core::u32 i = 0u; i < 5u; ++i)
            if (patch.stops[i] != 0u)
                std::printf(" %u %s,", patch.stops[i], kWhy[i]);
        std::printf("\n");

        ourMesh.points = patch.points;
        ourMesh.indices = patchIndices.data();
        ourMesh.pointCount = patch.rows * patch.columns;
        ourMesh.indexCount = written;
        // Smooth shading, or the sheet reads as a heap of shards -- a fact about the shading, not
        // about the trace, and the first thing anybody mistakes for the geometry being wrong.
        ourNormals.resize(ourMesh.pointCount);
        voxel::computeVertexNormals(ourMesh, ourNormals.data());
        ourMesh.normals = ourNormals.data();
        (void) addLayer(ourMesh, 0.35f, 0.85f, 1.00f, "ours");

        if (!o.traceExport.empty())
        {
            // Level-0 sample coordinates and the corpus's own axis order, so what comes out can be
            // loaded straight back in -- which is also the round-trip that proves the reader and
            // the writer agree rather than merely both existing.
            std::FILE *obj = std::fopen(o.traceExport.c_str(), "wb");
            if (obj == nullptr)
            {
                std::fprintf(stderr, "cannot write %s\n", o.traceExport.c_str());
                return 1;
            }
            std::fprintf(obj, "# traced by lpl-scrollwalk from %s\n", leaf.c_str());
            std::fprintf(obj, "# seed %lld %lld %lld, %ux%u patch, jump limit %.2f, %u refused\n",
                         static_cast<long long>(o.traceFrom[0]), static_cast<long long>(o.traceFrom[1]),
                         static_cast<long long>(o.traceFrom[2]), patch.rows, patch.columns,
                         static_cast<double>(trace.maximumRecentre), patch.refusedJumps);
            for (core::u32 v = 0u; v < ourMesh.pointCount; ++v)
                std::fprintf(obj, "v %.4f %.4f %.4f\n", static_cast<double>(ourMesh.points[v].x),
                             static_cast<double>(ourMesh.points[v].y), static_cast<double>(ourMesh.points[v].z));
            // The patch IS its own flattening: a grid traced along two in-plane directions, so its
            // row and column are already the coordinates a prediction would be painted in. Writing
            // them makes the export a surface somebody can put a map on, not just a shape.
            for (core::u32 r = 0u; r < patch.rows; ++r)
                for (core::u32 col = 0u; col < patch.columns; ++col)
                    std::fprintf(obj, "vt %.6f %.6f\n",
                                 static_cast<double>(col) / static_cast<double>(patch.columns - 1u),
                                 static_cast<double>(r) / static_cast<double>(patch.rows - 1u));
            for (core::u32 t = 0u; t + 2u < ourMesh.indexCount; t += 3u)
                std::fprintf(obj, "f %u/%u %u/%u %u/%u\n", ourMesh.indices[t] + 1u, ourMesh.indices[t] + 1u,
                             ourMesh.indices[t + 1u] + 1u, ourMesh.indices[t + 1u] + 1u,
                             ourMesh.indices[t + 2u] + 1u, ourMesh.indices[t + 2u] + 1u);
            std::fclose(obj);
            std::printf("  export  %s (%u vertices, %u triangles)\n", o.traceExport.c_str(), ourMesh.pointCount,
                        ourMesh.indexCount / 3u);
        }
    }

    std::vector<lpl::math::Vec3<core::f32>> segmentPoints;
    std::vector<core::u32> segmentIndices;
    std::vector<core::f32> segmentTexture;
    std::vector<core::u32> segmentTextureIndices;
    std::vector<core::u8> inkSamples;
    scroll::GreyImage inkImage{};
    if (!o.segment.empty())
    {
        segmentPoints.resize(1u << 20);
        segmentIndices.resize(1u << 22);
        segmentTexture.resize(1u << 21);
        segmentTextureIndices.resize(segmentIndices.size());
        const scroll::SegmentLoad load = scroll::loadSegmentObj(
            o.segment.c_str(), segmentPoints.data(), static_cast<core::u32>(segmentPoints.size()),
            segmentIndices.data(), static_cast<core::u32>(segmentIndices.size()), o.segmentScale,
            segmentTexture.data(), static_cast<core::u32>(segmentTexture.size() / 2u),
            segmentTextureIndices.data());
        if (!load.opened)
        {
            std::fprintf(stderr, "cannot open segment '%s'\n", o.segment.c_str());
            return 1;
        }
        std::printf("  segment %u vertices, %u triangles, %u texture coords (%u quads split, %u dropped)\n",
                    load.vertices, load.triangles, load.textures, load.quads, load.skippedFaces);
        voxel::SurfaceMesh theirs{};
        theirs.points = segmentPoints.data();
        theirs.indices = segmentIndices.data();
        theirs.pointCount = load.vertices;
        theirs.indexCount = load.triangles * 3u;
        if (load.textures != 0u)
        {
            theirs.texture = segmentTexture.data();
            theirs.textureIndices = segmentTextureIndices.data();
            theirs.textureCount = load.textures;
        }

        if (!o.segmentInk.empty())
        {
            if (load.textures == 0u)
            {
                // Refused rather than stretched over the mesh: without the segment's own
                // flattening there is no registration, and inventing one would put a prediction
                // in a place nobody claimed it belonged.
                std::fprintf(stderr, "'%s' carries no texture coordinates, so a prediction cannot be placed\n"
                                     "on it -- the flattening IS the registration\n", o.segment.c_str());
                return 1;
            }
            inkSamples.resize(1u << 26);
            inkImage.samples = inkSamples.data();
            if (!scroll::loadGreyImage(o.segmentInk.c_str(), inkImage, static_cast<core::u32>(inkSamples.size())))
            {
                std::fprintf(stderr, "cannot read '%s' as 8-bit binary PGM or PPM.\n"
                                     "Convert it once:  python -c \"from PIL import Image;"
                                     " Image.open('in.png').convert('L').save('out.pgm')\"\n",
                             o.segmentInk.c_str());
                return 1;
            }
            std::printf("  ink     %s, %ux%u, confidence %.2f\n", o.segmentInk.c_str(), inkImage.width,
                        inkImage.height, static_cast<double>(o.segmentInkConfidence));
        }

        segmentNormals.resize(theirs.pointCount);
        voxel::computeVertexNormals(theirs, segmentNormals.data());
        theirs.normals = segmentNormals.data();
        Layer &their = addLayer(theirs, 1.00f, 0.72f, 0.30f, "theirs");
        if (inkImage.valid())
        {
            their.ink = inkImage.samples;
            their.inkWidth = inkImage.width;
            their.inkHeight = inkImage.height;
            their.inkConfidence = o.segmentInkConfidence;
        }

        if (patch.rows != 0u)
        {
            // The measurement, in the units the scan is in. Point-to-triangle, so two surfaces
            // meshed at different densities are not reported as disagreeing about the sheet.
            const scroll::SurfaceAgreement agree = scroll::compareSurfaces(
                patch.points, patch.rows * patch.columns, theirs, 40.0f);
            const core::f32 um = geometry.voxelMicrometres;
            std::printf("  agree   %u of %u points compared, %u had nothing within reach\n", agree.compared,
                        patch.rows * patch.columns, agree.unmatched);
            std::printf("          median %.2f samples (%.1f um), mean %.2f, worst %.2f (%.1f um)\n",
                        static_cast<double>(agree.medianSamples), static_cast<double>(agree.medianSamples * um),
                        static_cast<double>(agree.meanSamples), static_cast<double>(agree.worstSamples),
                        static_cast<double>(agree.worstSamples * um));
            // ⚠ The median is the number to read. Two traces of the same sheet agree almost
            // everywhere and disagree wildly where one of them left it; a mean folds those few
            // points in and reports a disagreement that exists nowhere.
        }
    }

    voxel::MarchParams march{};
    march.stepSamples = o.step;
    march.shading = o.shading;
    march.boundaryOpacity = o.boundary;
    march.levelBlendSamples = o.blend;
    voxel::SurfaceTexture textures[voxel::kMaxSurfaceLayers]{};
    for (const Layer &layer : layers)
    {
        if (march.surfaceCount >= voxel::kMaxSurfaceLayers)
            break;
        voxel::SurfaceLayer &slot = march.surfaces[march.surfaceCount++];
        slot.depth = layer.depth.data();
        slot.facing = layer.facing.data();
        slot.red = layer.red;
        slot.green = layer.green;
        slot.blue = layer.blue;
        slot.opacity = o.surfaceOpacity;
        slot.throughMatter = o.surfaceThrough;
        slot.ink = layer.ink;
        slot.inkWidth = layer.inkWidth;
        slot.inkHeight = layer.inkHeight;
        slot.inkConfidence = layer.inkConfidence;
        textures[march.surfaceCount - 1u].u = layer.u.empty() ? nullptr : layer.u.data();
        textures[march.surfaceCount - 1u].v = layer.v.empty() ? nullptr : layer.v.data();
    }
    march.surfaceTexture = textures;
    if (inkStreamer)
    {
        march.overlay = &inkStreamer->mosaic();
        march.overlayConfidence = o.inkConfidence;
    }
    if (o.debug == "level") march.debug = voxel::DebugView::Level;
    else if (o.debug == "gradient") march.debug = voxel::DebugView::GradientMagnitude;
    else if (o.debug == "shade") march.debug = voxel::DebugView::Shade;
    else if (o.debug == "normal") march.debug = voxel::DebugView::Normal;
    else if (o.debug == "steps") march.debug = voxel::DebugView::StepCount;
    else if (!o.debug.empty()) { std::fprintf(stderr, "unknown --debug view '%s'\n", o.debug.c_str()); return 2; }
    march.maxDistanceMetres = geometry.extentMetres(0);

    std::vector<core::u32> frame(static_cast<std::size_t>(o.width) * o.height, 0u);
    voxel::MarchReport report{};
    double tMarch = 1.0e30;
    for (core::u32 pass = 0u; pass < (o.repeat == 0u ? 1u : o.repeat); ++pass)
    {
        const double t1 = seconds();
        if (o.threads <= 1u)
        {
            report = voxel::march(streamer.mosaic(), geometry, profile, transfer, camera, march, frame.data(),
                                  o.width, o.height, 0u, o.height);
        }
        else
        {
            // ⚠ **Interleaved rows, not contiguous slabs.** A frame's cost is wildly uneven top to
            // bottom: a ray that leaves the volume immediately costs nothing and one down the
            // length of a sheet costs everything. Contiguous bands leave most threads idle waiting
            // on the one that got the expensive half; every thread taking every Nth row gives each
            // of them the same mix.
            std::vector<std::thread> pool;
            std::vector<voxel::MarchReport> reports(o.threads);
            for (core::u32 t = 0u; t < o.threads; ++t)
            {
                pool.emplace_back([&, t]() {
                    for (core::u32 row = t; row < o.height; row += o.threads)
                    {
                        const voxel::MarchReport r = voxel::march(streamer.mosaic(), geometry, profile, transfer,
                                                                  camera, march, frame.data(), o.width, o.height,
                                                                  row, 1u);
                        reports[t].rays += r.rays;
                        reports[t].steps += r.steps;
                        reports[t].saturated += r.saturated;
                        reports[t].escaped += r.escaped;
                        reports[t].skippedBricks += r.skippedBricks;
                        reports[t].missingBricks += r.missingBricks;
                        reports[t].gradients += r.gradients;
                        reports[t].overlaid += r.overlaid;
                        reports[t].surfaceHits += r.surfaceHits;
                        reports[t].inkPainted += r.inkPainted;
                    }
                });
            }
            for (std::thread &t : pool)
                t.join();
            report = voxel::MarchReport{};
            for (const voxel::MarchReport &r : reports)
            {
                report.rays += r.rays;
                report.steps += r.steps;
                report.saturated += r.saturated;
                report.escaped += r.escaped;
                report.skippedBricks += r.skippedBricks;
                report.missingBricks += r.missingBricks;
                report.gradients += r.gradients;
                report.overlaid += r.overlaid;
                report.surfaceHits += r.surfaceHits;
                report.inkPainted += r.inkPainted;
            }
        }
        const double elapsed = seconds() - t1;
        if (elapsed < tMarch)
            tMarch = elapsed;
    }

    std::printf("  march   %llu rays, %llu samples in %.2f s (%.1f Msample/s)\n",
                static_cast<unsigned long long>(report.rays), static_cast<unsigned long long>(report.steps), tMarch,
                static_cast<double>(report.steps) / (tMarch > 0.0 ? tMarch : 1.0) / 1e6);
    // These are what make the image believable. A camera that never entered the volume produces a
    // perfectly stable picture, so the counts have to be printed next to it.
    std::printf("  rays    %llu saturated, %llu escaped | bricks %llu skipped empty, %llu cells skipped, %llu missing\n",
                static_cast<unsigned long long>(report.saturated), static_cast<unsigned long long>(report.escaped),
                static_cast<unsigned long long>(report.skippedBricks),
                static_cast<unsigned long long>(report.skippedCells),
                static_cast<unsigned long long>(report.missingBricks));
    if (!layers.empty())
    {
        std::printf("  surface %llu rays crossed a traced sheet, across %zu layer(s)\n",
                    static_cast<unsigned long long>(report.surfaceHits), layers.size());
        // Printed even at zero, and especially at zero: a prediction that painted nothing looks
        // exactly like one that was never asked for.
        if (inkImage.valid())
            std::printf("  painted %llu pixels carry the prediction\n",
                        static_cast<unsigned long long>(report.inkPainted));
    }
    if (inkStreamer)
        std::printf("  overlay %llu samples tinted at confidence %.2f\n",
                    static_cast<unsigned long long>(report.overlaid), static_cast<double>(o.inkConfidence));
    std::printf("  frame   signature 0x%08X\n", voxel::foldFrame(frame.data(), static_cast<core::u32>(frame.size())));

    if (o.minimap > 0u)
    {
        // The atlas is the coarsest level of the WHOLE subject, not the bricks the walk uses:
        // those cover the few metres already on screen, which is the one thing a lost person does
        // not need.
        scroll::VolumeStreamer atlas(store, geometry, meta);
        voxel::ResidencyParams whole{};
        whole.finestLevel = levels - 1u;
        whole.coarsestLevel = levels - 1u;
        core::i32 reach = 1;
        for (core::u32 axis = 0u; axis < 3u; ++axis)
            reach = reach > geometry.bricksAtLevel(axis, levels - 1u) ? reach : geometry.bricksAtLevel(axis, levels - 1u);
        whole.ringRadius = reach;
        whole.budget = voxel::kMaxResidentBricks;
        const core::i64 middle[3]{geometry.samples[0] / 2, geometry.samples[1] / 2, geometry.samples[2] / 2};
        const scroll::StreamReport atlasReport = atlas.update(whole, middle);
        std::printf("  atlas   level %u: %u bricks, %u all-fill, %.1f MB\n", levels - 1u, atlasReport.loaded,
                    atlasReport.absent, static_cast<double>(atlasReport.bytes) / 1e6);

        if (atlas.residentCount() == 0u)
        {
            std::printf("          (nothing resident at that level -- no minimap drawn)\n");
        }
        else
        {
            std::vector<core::u8> sliceSamples(192u * 192u, 0u);
            voxel::VolumeSlice slice{};
            slice.samples = sliceSamples.data();
            slice.width = 192u;
            slice.height = 192u;
            slice.axis = voxel::SliceAxis::Z;
            slice.at = eye[0];
            // Two panels, because they answer two different questions: the cross-section says
            // which turn of the spiral you are in, and the long view says how far along the scroll
            // -- and neither can be read off the other.
            const core::u32 panel = o.minimap < o.width ? o.minimap : o.width;
            core::u32 hits = 0u;

            voxel::MinimapStyle across{};
            across.width = panel;
            across.height = panel;
            across.left = o.width - panel;
            across.top = 0u;
            hits += voxel::extractSlice(atlas.mosaic(), geometry, slice);
            voxel::drawMinimap(frame.data(), o.width, o.height, across, slice, geometry, camera);

            // The long view is wide and short: a scroll is far longer than it is thick, and a
            // square panel of it would be mostly empty frame.
            std::vector<core::u8> longSamples(256u * 96u, 0u);
            voxel::VolumeSlice along{};
            along.samples = longSamples.data();
            along.width = 256u;
            along.height = 96u;
            along.axis = voxel::SliceAxis::Y;
            along.at = eye[1];
            hits += voxel::extractSlice(atlas.mosaic(), geometry, along);

            voxel::MinimapStyle lengthwise{};
            lengthwise.width = panel;
            lengthwise.height = panel / 3u > 24u ? panel / 3u : 24u;
            lengthwise.left = o.width - panel;
            lengthwise.top = across.height + 6u;
            if (lengthwise.top + lengthwise.height <= o.height)
                voxel::drawMinimap(frame.data(), o.width, o.height, lengthwise, along, geometry, camera);

            std::printf("  minimap %ux%u across + %ux%u along, %u slice samples found the subject\n", across.width,
                        across.height, lengthwise.width, lengthwise.height, hits);
        }
    }

    std::FILE *f = std::fopen(o.out.c_str(), "wb");
    if (f == nullptr)
    {
        std::fprintf(stderr, "cannot write %s\n", o.out.c_str());
        return 1;
    }
    std::fprintf(f, "P6\n%u %u\n255\n", o.width, o.height);
    for (core::u32 p : frame)
    {
        const unsigned char rgb[3]{static_cast<unsigned char>((p >> 16) & 0xFFu),
                                   static_cast<unsigned char>((p >> 8) & 0xFFu),
                                   static_cast<unsigned char>(p & 0xFFu)};
        std::fwrite(rgb, 1, 3, f);
    }
    std::fclose(f);
    std::printf("  wrote   %s\n", o.out.c_str());
    return 0;
}
