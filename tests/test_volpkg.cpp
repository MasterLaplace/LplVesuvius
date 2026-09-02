/**
 * @file test_volpkg.cpp
 * @brief Reading a resolution out of a corpus filename, and staging a scale from it.
 *
 * @author MasterLaplace
 * @version 0.1.0
 * @copyright MIT License
 */

#include <lpl/scroll/Volpkg.hpp>

#include <cstdio>

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
bool near(float a, float b, float tol) { return (a > b ? a - b : b - a) <= tol; }
} // namespace

int main()
{
    using namespace lpl;
    std::printf("volpkg\n");

    // Real directory names from the open bucket.
    {
        const scroll::VolumeName v = scroll::parseVolumeName("20241024131838-7.910um-53keV-masked.zarr");
        check(v.parsed, "a real volume name parses");
        check(near(v.micrometres, 7.910f, 0.001f), "the resolution comes out of the name");
        check(near(v.kiloElectronVolts, 53.0f, 0.01f), "so does the beam energy");
        check(v.masked, "and the mask flag");
    }
    {
        const scroll::VolumeName v = scroll::parseVolumeName("20230205180739-3.24um-88keV.zarr");
        check(v.parsed, "a fragment volume parses too");
        check(near(v.micrometres, 3.24f, 0.001f), "at its own, finer resolution");
        check(!v.masked, "and it is not masked");
    }
    {
        // Defaulting here would put an unknown scroll at somebody else's scale, and nothing
        // downstream could tell: the geometry would be wrong by a constant and look fine.
        const scroll::VolumeName v = scroll::parseVolumeName("volume.zarr");
        check(!v.parsed, "a name with no resolution is refused rather than defaulted");
        const core::i64 shape[3]{100, 100, 100};
        check(!scroll::geometryOf(shape, 3u, v, 3.0f).valid(), "and yields no geometry at all");
    }

    // The staging scale. Three metres of corridor between two sheets is the readable choice; the
    // arithmetic that gets there has to be right or the whole subject is the wrong size.
    {
        const scroll::PapyrusMetrics m{};
        check(near(m.gapMicrometres(), 260.0f, 0.01f), "the air gap is the pitch less the sheet");
        const float scale = m.metresPerMicrometre(3.0f);
        check(near(scale, 11538.0f, 2.0f), "and the scale that puts it at three metres is about 11538");

        const core::i64 shape[3]{21000, 6700, 9100};
        const scroll::VolumeName name = scroll::parseVolumeName("20241024131838-7.910um-53keV-masked.zarr");
        const voxel::VolumeGeometry g = scroll::geometryOf(shape, 6u, name, 3.0f);
        check(g.valid(), "a geometry comes out usable");
        check(near(g.metresPerSample(), 0.0913f, 0.001f), "one sample is about nine centimetres");
        // 21000 samples of 9.13 cm: the roll stands one and nine tenths of a kilometre tall.
        check(near(g.extentMetres(0) / 1000.0f, 1.917f, 0.01f), "and the roll is 1.9 km along its axis");
        check(g.bricksAtLevel(0, 0) == (21000 + 127) / 128, "brick counts round up the way zarr does");
        check(g.samplesAtLevel(0, 5) == (21000 + 31) / 32, "and so do level extents");
    }

    std::printf("%s (%d failures, %d checks)\n", gFailures == 0 ? "ALL PASS" : "FAILURES", gFailures, gChecks);
    return gFailures == 0 ? 0 : 1;
}
