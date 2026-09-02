-- /////////////////////////////////////////////////////////////////////////////
-- @file xmake.lua
-- @brief Build configuration for the native half of LplVesuvius.
--
-- The Python under src/ measures; this measures nothing. It is the Vesuvius-shaped
-- adapter that lets the LplPlugin engine open a scanned scroll and fly through it:
-- the bucket layout, the naming convention that carries a voxel size, the physical
-- constants of carbonised papyrus, and an HTTP store in front of a disk cache.
--
-- ⚠ Everything GENERIC lives upstream, on purpose. Direct volume rendering is
-- `lpl::voxel` and the chunked-array format is `lpl::zarr`, both in LplPlugin,
-- because neither is about Herculaneum: zarr is the open standard behind OME-NGFF
-- bioimaging and simulation output, and a volume raymarcher serves any tomographic
-- stack. What stays here is the part that is only true of this corpus.
--
-- Unlike LplKnowledge, the foundation is REQUIRED rather than detected: there is
-- nothing to build here without a renderer, so a standalone build would be an
-- empty library with a reassuring name.
-- /////////////////////////////////////////////////////////////////////////////

add_rules("mode.debug", "mode.release")
set_languages("c++23", "c17")
set_warnings("allextra", "error")

add_cxxflags("-fno-rtti", { force = true })
add_cxxflags("-fno-exceptions", { force = true })

option("engine-root")
    set_default("../LplKernel/LplPlugin")
    set_showmenu(true)
    set_description("Path to the LplPlugin checkout this repository renders with")
option_end()

ENGINE = get_config("engine-root") or "../LplKernel/LplPlugin"
if not os.isdir(path.join(ENGINE, "voxel/include")) then
    raise("LplPlugin not found at '" .. ENGINE .. "'. Pass --engine-root=<path>; there is nothing " ..
          "to build here without it, so failing now beats linking an empty library.")
end

-- The engine modules this repository actually uses, built from the neighbouring
-- checkout. Listing them rather than including LplPlugin's root script keeps this
-- build free of its apps, its tests and its Vulkan option.
for _, module in ipairs({ "core", "math", "voxel", "zarr" }) do
    target("lpl-" .. module)
        set_kind("static")
        set_group("engine")
        add_includedirs(path.join(ENGINE, module, "include"), { public = true })
        if os.isdir(path.join(ENGINE, module, "src")) then
            add_files(path.join(ENGINE, module, "src/**.cpp"))
        end
        if module == "math" then
            add_deps("lpl-core")
        elseif module == "voxel" then
            add_deps("lpl-core", "lpl-math")
        elseif module == "zarr" then
            add_deps("lpl-core")
            if os.isfile("/usr/include/blosc.h") then
                add_defines("LPL_ZARR_HAS_BLOSC")
                add_syslinks("blosc", { public = true })
            end
            if os.isfile("/usr/include/zstd.h") then
                add_defines("LPL_ZARR_HAS_ZSTD")
                add_syslinks("zstd", { public = true })
            end
        end
    target_end()
end

includes("scroll", "apps", "tests")
