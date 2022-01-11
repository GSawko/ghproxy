import re
import sys
import json
from http.server import BaseHTTPRequestHandler
from urllib.error import HTTPError
from auth import gh_token
from client import fetch
from ghapi.all import GhApi

ROUTE_RE = re.compile(r'^/users/([^/]+)/stats/popularity$')


def handler(h: BaseHTTPRequestHandler, username: str):
    """
    Return the total number of stars the user has received across all their repositories.
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

    # Count the stars.
    total_stars = sum([repo.stargazers_count for repo in repos])

    # Reply.
    h.send_response(200)
    h.send_header('Content-Type', 'application/json')
    h.end_headers()
    h.wfile.write(json.dumps({"login": username, "total_stars": total_stars}).encode("UTF-8"))
