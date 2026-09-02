/**
 * @file Volpkg.hpp
 * @brief What the Vesuvius corpus puts where, and what its filenames mean.
 *
 * @warning **This is the only file in the tree that knows about Herculaneum.** Everything it feeds
 * -- the renderer, the format reader, the residency planner -- is generic and upstream. What is
 * genuinely local to this corpus is small and worth writing down exactly: a bucket laid out as
 * `<PHerc id>/volumes/<timestamp>-<resolution>um-<energy>keV[-masked].zarr`, a resolution carried
 * in the *filename* rather than in any metadata, and a mask convention where zero means "outside
 * the object" rather than "density zero".
 *
 * @warning **The resolution has to be read out of the name, and that is not a shortcut.** The
 * `.zattrs` of these volumes declares a coordinate transform of 1.0 on every axis -- the pyramid's
 * own scaling, not the physical one -- so the micrometre figure exists nowhere else. A viewer that
 * defaulted it would put every scroll at one scale and quietly make two of them different sizes.
 *
 * @author MasterLaplace
 * @version 0.1.0
 * @copyright MIT License
 */

#pragma once

#ifndef LPL_SCROLL_VOLPKG_HPP
#    define LPL_SCROLL_VOLPKG_HPP

#    include <lpl/core/Types.hpp>
#    include <lpl/voxel/Volume.hpp>

namespace lpl::scroll {

/// The open bucket the corpus publishes from.
inline constexpr const char *kOpenDataBucket = "https://vesuvius-challenge-open-data.s3.amazonaws.com";

/**
 * @struct VolumeName
 * @brief What a volume's own filename says about it.
 */
struct VolumeName final {
    core::f32 micrometres{0.0f}; ///< Sample edge, from the `-<n>um-` field.
    core::f32 kiloElectronVolts{0.0f};
    bool masked{false}; ///< Zero means outside the object, not zero density.
    bool parsed{false};
};

/**
 * @brief Reads a volume directory name such as `20241024131838-7.910um-53keV-masked.zarr`.
 *
 * @warning Returns `parsed == false` rather than a default when the name does not carry a
 * resolution. Defaulting would put an unknown scroll at somebody else's scale, and nothing
 * downstream could tell.
 */
[[nodiscard]] VolumeName parseVolumeName(const char *name) noexcept;

/**
 * @brief Physical constants of a carbonised Herculaneum roll, in micrometres.
 *
 * @warning Measured in this repository against real volumes and written down here rather than
 * spread through the code, because they are the numbers that decide the staging scale. A sheet is
 * about 40 um thick and the next spire sits about 300 um away, so roughly 260 um of the pitch is
 * the gap somebody walks down. The ink is a deposit of five to ten micrometres -- one voxel of
 * relief at the scale below, which is why letters read as carving rather than as paint.
 */
struct PapyrusMetrics final {
    core::f32 sheetMicrometres{40.0f};
    core::f32 spirePitchMicrometres{300.0f};
    core::f32 inkMicrometres{7.5f};

    [[nodiscard]] constexpr core::f32 gapMicrometres() const noexcept
    {
        return spirePitchMicrometres - sheetMicrometres;
    }

    /**
     * @brief Scale that puts the gap between two sheets at @p corridorMetres.
     *
     * The staging decision, stated as the thing a person can actually judge: how wide is the
     * corridor you are walking down. Three metres reads as a slot canyon; one voxel to one metre,
     * the obvious first idea, makes a body fourteen micrometres tall and the corridor fourteen
     * metres wide -- correct, and unreadable.
     */
    [[nodiscard]] constexpr core::f32 metresPerMicrometre(core::f32 corridorMetres) const noexcept
    {
        const core::f32 gap = gapMicrometres();
        return gap > 0.0f ? corridorMetres / (gap * 1e-6f) : 1.0f;
    }
};

/**
 * @brief Builds the geometry of a volume from its shape, its name and a staging choice.
 */
[[nodiscard]] voxel::VolumeGeometry geometryOf(const core::i64 shape[3], core::u32 levels, const VolumeName &name,
                                               core::f32 corridorMetres) noexcept;

} // namespace lpl::scroll

#endif // LPL_SCROLL_VOLPKG_HPP
