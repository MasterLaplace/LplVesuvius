/**
 * @file test_streamer.cpp
 * @brief Keeping the right bricks in memory while the eye moves, against a store made of arithmetic.
 *
 * @warning **No network.** A check that needs the bucket goes red when the bucket does. The store
 * here answers from a formula, so every brick is reproducible and the one thing being measured is
 * the streamer's bookkeeping.
 *
 * @author MasterLaplace
 * @version 0.1.0
 * @copyright MIT License
 */

#include <lpl/scroll/Streamer.hpp>

#include <cstdio>
#include <cstring>

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

/// A store that synthesises a brick from its own key, and can be told to withhold one.
class FormulaStore final : public zarr::IZarrStore {
public:
    core::u64 reads{0};
    char withhold[64]{};

    [[nodiscard]] zarr::FetchResult read(const char *key, core::u8 *buffer, core::usize capacity) noexcept override
    {
        ++reads;
        if (withhold[0] != '\0' && std::strcmp(key, withhold) == 0)
            return zarr::FetchResult{zarr::FetchStatus::Absent, 0u};
        if (capacity < voxel::kBrickVoxels)
            return zarr::FetchResult{zarr::FetchStatus::TooLarge, voxel::kBrickVoxels};

        // A value that depends on the key, so a brick served for the wrong key is detectable.
        core::u32 seed = 2166136261u;
        for (const char *p = key; *p != '\0'; ++p)
        {
            seed ^= static_cast<core::u8>(*p);
            seed *= 16777619u;
        }
        for (core::u32 i = 0u; i < voxel::kBrickVoxels; ++i)
            buffer[i] = static_cast<core::u8>(120u + ((seed + i) % 80u));
        return zarr::FetchResult{zarr::FetchStatus::Ok, voxel::kBrickVoxels};
    }

    [[nodiscard]] const char *name() const noexcept override { return "FormulaStore"; }
};

zarr::ArrayMeta metaFor(core::u32 level)
{
    zarr::ArrayMeta m{};
    m.dimensions = 3u;
    m.itemSize = 1u;
    m.codec = zarr::Codec::Raw;
    m.separator = '/';
    m.cOrder = true;
    for (core::u32 d = 0u; d < 3u; ++d)
    {
        m.shape[d] = 4096 >> level;
        m.chunks[d] = voxel::kBrickEdge;
    }
    return m;
}

} // namespace

int main()
{
    std::printf("volume streamer\n");

    voxel::VolumeGeometry geometry{};
    geometry.samples[0] = 4096;
    geometry.samples[1] = 4096;
    geometry.samples[2] = 4096;
    geometry.levels = 4u;
    geometry.voxelMicrometres = 7.91f;
    geometry.metresPerMicrometre = 11538.0f;

    std::vector<zarr::ArrayMeta> meta;
    for (core::u32 lv = 0u; lv < geometry.levels; ++lv)
        meta.push_back(metaFor(lv));

    FormulaStore store;
    scroll::VolumeStreamer streamer(store, geometry, meta);

    voxel::ResidencyParams params{};
    params.finestLevel = 0u;
    params.coarsestLevel = 3u;
    params.ringRadius = 1;
    params.budget = 128u;

    core::i64 eye[3]{2048, 2048, 2048};

    const scroll::StreamReport first = streamer.update(params, eye);
    std::printf("  first pass: %u wanted, %u loaded, %u kept, %.1f MB\n", first.wanted, first.loaded, first.kept,
                static_cast<double>(first.bytes) / 1e6);
    check(first.wanted > 0u, "a plan is produced");
    checkEq(first.loaded, first.wanted, "the first pass loads everything it asked for");
    checkEq(first.kept, 0, "and keeps nothing, because nothing was resident");
    checkEq(first.released, 0, "and releases nothing");

    // The only assertion a use-after-free cannot fake: a structural identity. Reading a value back
    // through the mosaic would pass by luck, because a freed buffer is usually reused intact.
    checkEq(streamer.residentCount(), streamer.mosaic().count(), "every held brick is listed, and only those");

    // Standing still must cost nothing. A streamer that rebuilt its set every frame would make
    // the price of not moving equal to the price of travelling.
    const scroll::StreamReport still = streamer.update(params, eye);
    checkEq(still.loaded, 0, "standing still loads nothing");
    checkEq(still.released, 0, "and releases nothing");
    checkEq(still.kept, first.wanted, "everything is kept");
    const core::u64 readsAfterStill = store.reads;

    // Moving by less than a fine brick should keep most of the set.
    eye[2] += 64;
    const scroll::StreamReport nudge = streamer.update(params, eye);
    std::printf("  nudge by half a brick: %u loaded, %u released, %u kept\n", nudge.loaded, nudge.released, nudge.kept);
    check(nudge.kept > nudge.loaded, "a small step keeps more than it fetches");
    checkEq(streamer.residentCount(), streamer.mosaic().count(), "the mosaic still matches what is held");

    // Moving a long way should replace the fine detail and keep the coarse cover.
    eye[2] += 2000;
    const scroll::StreamReport leap = streamer.update(params, eye);
    std::printf("  leap of 2000 samples: %u loaded, %u released, %u kept\n", leap.loaded, leap.released, leap.kept);
    check(leap.loaded > 0u, "a long move fetches new ground");
    check(leap.released > 0u, "and drops what is behind");
    checkEq(streamer.residentCount(), streamer.mosaic().count(), "and the mosaic follows");
    check(store.reads > readsAfterStill, "the store was actually asked");

    // A chunk the store does not have is ABSENT, not failed: zarr does not store chunks that are
    // entirely fill value, so absence is a normal answer about a sparse volume.
    {
        FormulaStore sparse;
        std::snprintf(sparse.withhold, sizeof(sparse.withhold), "0/16/16/16");
        scroll::VolumeStreamer thin(sparse, geometry, meta);
        core::i64 corner[3]{2048, 2048, 2048};
        const scroll::StreamReport r = thin.update(params, corner);
        checkEq(r.failed, 0, "a withheld chunk is not a failure");
        check(r.absent >= 1u, "it is counted absent");
        checkEq(thin.residentCount(), thin.mosaic().count(), "and the mosaic is still consistent");
    }

    // The curve is measured from what is resident, so it can be re-measured as the eye moves into
    // a different part of the subject.
    {
        const voxel::DensityProfile p = streamer.measureProfile(0.133f, 1.0f);
        check(p.valid(), "a profile comes out of the resident set");
        check(p.mean > 100.0f && p.mean < 220.0f, "with a mean inside the fixture's range");
        check(p.sheetSample > p.floorSample, "and a window that is the right way round");
    }

    std::printf("  totals: %llu loads, %llu releases, %llu store reads\n",
                static_cast<unsigned long long>(streamer.totalLoads()),
                static_cast<unsigned long long>(streamer.totalReleases()),
                static_cast<unsigned long long>(store.reads));
    std::printf("%s (%d failures, %d checks)\n", gFailures == 0 ? "ALL PASS" : "FAILURES", gFailures, gChecks);
    return gFailures == 0 ? 0 : 1;
}
