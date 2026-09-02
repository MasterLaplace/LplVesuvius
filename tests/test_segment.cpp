/**
 * @file test_segment.cpp
 * @brief Reading somebody else's surface, and measuring how far ours sits from it.
 *
 * @author MasterLaplace
 * @version 0.1.0
 * @copyright MIT License
 */

#include <lpl/scroll/Segment.hpp>

#include <cstdio>
#include <string>
#include <unistd.h>
#include <vector>

namespace {

int gChecks = 0;
int gFailures = 0;

void check(bool ok, const char *what)
{
    ++gChecks;
    if (!ok)
    {
        ++gFailures;
        std::printf("  FAIL  %s\n", what);
    }
}

void checkEq(long long got, long long want, const char *what)
{
    ++gChecks;
    if (got != want)
    {
        ++gFailures;
        std::printf("  FAIL  %s: got %lld, want %lld\n", what, got, want);
    }
}

using namespace lpl;
using Point = math::Vec3<core::f32>;

std::string writeTemp(const char *name, const char *body)
{
    char path[256];
    std::snprintf(path, sizeof(path), "/tmp/lpl-seg-%d-%s.obj", static_cast<int>(::getpid()), name);
    std::FILE *f = std::fopen(path, "wb");
    if (f != nullptr)
    {
        std::fputs(body, f);
        std::fclose(f);
    }
    return std::string(path);
}

} // namespace

