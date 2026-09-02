/**
 * @file Volpkg.cpp
 * @brief Reading a resolution out of a filename.
 *
 * @author MasterLaplace
 * @version 0.1.0
 * @copyright MIT License
 */

#include <lpl/scroll/Volpkg.hpp>

namespace lpl::scroll {

namespace {

/// Reads a decimal number ending just before @p suffix, scanning backwards from it.
[[nodiscard]] bool numberBefore(const char *text, core::usize at, core::f32 &out) noexcept
{
    core::usize end = at;
    core::usize begin = at;
    while (begin > 0u)
    {
        const char c = text[begin - 1u];
        if ((c >= '0' && c <= '9') || c == '.')
        {
            --begin;
            continue;
        }
        break;
    }
    if (begin == end)
        return false;

    core::f32 whole = 0.0f;
    core::f32 frac = 0.0f;
    core::f32 scale = 1.0f;
    bool afterPoint = false;
    for (core::usize i = begin; i < end; ++i)
    {
        const char c = text[i];
        if (c == '.')
        {
            if (afterPoint)
                return false;
            afterPoint = true;
            continue;
        }
        if (!afterPoint)
        {
            whole = whole * 10.0f + static_cast<core::f32>(c - '0');
        }
        else
        {
            scale *= 0.1f;
            frac += static_cast<core::f32>(c - '0') * scale;
        }
    }
    out = whole + frac;
    return out > 0.0f;
}

[[nodiscard]] bool findSuffix(const char *text, const char *needle, core::usize &at) noexcept
{
    for (core::usize i = 0u; text[i] != '\0'; ++i)
    {
        core::usize j = 0u;
        while (needle[j] != '\0' && text[i + j] == needle[j])
            ++j;
        if (needle[j] == '\0')
        {
            at = i;
            return true;
        }
    }
    return false;
}

} // namespace

VolumeName parseVolumeName(const char *name) noexcept
{
    VolumeName out{};
    if (name == nullptr)
        return out;

    core::usize at = 0u;
    if (findSuffix(name, "um", at) && numberBefore(name, at, out.micrometres))
        out.parsed = true;
    if (findSuffix(name, "keV", at))
        (void) numberBefore(name, at, out.kiloElectronVolts);
    out.masked = findSuffix(name, "masked", at);
    return out;
}

voxel::VolumeGeometry geometryOf(const core::i64 shape[3], core::u32 levels, const VolumeName &name,
                                 core::f32 corridorMetres) noexcept
{
    voxel::VolumeGeometry g{};
    if (shape == nullptr || !name.parsed)
        return g;

    g.samples[0] = shape[0];
    g.samples[1] = shape[1];
    g.samples[2] = shape[2];
    g.levels = levels == 0u ? 1u : levels;
    g.voxelMicrometres = name.micrometres;

    const PapyrusMetrics metrics{};
    g.metresPerMicrometre = metrics.metresPerMicrometre(corridorMetres);
    return g;
}

} // namespace lpl::scroll
