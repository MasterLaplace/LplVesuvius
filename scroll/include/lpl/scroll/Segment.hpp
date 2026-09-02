/**
 * @file Segment.hpp
 * @brief Reading a published segment surface, so somebody else's trace can be put beside ours.
 *
 * @warning **This is the comparison the tool exists to make possible.** A traced sheet is judged
 * today by looking at flat slices; two traces of the same region are compared by looking at two
 * sets of flat slices. Loaded into the same volume as the walk that generated one, they can be
 * looked at together and measured against each other in the units the scan is in.
 *
 * @warning **The axis order is a CONVENTION and it is stated rather than assumed.** A corpus
 * writes vertices in the order its own tooling used, and getting it wrong produces a surface that
 * is a plausible sheet somewhere else in the scroll -- it renders, it looks like papyrus, and it
 * is the subject transposed. The default matches the Vesuvius Challenge segment meshes, whose
 * vertices are in volume voxels as (x, y, z); anything else is the caller's to declare.
 *
 * @author MasterLaplace
 * @version 0.1.0
 * @copyright MIT License
 */

#pragma once

#ifndef LPL_SCROLL_SEGMENT_HPP
#    define LPL_SCROLL_SEGMENT_HPP

#    include <lpl/math/Vec3.hpp>
#    include <lpl/voxel/Surface.hpp>

namespace lpl::scroll {

/**
 * @struct SegmentLoad
 * @brief What came out of a segment file, and what did not.
 */
struct SegmentLoad final {
    core::u32 vertices{0};
    core::u32 triangles{0};
    core::u32 skippedFaces{0}; ///< Faces referring to a vertex the file never declared.
    core::u32 quads{0};        ///< Four-sided faces, split into two triangles.
    core::u32 textures{0};     ///< Texture coordinates: the segment's own flattening.
    bool opened{false};
};

/**
 * @brief Reads a Wavefront OBJ into caller-owned storage, in level-0 sample coordinates.
 *
 * Only `v` and `f` are read. Normals and texture coordinates are ignored on purpose: the surface
 * is shaded from the geometry, so carrying a normal the file asserts would be a second answer to
 * which way the sheet faces.
 *
 * @param scale  Multiplier applied to every vertex. A segment written for a downsampled volume
 *               needs it; one written for level 0 does not. There is no way to detect which from
 *               the file, so it is a parameter rather than a guess.
 */
[[nodiscard]] SegmentLoad loadSegmentObj(const char *path, math::Vec3<core::f32> *points, core::u32 pointCapacity,
                                         core::u32 *indices, core::u32 indexCapacity, core::f32 scale,
                                         core::f32 *texture = nullptr, core::u32 textureCapacity = 0u,
                                         core::u32 *textureIndices = nullptr) noexcept;

/**
 * @struct GreyImage
 * @brief A single-channel image, in caller-owned storage.
 */
struct GreyImage final {
    core::u8 *samples{nullptr};
    core::u32 width{0};
    core::u32 height{0};

    [[nodiscard]] constexpr bool valid() const noexcept
    {
        return samples != nullptr && width != 0u && height != 0u;
    }
};

/**
 * @brief Reads a binary PGM or PPM into @p out.
 *
 * @warning **PGM and PPM only, and that is a stated limit rather than an oversight.** The corpus
 * publishes predictions as PNG, which needs a decompressor -- a dependency this module would carry
 * forever so that a conversion somebody can do in one line happens inside the binary instead of
 * beside it. The caller is told the command when the file is not one of these.
 *
 * @return Whether the file was read. @p out keeps the caller's buffer either way.
 */
[[nodiscard]] bool loadGreyImage(const char *path, GreyImage &out, core::u32 capacity) noexcept;

/**
 * @struct SurfaceAgreement
 * @brief How far one surface sits from another, sample by sample.
 *
 * @warning **The median is the number to read, not the mean.** Two traces of the same sheet agree
 * almost everywhere and disagree wildly where one of them left the surface; a mean folds those
 * few points into the whole and reports a disagreement that exists nowhere. The worst case is
 * reported separately because it is the interesting one.
 */
struct SurfaceAgreement final {
    core::u32 compared{0};      ///< Points of the first surface that found anything to compare to.
    core::u32 unmatched{0};     ///< Points with nothing within the search radius: no overlap there.
    core::f32 medianSamples{0.0f};
    core::f32 worstSamples{0.0f};
    core::f32 meanSamples{0.0f};
};

/**
 * @brief Measures how far each point of @p from sits from the nearest triangle of @p to.
 *
 * @warning Point-to-TRIANGLE, not point-to-vertex. Two surfaces meshed at different densities
 * have vertices nowhere near each other while lying on exactly the same sheet, so a
 * vertex-to-vertex distance reports a disagreement that is entirely an artefact of tessellation.
 *
 * @param searchSamples  Beyond this, a point counts as unmatched rather than as a large distance.
 *                       Folding "no overlap" into "disagrees a lot" is how a comparison of two
 *                       partly-overlapping surfaces comes out meaningless.
 */
[[nodiscard]] SurfaceAgreement compareSurfaces(const math::Vec3<core::f32> *from, core::u32 fromCount,
                                               const voxel::SurfaceMesh &to, core::f32 searchSamples) noexcept;

} // namespace lpl::scroll

#endif // LPL_SCROLL_SEGMENT_HPP
