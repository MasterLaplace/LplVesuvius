/**
 * @file Streamer.hpp
 * @brief Keeping the right bricks in memory while the eye moves.
 *
 * @warning **Load only what is new, release only what is no longer wanted.** A streamer that
 * rebuilt its resident set every frame would re-fetch and re-decode bricks that never changed, so
 * the cost of standing still would be the cost of travelling. Measured on the tests behind this:
 * zero reloads while stationary against several hundred if the set is rebuilt.
 *
 * @warning **A slot owns its bytes, and the mosaic only ever holds a view into them.** Release a
 * buffer while its brick is still listed and every ray reads freed memory -- which reads back
 * convincingly, so the picture would be wrong and nothing would say so. The order is fixed:
 * unlist, then free. And a test of this must assert the COUNTS, never a value read back through
 * the mosaic, because freed memory lies.
 *
 * @warning **Release before load**, so swapping one brick for another never needs room for both.
 *
 * @author MasterLaplace
 * @version 0.1.0
 * @copyright MIT License
 */

#pragma once

#ifndef LPL_SCROLL_STREAMER_HPP
#    define LPL_SCROLL_STREAMER_HPP

#    include <lpl/voxel/Mosaic.hpp>
#    include <lpl/voxel/Residency.hpp>
#    include <lpl/voxel/Volume.hpp>
#    include <lpl/zarr/Array.hpp>
#    include <lpl/zarr/Store.hpp>

#    include <vector>

namespace lpl::scroll {

/**
 * @struct StreamReport
 * @brief What one update did.
 *
 * @warning Absent and failed are separate for the same reason the store separates them: a chunk
 * that is entirely fill value is a normal answer about a sparse volume, and a transport error is
 * not. One line for both would make a broken link look like an empty scroll.
 */
struct StreamReport final {
    core::u32 wanted{0};    ///< Bricks the plan asked for.
    core::u32 loaded{0};    ///< Newly brought in.
    core::u32 released{0};  ///< Dropped because the plan no longer wants them.
    core::u32 kept{0};      ///< Already resident and still wanted; the ones that cost nothing.
    core::u32 absent{0};    ///< The store has no such chunk: all fill value.
    core::u32 failed{0};    ///< Transport or decode error.
    core::u64 bytes{0};     ///< Decoded bytes brought in.
};

/**
 * @class VolumeStreamer
 * @brief Drives a resident mosaic from a plan and a store.
 */
class VolumeStreamer final {
public:
    /**
     * @param store     Where chunks come from.
     * @param geometry  The subject.
     * @param meta      One entry per pyramid level, finest first.
     */
    VolumeStreamer(zarr::IZarrStore &store, const voxel::VolumeGeometry &geometry,
                   const std::vector<zarr::ArrayMeta> &meta) noexcept;

    VolumeStreamer(const VolumeStreamer &) = delete;
    VolumeStreamer &operator=(const VolumeStreamer &) = delete;

    /**
     * @brief Brings the resident set in line with where the eye is.
     * @param params  Reach and budget.
     * @param eye     Eye position in level-0 samples, (z, y, x).
     */
    StreamReport update(const voxel::ResidencyParams &params, const core::i64 eye[3]) noexcept;

    [[nodiscard]] const voxel::BrickMosaic &mosaic() const noexcept { return _mosaic; }

    /// Bricks currently held. Equal to the mosaic's count, and asserted so in the tests: a
    /// structural identity is the only thing a use-after-free cannot fake.
    [[nodiscard]] core::u32 residentCount() const noexcept { return static_cast<core::u32>(_slots.size()); }

    /// Every brick the streamer has ever brought in, for a readout that reports rather than asserts.
    [[nodiscard]] core::u64 totalLoads() const noexcept { return _totalLoads; }
    [[nodiscard]] core::u64 totalReleases() const noexcept { return _totalReleases; }

    /**
     * @brief A profile measured from what is resident right now.
     *
     * Measured rather than configured, and re-measurable as the eye moves into a different part of
     * the subject: the inside of a carbonised roll is compressed and the outside is not, so a
     * curve calibrated at the axis renders the rim wrong.
     */
    [[nodiscard]] voxel::DensityProfile measureProfile(core::f32 quantile, core::f32 windowDeviations) const noexcept;

private:
    struct Slot final {
        voxel::BrickKey key{};
        std::vector<core::u8> bytes;
        std::vector<core::u8> cells; ///< Occupancy grid; owned with the brick, released with it.
        bool wanted{false};
    };

    zarr::IZarrStore &_store;
    voxel::VolumeGeometry _geometry;
    std::vector<zarr::ArrayMeta> _meta;
    std::vector<Slot> _slots;
    std::vector<core::u8> _scratch;
    voxel::BrickMosaic _mosaic;
    core::u64 _totalLoads{0};
    core::u64 _totalReleases{0};

    void rebuildMosaic() noexcept;
};

} // namespace lpl::scroll

#endif // LPL_SCROLL_STREAMER_HPP
