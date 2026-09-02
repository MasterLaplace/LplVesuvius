-- /////////////////////////////////////////////////////////////////////////////
-- @file xmake.lua
-- @brief Build configuration for the lpl::scroll module — the Vesuvius adapter.
-- /////////////////////////////////////////////////////////////////////////////

target("lpl-scroll")
    set_kind("static")
    set_group("modules")
    add_deps("lpl-core", "lpl-math", "lpl-voxel", "lpl-zarr")
    add_includedirs("include", { public = true })
    add_files("src/**.cpp")
    add_headerfiles("include/(lpl/scroll/**.hpp)")
    if os.isfile("/usr/include/x86_64-linux-gnu/curl/curl.h") or os.isfile("/usr/include/curl/curl.h") then
        add_defines("LPL_SCROLL_HAS_CURL")
        add_syslinks("curl", { public = true })
    end
target_end()
