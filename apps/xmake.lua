-- /////////////////////////////////////////////////////////////////////////////
-- @file xmake.lua
-- @brief Applications of the native half of LplVesuvius.
-- /////////////////////////////////////////////////////////////////////////////

target("lpl-scrollwalk")
    set_kind("binary")
    set_group("apps")
    add_deps("lpl-core", "lpl-math", "lpl-voxel", "lpl-zarr", "lpl-scroll")
    add_files("scrollwalk/main.cpp")
target_end()

target("lpl-scrollfly")
    set_kind("binary")
    set_group("apps")
    add_deps("lpl-core", "lpl-math", "lpl-voxel", "lpl-zarr", "lpl-scroll")
    add_files("scrollfly/main.cpp")
    add_syslinks("GL", "X11", "pthread")
target_end()
