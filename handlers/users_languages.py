import re
import sys
import json
from http.server import BaseHTTPRequestHandler
from urllib.error import HTTPError
from auth import gh_token
from client import fetch, CONCURRENT_REQUESTS_MAX
from ghapi.all import GhApi
from fastcore.utils import parallel

ROUTE_RE = re.compile(r'^/users/([^/]+)/stats/languages$')


def handler(h: BaseHTTPRequestHandler, username: str):
    """
    Return the top 10 most popular languages for the given user.
    """

    # Obtain ghapi handle.
    api = GhApi(token=gh_token(h.headers))

    # Fetch repo list.
    try:
        per_page = 30  # the default according to https://docs.github.com/en/rest/reference/repos#list-repositories-for-a-user
        repos = fetch(api, api.repos.list_for_user, username, per_page=per_page)
    except HTTPError as e:
        h.send_response(e.code, e.msg)
        for k, v in e.hdrs.items():
            h.send_header(k, v)
        h.end_headers()
        h.wfile.write(e.fp.read())
        return
    except Exception as e:
        msg = f"error obtaining repos for the user {username}: {e}\n"
        sys.stderr.write(msg)
        h.send_response(500, msg)
        h.end_headers()
        return

    # Fetch repo language stats.
    try:
        langs = parallel(
            _repos_list_languages,
            [r.name for r in repos],
            api,
            username,
            n_workers=min(CONCURRENT_REQUESTS_MAX, len(repos)),
            threadpool=True,
        )
    except HTTPError as e:
        h.send_response(e.code, e.msg)
        for k, v in e.hdrs.items():
            h.send_header(k, v)
        h.end_headers()
        h.wfile.write(e.fp.read())
        return
    except Exception as e:
        msg = f"failed to check languages used by the user {username}: {e}\n"
        sys.stderr.write(msg)
        h.send_response(500, msg)
        h.end_headers()
        return

    # Transform into a top 10 ranking.
    langbytes = {}
    for langmap in langs:
        for lang, num_bytes in langmap.items():
            if lang not in langbytes:
                langbytes[lang] = 0
            langbytes[lang] += num_bytes

    langbytes = dict(sorted(langbytes.items(), key=lambda repo: repo[1], reverse=True))
    top10 = [{"language": lang, "bytes": num_bytes} for lang, num_bytes in langbytes.items()][:10]

    # Reply.
    h.send_response(200)
    h.send_header('Content-Type', 'application/json')
    h.end_headers()
    h.wfile.write(json.dumps(top10).encode('UTF-8'))


def _repos_list_languages(api, username, reponame):
    """
    Call the api.repos.list_languages converting 404's into empty dicts.
    It prevents a cascading failure where a 404 for a single query aborts all queries.
    """

    try:
        return fetch(api, api.repos.list_languages, username, reponame)
    except HTTPError as e:
        if e.code == 404:
            return {}
        raise
