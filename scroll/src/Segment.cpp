/**
 * @file Segment.cpp
 * @brief An OBJ reader, and a point-to-triangle comparison.
 *
 * @author MasterLaplace
 * @version 0.1.0
 * @copyright MIT License
 */

#include <lpl/scroll/Segment.hpp>

#include <algorithm>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <vector>

namespace lpl::scroll {

namespace {

/// Reads the vertex and texture indices out of an OBJ face token: "v", "v/t", "v//n" or "v/t/n".
void faceIndices(const char *token, long &vertex, long &texture) noexcept
{
    char *after = nullptr;
    vertex = std::strtol(token, &after, 10);
    texture = 0;
    if (after == nullptr || *after != '/')
        return;
    ++after;
    if (*after == '/')
        return; // "v//n": no texture coordinate on this corner.
    texture = std::strtol(after, nullptr, 10);
}

[[nodiscard]] core::f32 squareRoot(core::f32 v) noexcept
{
    if (v <= 0.0f)
        return 0.0f;
    core::f32 g = v > 1.0f ? v : 1.0f;
    for (int i = 0; i < 24; ++i)
        g = 0.5f * (g + v / g);
    return g;
}

using Point = math::Vec3<core::f32>;

[[nodiscard]] core::f32 dot(const Point &a, const Point &b) noexcept { return a.x * b.x + a.y * b.y + a.z * b.z; }

/// Squared distance from @p p to the triangle (a, b, c). Ericson's closed form: no iteration.
[[nodiscard]] core::f32 distanceSquaredToTriangle(const Point &p, const Point &a, const Point &b,
                                                  const Point &c) noexcept
{
    const Point ab{b.x - a.x, b.y - a.y, b.z - a.z};
    const Point ac{c.x - a.x, c.y - a.y, c.z - a.z};
    const Point ap{p.x - a.x, p.y - a.y, p.z - a.z};
    const core::f32 d1 = dot(ab, ap);
    const core::f32 d2 = dot(ac, ap);
    const auto lengthSquared = [](const Point &v) { return v.x * v.x + v.y * v.y + v.z * v.z; };
    if (d1 <= 0.0f && d2 <= 0.0f)
        return lengthSquared(ap);

    const Point bp{p.x - b.x, p.y - b.y, p.z - b.z};
    const core::f32 d3 = dot(ab, bp);
    const core::f32 d4 = dot(ac, bp);
    if (d3 >= 0.0f && d4 <= d3)
        return lengthSquared(bp);

    const core::f32 vc = d1 * d4 - d3 * d2;
    if (vc <= 0.0f && d1 >= 0.0f && d3 <= 0.0f)
    {
        const core::f32 v = d1 / (d1 - d3);
        const Point q{a.x + ab.x * v - p.x, a.y + ab.y * v - p.y, a.z + ab.z * v - p.z};
        return lengthSquared(q);
    }

    const Point cp{p.x - c.x, p.y - c.y, p.z - c.z};
    const core::f32 d5 = dot(ab, cp);
    const core::f32 d6 = dot(ac, cp);
    if (d6 >= 0.0f && d5 <= d6)
        return lengthSquared(cp);

    const core::f32 vb = d5 * d2 - d1 * d6;
    if (vb <= 0.0f && d2 >= 0.0f && d6 <= 0.0f)
    {
        const core::f32 w = d2 / (d2 - d6);
        const Point q{a.x + ac.x * w - p.x, a.y + ac.y * w - p.y, a.z + ac.z * w - p.z};
        return lengthSquared(q);
    }

    const core::f32 va = d3 * d6 - d5 * d4;
    if (va <= 0.0f && (d4 - d3) >= 0.0f && (d5 - d6) >= 0.0f)
    {
        const core::f32 w = (d4 - d3) / ((d4 - d3) + (d5 - d6));
        const Point q{b.x + (c.x - b.x) * w - p.x, b.y + (c.y - b.y) * w - p.y, b.z + (c.z - b.z) * w - p.z};
        return lengthSquared(q);
    }

    const core::f32 denominator = 1.0f / (va + vb + vc);
    const core::f32 v = vb * denominator;
    const core::f32 w = vc * denominator;
    const Point q{a.x + ab.x * v + ac.x * w - p.x, a.y + ab.y * v + ac.y * w - p.y, a.z + ab.z * v + ac.z * w - p.z};
    return lengthSquared(q);
}

} // namespace

SegmentLoad loadSegmentObj(const char *path, math::Vec3<core::f32> *points, core::u32 pointCapacity,
                           core::u32 *indices, core::u32 indexCapacity, core::f32 scale, core::f32 *texture,
                           core::u32 textureCapacity, core::u32 *textureIndices) noexcept
{
    SegmentLoad load{};
    if (path == nullptr || points == nullptr || indices == nullptr)
        return load;

    std::FILE *file = std::fopen(path, "rb");
    if (file == nullptr)
        return load;
    load.opened = true;

    char line[512];
    while (std::fgets(line, sizeof(line), file) != nullptr)
    {
        if (line[0] == 'v' && (line[1] == ' ' || line[1] == '\t'))
        {
            if (load.vertices >= pointCapacity)
                continue;
            float x = 0.0f;
            float y = 0.0f;
            float z = 0.0f;
            if (std::sscanf(line + 1, "%f %f %f", &x, &y, &z) != 3)
                continue;
            // Straight through in the order the file wrote them; see the header on why the axis
            // convention is stated rather than sniffed.
            points[load.vertices++] = math::Vec3<core::f32>{x * scale, y * scale, z * scale};
        }
        else if (line[0] == 'v' && line[1] == 't' && (line[2] == ' ' || line[2] == '\t'))
        {
            if (texture == nullptr || load.textures >= textureCapacity)
                continue;
            float u = 0.0f;
            float v = 0.0f;
            if (std::sscanf(line + 2, "%f %f", &u, &v) != 2)
                continue;
            texture[load.textures * 2u] = u;
            texture[load.textures * 2u + 1u] = v;
            ++load.textures;
        }
        else if (line[0] == 'f' && (line[1] == ' ' || line[1] == '\t'))
        {
            long corner[4]{0, 0, 0, 0};
            long corerTexture[4]{0, 0, 0, 0};
            core::u32 corners = 0u;
            for (char *token = std::strtok(line + 1, " \t\r\n"); token != nullptr && corners < 4u;
                 token = std::strtok(nullptr, " \t\r\n"))
            {
                faceIndices(token, corner[corners], corerTexture[corners]);
                ++corners;
            }
            if (corners < 3u)
                continue;

            // OBJ indices are one-based, and negative means "counting back from the end".
            const auto resolve = [&](long v) -> long {
                if (v > 0)
                    return v - 1;
                if (v < 0)
                    return static_cast<long>(load.vertices) + v;
                return -1;
            };
            long a = resolve(corner[0]);
            long b = resolve(corner[1]);
            long c = resolve(corner[2]);
            const auto resolveTexture = [&](long v) -> long {
                if (v > 0)
                    return v - 1;
                if (v < 0)
                    return static_cast<long>(load.textures) + v;
                return -1;
            };
            const auto emit = [&](long i, long j, long k, long ti, long tj, long tk) {
                if (i < 0 || j < 0 || k < 0 || i >= static_cast<long>(load.vertices) ||
                    j >= static_cast<long>(load.vertices) || k >= static_cast<long>(load.vertices))
                {
                    // A face that names a vertex the file never declared is dropped and counted.
                    // Clamping it instead would staple a triangle across the whole mesh.
                    ++load.skippedFaces;
                    return;
                }
                if (load.triangles * 3u + 3u > indexCapacity)
                    return;
                indices[load.triangles * 3u] = static_cast<core::u32>(i);
                indices[load.triangles * 3u + 1u] = static_cast<core::u32>(j);
                indices[load.triangles * 3u + 2u] = static_cast<core::u32>(k);
                if (textureIndices != nullptr)
                {
                    // Per CORNER: a vertex on the flattening's seam carries a different coordinate
                    // on each side, and an array indexed by vertex silently picks one -- which
                    // smears everything painted from the texture across the cut.
                    const long t[3]{ti, tj, tk};
                    for (core::u32 n = 0u; n < 3u; ++n)
                        textureIndices[load.triangles * 3u + n] =
                            t[n] >= 0 ? static_cast<core::u32>(t[n]) : 0u;
                }
                ++load.triangles;
            };
            emit(a, b, c, resolveTexture(corerTexture[0]), resolveTexture(corerTexture[1]),
                 resolveTexture(corerTexture[2]));
            if (corners == 4u)
            {
                ++load.quads;
                emit(a, c, resolve(corner[3]), resolveTexture(corerTexture[0]), resolveTexture(corerTexture[2]),
                     resolveTexture(corerTexture[3]));
            }
        }
    }
    std::fclose(file);
    return load;
}

bool loadGreyImage(const char *path, GreyImage &out, core::u32 capacity) noexcept
{
    if (path == nullptr || out.samples == nullptr)
        return false;
    std::FILE *file = std::fopen(path, "rb");
    if (file == nullptr)
        return false;

    char magic[3]{};
    if (std::fscanf(file, "%2s", magic) != 1 || (magic[0] != 'P' || (magic[1] != '5' && magic[1] != '6')))
    {
        std::fclose(file);
        return false;
    }
    const bool colour = magic[1] == '6';

    // Comments may sit between any two tokens of a netpbm header, and a reader that skips them
    // only after the magic breaks on files written by half the tools that emit these.
    const auto readNumber = [&](int &value) {
        int c = 0;
        do
        {
            c = std::fgetc(file);
            if (c == '#')
            {
                while (c != '\n' && c != EOF)
                    c = std::fgetc(file);
            }
        } while (c == ' ' || c == '\t' || c == '\n' || c == '\r');
        if (c == EOF)
            return false;
        value = 0;
        while (c >= '0' && c <= '9')
        {
            value = value * 10 + (c - '0');
            c = std::fgetc(file);
        }
        return true;
    };

    int width = 0;
    int height = 0;
    int maximum = 0;
    if (!readNumber(width) || !readNumber(height) || !readNumber(maximum) || width <= 0 || height <= 0 ||
        maximum != 255)
    {
        // Sixteen-bit netpbm exists and is not handled: reading it as eight would halve every
        // value and the prediction would come out uniformly faint rather than wrong-looking.
        std::fclose(file);
        return false;
    }
    const core::u32 pixels = static_cast<core::u32>(width) * static_cast<core::u32>(height);
    if (pixels > capacity)
    {
        std::fclose(file);
        return false;
    }

    bool ok = true;
    if (colour)
    {
        for (core::u32 i = 0u; i < pixels && ok; ++i)
        {
            int rgb[3]{};
            for (int k = 0; k < 3; ++k)
            {
                const int c = std::fgetc(file);
                if (c == EOF)
                    ok = false;
                rgb[k] = c;
            }
            out.samples[i] = static_cast<core::u8>((rgb[0] + rgb[1] + rgb[2]) / 3);
        }
    }
    else
    {
        ok = std::fread(out.samples, 1u, pixels, file) == pixels;
    }
    std::fclose(file);
    if (!ok)
        return false;
    out.width = static_cast<core::u32>(width);
    out.height = static_cast<core::u32>(height);
    return true;
}

SurfaceAgreement compareSurfaces(const math::Vec3<core::f32> *from, core::u32 fromCount, const voxel::SurfaceMesh &to,
                                 core::f32 searchSamples) noexcept
{
    SurfaceAgreement out{};
    if (from == nullptr || fromCount == 0u || !to.valid())
        return out;

    const core::f32 limitSquared = searchSamples * searchSamples;
    std::vector<core::f32> distances;
    distances.reserve(fromCount);
    core::f64 total = 0.0;

    for (core::u32 i = 0u; i < fromCount; ++i)
    {
        core::f32 best = 3.0e38f;
        for (core::u32 t = 0u; t + 2u < to.indexCount; t += 3u)
        {
            const core::f32 d = distanceSquaredToTriangle(from[i], to.points[to.indices[t]],
                                                          to.points[to.indices[t + 1u]], to.points[to.indices[t + 2u]]);
            if (d < best)
            {
                best = d;
                if (best < 1e-6f)
                    break;
            }
        }
        if (best > limitSquared)
        {
            // No overlap here. Counting it as a large distance instead would let the parts of two
            // surfaces that do not meet dominate the number describing the parts that do.
            ++out.unmatched;
            continue;
        }
        const core::f32 d = squareRoot(best);
        distances.push_back(d);
        total += static_cast<core::f64>(d);
        if (d > out.worstSamples)
            out.worstSamples = d;
    }

    out.compared = static_cast<core::u32>(distances.size());
    if (out.compared == 0u)
        return out;
    out.meanSamples = static_cast<core::f32>(total / static_cast<core::f64>(out.compared));
    std::nth_element(distances.begin(), distances.begin() + distances.size() / 2, distances.end());
    out.medianSamples = distances[distances.size() / 2];
    return out;
}

} // namespace lpl::scroll
