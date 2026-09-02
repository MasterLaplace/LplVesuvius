/**
 * @file HttpStore.cpp
 * @brief One reused connection, a disk cache in front, and 404 kept distinct from failure.
 *
 * @author MasterLaplace
 * @version 0.1.0
 * @copyright MIT License
 */

#include <lpl/scroll/HttpStore.hpp>

#include <cstdio>
#include <cstring>

#if defined(LPL_SCROLL_HAS_CURL)
#    include <curl/curl.h>
#endif

namespace lpl::scroll {

namespace {

struct Sink final {
    core::u8 *buffer{nullptr};
    core::usize capacity{0};
    core::usize written{0};
    bool overflow{false};
};

extern "C" core::usize sinkWrite(void *data, core::usize size, core::usize count, void *user) noexcept
{
    Sink *sink = static_cast<Sink *>(user);
    const core::usize n = size * count;
    if (sink->written + n > sink->capacity)
    {
        sink->overflow = true;
        sink->written += n; // Keep counting so the caller learns what it would have needed.
        return n;           // Consume it: aborting mid-body leaves the connection unusable.
    }
    std::memcpy(sink->buffer + sink->written, data, n);
    sink->written += n;
    return n;
}

} // namespace

HttpStore::HttpStore(const char *prefix, const char *cacheRoot) noexcept : _cache(cacheRoot)
{
    if (prefix != nullptr)
    {
        const core::usize n = std::strlen(prefix);
        if (n + 1u < sizeof(_prefix))
            std::memcpy(_prefix, prefix, n + 1u);
    }
    _caching = cacheRoot != nullptr && _cache.valid();

#if defined(LPL_SCROLL_HAS_CURL)
    static bool globalReady = false;
    if (!globalReady)
    {
        curl_global_init(CURL_GLOBAL_DEFAULT);
        globalReady = true;
    }
    CURL *curl = curl_easy_init();
    if (curl != nullptr)
    {
        curl_easy_setopt(curl, CURLOPT_WRITEFUNCTION, sinkWrite);
        curl_easy_setopt(curl, CURLOPT_FOLLOWLOCATION, 1L);
        curl_easy_setopt(curl, CURLOPT_TIMEOUT, 90L);
        curl_easy_setopt(curl, CURLOPT_CONNECTTIMEOUT, 15L);
        curl_easy_setopt(curl, CURLOPT_NOSIGNAL, 1L);
        curl_easy_setopt(curl, CURLOPT_USERAGENT, "lpl-scrollwalk/0.1");
        // FAILONERROR is deliberately OFF: a 503 is an answer -- it means "later" -- and turning
        // it into a transport error would make throttling indistinguishable from unreachable.
    }
    _handle = curl;
#endif
}

HttpStore::~HttpStore()
{
#if defined(LPL_SCROLL_HAS_CURL)
    if (_handle != nullptr)
        curl_easy_cleanup(static_cast<CURL *>(_handle));
#endif
    _handle = nullptr;
}


zarr::FetchResult HttpStore::read(const char *key, core::u8 *buffer, core::usize capacity) noexcept
{
    if (key == nullptr || buffer == nullptr)
        return zarr::FetchResult{zarr::FetchStatus::Failed, 0u};

    if (_caching)
    {
        const zarr::FetchResult cached = _cache.read(key, buffer, capacity);
        if (cached.ok())
        {
            ++_hits;
            return cached;
        }
        if (cached.status == zarr::FetchStatus::TooLarge)
            return cached;
    }

#if !defined(LPL_SCROLL_HAS_CURL)
    ++_failures;
    return zarr::FetchResult{zarr::FetchStatus::Failed, 0u};
#else
    if (_handle == nullptr)
    {
        ++_failures;
        return zarr::FetchResult{zarr::FetchStatus::Failed, 0u};
    }

    char url[1024];
    const int n = std::snprintf(url, sizeof(url), "%s/%s", _prefix, key);
    // snprintf truncates in silence, and a truncated URL is a request for a different object that
    // usually 404s -- which this store would then report as a legitimately absent chunk.
    if (n <= 0 || static_cast<core::usize>(n) >= sizeof(url))
    {
        ++_failures;
        return zarr::FetchResult{zarr::FetchStatus::Failed, 0u};
    }

    Sink sink{buffer, capacity, 0u, false};
    CURL *curl = static_cast<CURL *>(_handle);
    curl_easy_setopt(curl, CURLOPT_URL, url);
    curl_easy_setopt(curl, CURLOPT_WRITEDATA, &sink);

    const CURLcode code = curl_easy_perform(curl);
    if (code != CURLE_OK)
    {
        ++_failures;
        return zarr::FetchResult{zarr::FetchStatus::Failed, 0u};
    }

    long status = 0;
    curl_easy_getinfo(curl, CURLINFO_RESPONSE_CODE, &status);
    if (status == 404 || status == 403)
    {
        // The open bucket answers 403 for a key it does not have, because listing is denied. Both
        // mean the same thing here: no such chunk, therefore all fill value.
        ++_absent;
        return zarr::FetchResult{zarr::FetchStatus::Absent, 0u};
    }
    if (status < 200 || status >= 300)
    {
        ++_failures;
        return zarr::FetchResult{zarr::FetchStatus::Failed, 0u};
    }
    if (sink.overflow)
        return zarr::FetchResult{zarr::FetchStatus::TooLarge, sink.written};

    ++_fetches;
    _received += sink.written;
    if (_caching)
        (void) _cache.write(key, buffer, sink.written);
    return zarr::FetchResult{zarr::FetchStatus::Ok, sink.written};
#endif
}

} // namespace lpl::scroll
