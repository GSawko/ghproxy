#!/usr/bin/env python3

import argparse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from handlers import users_languages, users_popularity_by_repo, users_popularity, proxy
from client import call_synced


DESCRIPTION = """
A proxy server that wraps the api.github.com API, adding custom methods.

The GH_HOST environment variable may be used to override https://api.github.com
with a custom base API address.
"""


class HandleOrProxy(BaseHTTPRequestHandler):
    """
    HandleOrProxy dispatches the incoming request to a local handler if one exists,
    or falls back on proxying to api.github.com otherwise.
    """

    def do_GET(self):
        routes = {
            users_languages.ROUTE_RE:          users_languages.handler,
            users_popularity_by_repo.ROUTE_RE: users_popularity_by_repo.handler,
            users_popularity.ROUTE_RE:         users_popularity.handler,
        }

        # Look for a local handler.
        for path_re, handler_fn in routes.items():
            match = path_re.match(self.path)
            if match:
                handler_fn(self, *match.groups())
                return

        # Not handled locally. Let the remote api.github.com handle it.
        call_synced(proxy.handler, self)


def main():
    parser = argparse.ArgumentParser(description=DESCRIPTION)
    parser.add_argument('--addr', help='Listen address', default='0.0.0.0')
    parser.add_argument('--port', type=int, help='Listen port', default=8080)
    args = parser.parse_args()

    server = ThreadingHTTPServer((args.addr, args.port), HandleOrProxy)
    print(f"Listening on http://{args.addr}:{args.port}")
    server.serve_forever()


if __name__ == '__main__':
    main()