int main()
{
    std::printf("segment\n");

    // A flat quad at x = 10, plus the shapes a real writer emits: comments, a quad face, index
    // forms with texture and normal slots, and a negative (relative) index.
    const std::string path = writeTemp("plain", "# a segment\n"
                                                "v 10.0 0.0 0.0\n"
                                                "v 10.0 8.0 0.0\n"
                                                "v 10.0 8.0 8.0\n"
                                                "v 10.0 0.0 8.0\n"
                                                "vn 1 0 0\n"
                                                "vt 0 0\n"
                                                "f 1/1/1 2/1/1 3/1/1 4/1/1\n"
                                                "f -4 -3 -2\n");
    std::vector<Point> points(64);
    std::vector<core::u32> indices(256);
    scroll::SegmentLoad load = scroll::loadSegmentObj(path.c_str(), points.data(), static_cast<core::u32>(points.size()),
                                                      indices.data(), static_cast<core::u32>(indices.size()), 1.0f);
    check(load.opened, "the file opens");
    checkEq(load.vertices, 4, "four vertices");
    // The quad becomes two triangles and the explicit face is a third: normals and texture slots
    // are skipped rather than read, because a normal the file asserts would be a second answer to
    // which way the sheet faces.
    checkEq(load.triangles, 3, "a quad splits in two, plus the triangle");
    checkEq(load.quads, 1, "and the quad is counted as one");
    checkEq(load.skippedFaces, 0, "nothing is dropped");
    check(points[0].x == 10.0f && points[2].z == 8.0f, "the vertices come through in the order written");

    // A face naming a vertex that does not exist is dropped and counted, not clamped: clamping
    // staples a triangle across the whole mesh, and it renders.
    const std::string bad = writeTemp("bad", "v 0 0 0\nv 1 0 0\nv 0 1 0\nf 1 2 99\nf 1 2 3\n");
    load = scroll::loadSegmentObj(bad.c_str(), points.data(), static_cast<core::u32>(points.size()), indices.data(),
                                  static_cast<core::u32>(indices.size()), 1.0f);
    checkEq(load.triangles, 1, "only the valid face survives");
    checkEq(load.skippedFaces, 1, "and the other is counted");

    check(!scroll::loadSegmentObj("/nonexistent/segment.obj", points.data(), 64u, indices.data(), 256u, 1.0f).opened,
          "a missing file says so rather than returning an empty surface");

    // Scale is a parameter because nothing in the file says which resolution it was written for.
    load = scroll::loadSegmentObj(path.c_str(), points.data(), static_cast<core::u32>(points.size()), indices.data(),
                                  static_cast<core::u32>(indices.size()), 2.0f);
    check(points[0].x == 20.0f, "the scale is applied to every vertex");

    // ── the comparison ─────────────────────────────────────────────────────
    {
        // A plane at x = 10, meshed coarsely.
        std::vector<Point> plane{{10.0f, 0.0f, 0.0f}, {10.0f, 20.0f, 0.0f}, {10.0f, 20.0f, 20.0f},
                                 {10.0f, 0.0f, 20.0f}};
        std::vector<core::u32> planeIndices{0u, 1u, 2u, 0u, 2u, 3u};
        voxel::SurfaceMesh mesh{plane.data(), planeIndices.data(), 4u, 6u};

        // Points on the same plane but nowhere near its vertices: a vertex-to-vertex distance
        // would report a disagreement that is entirely an artefact of how each side was meshed.
        std::vector<Point> ours;
        for (int i = 1; i < 10; ++i)
            for (int j = 1; j < 10; ++j)
                ours.push_back(Point{10.0f, static_cast<core::f32>(i), static_cast<core::f32>(j)});
        scroll::SurfaceAgreement agree =
            scroll::compareSurfaces(ours.data(), static_cast<core::u32>(ours.size()), mesh, 5.0f);
        std::printf("  same plane, different tessellation: %u compared, median %.4f, worst %.4f\n", agree.compared,
                    static_cast<double>(agree.medianSamples), static_cast<double>(agree.worstSamples));
        checkEq(agree.compared, static_cast<long long>(ours.size()), "every point finds the surface");
        check(agree.medianSamples < 1e-3f, "and sits on it, whatever the tessellation");

        // Offset by three samples: the measurement must say three.
        for (Point &p : ours)
            p.x = 13.0f;
        agree = scroll::compareSurfaces(ours.data(), static_cast<core::u32>(ours.size()), mesh, 5.0f);
        std::printf("  offset by 3: median %.4f, worst %.4f\n", static_cast<double>(agree.medianSamples),
                    static_cast<double>(agree.worstSamples));
        check(agree.medianSamples > 2.9f && agree.medianSamples < 3.1f, "an offset of three reads as three");

        // Beyond the search radius: unmatched, NOT "disagrees a lot". Folding the two together is
        // how a comparison of two partly-overlapping surfaces comes out meaningless.
        for (Point &p : ours)
            p.x = 40.0f;
        agree = scroll::compareSurfaces(ours.data(), static_cast<core::u32>(ours.size()), mesh, 5.0f);
        checkEq(agree.compared, 0, "nothing within reach is compared");
        checkEq(agree.unmatched, static_cast<long long>(ours.size()), "and all of it is reported unmatched");

        // A surface that overlaps only partly: the median must describe the overlap, not be
        // dragged by the part that has nothing to meet.
        ours.clear();
        for (int j = 1; j < 10; ++j)
            ours.push_back(Point{10.2f, 5.0f, static_cast<core::f32>(j)}); // On the plane.
        for (int j = 1; j < 10; ++j)
            ours.push_back(Point{10.2f, 5.0f, static_cast<core::f32>(200 + j)}); // Far off the end.
        agree = scroll::compareSurfaces(ours.data(), static_cast<core::u32>(ours.size()), mesh, 5.0f);
        std::printf("  half overlapping: %u compared, %u unmatched, median %.4f\n", agree.compared, agree.unmatched,
                    static_cast<double>(agree.medianSamples));
        checkEq(agree.compared, 9, "the overlapping half is measured");
        checkEq(agree.unmatched, 9, "and the other half is reported as having nothing to meet");
        check(agree.medianSamples < 0.3f, "the median describes the overlap, not the gap");
    }

    // ── texture coordinates, which are the registration a prediction needs ──
    {
        // A quad with a flattening, and a SEAM: vertex 2 carries two different coordinates
        // depending on which side of the cut the face is on. Indexing by vertex would silently
        // pick one and smear whatever is painted from the texture across the cut.
        const std::string seam = writeTemp("seam", "v 0 0 0\nv 0 1 0\nv 0 1 1\nv 0 0 1\n"
                                                   "vt 0.0 0.0\nvt 0.0 1.0\nvt 1.0 1.0\nvt 1.0 0.0\n"
                                                   "vt 0.5 1.0\n"
                                                   "f 1/1 2/2 3/3\n"
                                                   "f 1/1 3/5 4/4\n");
        std::vector<core::f32> uv(64);
        std::vector<core::u32> uvIndices(256);
        scroll::SegmentLoad t = scroll::loadSegmentObj(seam.c_str(), points.data(), 64u, indices.data(), 256u, 1.0f,
                                                       uv.data(), 32u, uvIndices.data());
        checkEq(t.textures, 5, "five texture coordinates for four vertices: that is the seam");
        checkEq(t.triangles, 2, "two triangles");
        // Vertex 3 (index 2) appears in both faces with DIFFERENT texture indices.
        checkEq(uvIndices[2], 2, "the first face uses coordinate 3 for that corner");
        checkEq(uvIndices[4], 4, "and the second uses coordinate 5 for the same vertex");
        check(uv[4] == 1.0f && uv[5] == 1.0f, "the coordinates come through in order");

        // "v//n" carries no texture coordinate, and must not be read as one.
        const std::string noUv = writeTemp("nouv", "v 0 0 0\nv 1 0 0\nv 0 1 0\nvt 0.25 0.75\n"
                                                   "f 1//1 2//1 3//1\n");
        t = scroll::loadSegmentObj(noUv.c_str(), points.data(), 64u, indices.data(), 256u, 1.0f, uv.data(), 32u,
                                   uvIndices.data());
        checkEq(t.triangles, 1, "the face still loads");
        checkEq(uvIndices[0], 0, "and a corner with no coordinate falls back rather than reading the normal");
    }

    // ── the prediction image ───────────────────────────────────────────────
    {
        char path[256];
        std::snprintf(path, sizeof(path), "/tmp/lpl-seg-%d.pgm", static_cast<int>(::getpid()));
        std::FILE *f = std::fopen(path, "wb");
        // A comment between header tokens: half the tools that write these put one there, and a
        // reader that only skips comments after the magic breaks on the other half.
        std::fputs("P5\n# written by a tool that comments\n4 2\n255\n", f);
        const unsigned char body[8]{0u, 40u, 80u, 120u, 160u, 200u, 240u, 255u};
        std::fwrite(body, 1, 8, f);
        std::fclose(f);

        std::vector<core::u8> buffer(64);
        scroll::GreyImage image{buffer.data(), 0u, 0u};
        check(scroll::loadGreyImage(path, image, 64u), "a commented PGM reads");
        checkEq(image.width, 4, "width");
        checkEq(image.height, 2, "height");
        check(image.samples[0] == 0u && image.samples[7] == 255u, "and the samples come through");

        // Sixteen-bit is refused rather than halved: reading it as eight would make a prediction
        // come out uniformly faint instead of visibly wrong.
        std::snprintf(path, sizeof(path), "/tmp/lpl-seg16-%d.pgm", static_cast<int>(::getpid()));
        f = std::fopen(path, "wb");
        std::fputs("P5\n2 2\n65535\n", f);
        std::fclose(f);
        check(!scroll::loadGreyImage(path, image, 64u), "a sixteen-bit PGM is refused, not halved");

        std::vector<core::u8> tiny(2);
        scroll::GreyImage small{tiny.data(), 0u, 0u};
        std::snprintf(path, sizeof(path), "/tmp/lpl-seg-%d.pgm", static_cast<int>(::getpid()));
        check(!scroll::loadGreyImage(path, small, 2u), "a buffer that does not fit is refused");
    }

    std::printf("%s (%d failures, %d checks)\n", gFailures == 0 ? "ALL PASS" : "FAILURES", gFailures, gChecks);
    return gFailures == 0 ? 0 : 1;
}
