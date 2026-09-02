-- /////////////////////////////////////////////////////////////////////////////
-- @file xmake.lua
-- @brief Tests for the Vesuvius adapter. Nothing here touches the network: a
-- check that needs the bucket goes red when the bucket does.
-- /////////////////////////////////////////////////////////////////////////////

target("test-volpkg")
    set_kind("binary")
    set_group("tests")
    add_deps("lpl-core", "lpl-math", "lpl-voxel", "lpl-scroll")
    add_files("test_volpkg.cpp")
target_end()

target("test-streamer")
    set_kind("binary")
    set_group("tests")
    add_deps("lpl-core", "lpl-math", "lpl-voxel", "lpl-zarr", "lpl-scroll")
    add_files("test_streamer.cpp")
target_end()

target("test-segment")
    set_kind("binary")
    set_group("tests")
    add_deps("lpl-core", "lpl-math", "lpl-voxel", "lpl-scroll")
    add_files("test_segment.cpp")
target_end()
