/**
 * @file Streamer.cpp
 * @brief Release, then load, then relist.
 *
 * @author MasterLaplace
 * @version 0.1.0
 * @copyright MIT License
 */

#include <lpl/scroll/Streamer.hpp>

#include <cstdio>

namespace lpl::scroll {

VolumeStreamer::VolumeStreamer(zarr::IZarrStore &store, const voxel::VolumeGeometry &geometry,
                               const std::vector<zarr::ArrayMeta> &meta) noexcept
    : _store(store), _geometry(geometry), _meta(meta), _scratch(4u << 20)
{
}

void VolumeStreamer::rebuildMosaic() noexcept
{
    // Relisted from scratch AFTER every allocation has settled. A vector that grows moves its
    // elements, so a mosaic listed during the loading loop would point at buffers that have been
    // relocated -- freed memory that reads back convincingly, and a picture that is wrong with
    // nothing to say so.
    _mosaic.clear();
    for (Slot &slot : _slots)
    {
        voxel::BrickView view{};
        view.voxels = slot.bytes.data();
        view.key = slot.key;
        // The occupancy grid lives beside the brick and for exactly as long: a kibibyte against
        // two mebibytes, and it is what lets a ray leave the medium in one comparison.
        voxel::summariseCells(view, slot.cells.data());
        (void) _mosaic.insert(view);
    }
}

StreamReport VolumeStreamer::update(const voxel::ResidencyParams &params, const core::i64 eye[3]) noexcept
{
    StreamReport report{};

    std::vector<voxel::BrickKey> plan(params.budget);
    report.wanted = voxel::planResidency(_geometry, params, eye, plan.data(), params.budget);

    for (Slot &slot : _slots)
        slot.wanted = false;
    for (core::u32 i = 0u; i < report.wanted; ++i)
    {
        for (Slot &slot : _slots)
        {
            if (slot.key == plan[i])
            {
                slot.wanted = true;
                ++report.kept;
                break;
            }
        }
    }

    // Release first, so swapping one brick for another never needs room for both.
    for (core::usize i = _slots.size(); i-- > 0u;)
    {
        if (_slots[i].wanted)
            continue;
        _slots[i] = std::move(_slots.back());
        _slots.pop_back();
        ++report.released;
        ++_totalReleases;
    }

    for (core::u32 i = 0u; i < report.wanted; ++i)
    {
        const voxel::BrickKey &key = plan[i];
        bool already = false;
        for (const Slot &slot : _slots)
        {
            if (slot.key == key)
            {
                already = true;
                break;
            }
        }
        if (already)
            continue;
        if (key.level >= _meta.size())
            continue;

        const zarr::ArrayMeta &m = _meta[key.level];
        char prefix[16];
        std::snprintf(prefix, sizeof(prefix), "%u", key.level);
        const core::i64 index[3]{key.z, key.y, key.x};
        char storeKey[zarr::kMaxKeyLength];
        if (!zarr::chunkKey(m, prefix, index, storeKey))
        {
            ++report.failed;
            continue;
        }

        Slot slot{};
        slot.key = key;
        slot.wanted = true;
        slot.bytes.resize(m.chunkBytes());
        slot.cells.resize(voxel::kOccupancyBytes);
        const zarr::FetchResult r = zarr::readChunk(_store, m, storeKey, slot.bytes.data(), slot.bytes.size(),
                                                    _scratch.data(), _scratch.size());
        if (!r.ok())
        {
            if (r.status == zarr::FetchStatus::Absent)
                ++report.absent;
            else
                ++report.failed;
            continue;
        }
        if (r.filled)
            ++report.absent; // Held anyway: all fill IS the content of that region.
        else
            report.bytes += r.size;
        _slots.push_back(std::move(slot));
        ++report.loaded;
        ++_totalLoads;
    }

    rebuildMosaic();
    return report;
}

voxel::DensityProfile VolumeStreamer::measureProfile(core::f32 quantile, core::f32 windowDeviations) const noexcept
{
    std::vector<voxel::BrickView> views;
    views.reserve(_mosaic.count());
    for (core::u32 i = 0u; i < _mosaic.count(); ++i)
        views.push_back(_mosaic.at(i));
    voxel::DensityProfile profile =
        voxel::measureProfile(views.data(), static_cast<core::u32>(views.size()), quantile, windowDeviations);

    // And the per-level correction, measured over a box the FINEST level actually covers -- so the
    // levels are compared on the same region rather than on however much of the world each of them
    // happens to reach. Left unmeasured every ratio is one, which is not a neutral default: it
    // leaves the curve calibrated on the finest level painting the whole histogram a few levels up,
    // and that is what makes a level of detail show up as tiling.
    if (_mosaic.count() != 0u)
    {
        core::i64 finestSpan = 0;
        core::i64 centre[3]{0, 0, 0};
        core::u32 finest = voxel::kMaxPyramidLevels;
        for (core::u32 i = 0u; i < _mosaic.count(); ++i)
        {
            const voxel::BrickView &b = _mosaic.at(i);
            if (b.key.level >= finest)
                continue;
            finest = b.key.level;
            finestSpan = voxel::brickSpanInBaseSamples(b.key.level);
            centre[0] = static_cast<core::i64>(b.key.z) * finestSpan + finestSpan / 2;
            centre[1] = static_cast<core::i64>(b.key.y) * finestSpan + finestSpan / 2;
            centre[2] = static_cast<core::i64>(b.key.x) * finestSpan + finestSpan / 2;
        }
        if (finestSpan > 0)
            voxel::measureSpreadOverBox(profile, _mosaic, centre, finestSpan / 2);
    }
    return profile;
}

} // namespace lpl::scroll
