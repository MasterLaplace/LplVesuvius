/**
 * @file HttpStore.hpp
 * @brief A zarr store over HTTPS, with a disk cache in front of it.
 *
 * @warning **The cache is not a fallback for a slow link, it is the design.** Measured against the
 * open bucket from a home connection: 4.98 MB/s, about 2.4 chunks a second. Filling a resident set
 * from cold takes minutes, and doing it again on every launch would make the tool unusable long
 * before the renderer became the bottleneck. Pages backed by a file are RAM, read at memory speed
 * and reclaimable under pressure; the all-in-process alternative is the arrangement that gets
 * killed.
 *
 * @warning **libcurl as a LIBRARY, not the binary.** A walk asks for thousands of chunks, and a
 * process per request pays a TCP and TLS handshake every time -- slower, and the impolite way to
 * traverse a server that agreed to be traversed. This project measured a factor of 7.9 on exactly
 * that change elsewhere.
 *
 * @warning **A 404 is ABSENCE and anything else is failure.** Zarr does not store chunks that are
 * entirely fill value, so a missing key is a normal answer with a meaning. A store that folded a
 * timeout into the same answer would render holes and say nothing.
 *
 * @author MasterLaplace
 * @version 0.1.0
 * @copyright MIT License
 */

#pragma once

#ifndef LPL_SCROLL_HTTPSTORE_HPP
#    define LPL_SCROLL_HTTPSTORE_HPP

#    include <lpl/zarr/FileStore.hpp>
#    include <lpl/zarr/Store.hpp>

namespace lpl::scroll {

/**
 * @class HttpStore
 * @brief Reads keys from a URL prefix, writing what it fetches into a local store.
 */
class HttpStore final : public zarr::IZarrStore {
public:
    /**
     * @param prefix     URL the keys hang off, without a trailing slash.
     * @param cacheRoot  Directory to keep fetched values in; null disables caching.
     *
     * @warning Do not point the cache at a tmpfs. `/tmp` is one on many systems, so the "cache"
     * would BE memory and the whole arrangement would consume exactly what it exists to avoid.
     * This project already made that measurement mistake once.
     */
    HttpStore(const char *prefix, const char *cacheRoot) noexcept;
    ~HttpStore() override;

    HttpStore(const HttpStore &) = delete;
    HttpStore &operator=(const HttpStore &) = delete;

    [[nodiscard]] zarr::FetchResult read(const char *key, core::u8 *buffer, core::usize capacity) noexcept override;
    [[nodiscard]] const char *name() const noexcept override { return "HttpStore"; }

    [[nodiscard]] bool valid() const noexcept { return _handle != nullptr; }

    /// Values served from the local cache rather than the network.
    [[nodiscard]] core::u64 hits() const noexcept { return _hits; }
    /// Values fetched over the network.
    [[nodiscard]] core::u64 fetches() const noexcept { return _fetches; }
    /// Keys the server does not have: entirely fill value, which is not an error.
    [[nodiscard]] core::u64 absent() const noexcept { return _absent; }
    /// Transport failures. Distinct from absence, on purpose.
    [[nodiscard]] core::u64 failures() const noexcept { return _failures; }
    /// Bytes received on the wire.
    [[nodiscard]] core::u64 received() const noexcept { return _received; }

private:
    void *_handle{nullptr}; ///< CURL*, kept opaque so the header pulls in no curl.
    char _prefix[512]{};
    zarr::FileStore _cache;
    bool _caching{false};
    core::u64 _hits{0};
    core::u64 _fetches{0};
    core::u64 _absent{0};
    core::u64 _failures{0};
    core::u64 _received{0};
};

} // namespace lpl::scroll

#endif // LPL_SCROLL_HTTPSTORE_HPP
