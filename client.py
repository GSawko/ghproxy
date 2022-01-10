from threading import Semaphore
from ghapi.all import GhApi, pages

# CONCURRENT_REQUESTS_MAX is the max number of concurrent requests tolerated by the api.github.com API.
CONCURRENT_REQUESTS_MAX = 100

# CONCURRENT_REQUESTS helps prevent exceeding api.github.com's concurrent requests limit.
# We assume that the concurrent requests limit is based on the client IP address
# (and not the personal github token).
CONCURRENT_REQUESTS = Semaphore(CONCURRENT_REQUESTS_MAX)


def fetch(api: GhApi, func, *args, per_page=None):
    """
    Call the given GhApi method with the given args.
    If the method supports paging, the per_page kwarg is mandatory.
    fetch will obtain the result efficiently:
    it will query pages in parallel and honor CONCURRENT_REQUESTS_MAX.
    """

    if per_page is None:
        ret = call_synced(func, *args)
    else:
        ret = call_synced(func, *args, per_page=per_page)

    # Fast path: don't need paging.
    last_page = api.last_page()
    if last_page == 0:
        return ret

    # Slow path: query pages in parallel.
    if per_page is None:
        raise Exception('per_page must be set')
    ret = pages(
        call_synced,
        last_page,
        func,
        *args,
        n_workers=min(CONCURRENT_REQUESTS_MAX, last_page),
        per_page=per_page,
    ).concat()

    return list(ret)


def call_synced(func, *args, **kwargs):
    """
    Run the given function under the CONCURRENT_REQUESTS semaphore.
    """

    CONCURRENT_REQUESTS.acquire()
    try:
        return func(*args, **kwargs)
    finally:
        CONCURRENT_REQUESTS.release()
