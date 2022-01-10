import http.client
from http.server import BaseHTTPRequestHandler
from urllib.parse import urlparse
from ghapi.all import GH_HOST

def handler(h: BaseHTTPRequestHandler):
    """
    Forward the request to api.github.com and pass the response to the caller.
    """

    host = urlparse(GH_HOST).hostname
    conn = http.client.HTTPSConnection(host)
    h.headers.replace_header('Host', host)
    h.headers['X-Forwarded-For'] = h.client_address[0]
    conn.request("GET", h.path, headers=h.headers)
    resp = conn.getresponse()
    h.send_response(resp.getcode())
    for name, val in resp.getheaders():
        h.send_header(name, val)
    h.end_headers()
    h.wfile.write(resp.read())

