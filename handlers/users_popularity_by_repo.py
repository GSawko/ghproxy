import re
import sys
import json
from http.server import BaseHTTPRequestHandler
from urllib.error import HTTPError
from auth import gh_token
from client import fetch
from ghapi.all import GhApi

ROUTE_RE = re.compile(r'^/users/([^/]+)/stats/popularity_by_repo$')


def handler(h: BaseHTTPRequestHandler, username: str):
    """
    Return the user repositories, sorted descending by the count of stargazers.
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

    # Transform and sort.
    items = [{'login': username, 'repository': repo.name, 'stargazers_count': repo.stargazers_count} for repo in repos]
    items.sort(key=lambda repo: repo["stargazers_count"], reverse=True)

    # Reply.
    h.send_response(200)
    h.send_header('Content-Type', 'application/json')
    h.end_headers()
    h.wfile.write(json.dumps(items).encode("UTF-8"))
