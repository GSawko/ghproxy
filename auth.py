from http.client import HTTPMessage

def gh_token(hdr: HTTPMessage):
    """
    Returns the github token contained in the given header, or None if absent.
    """

    val = hdr.get('Authorization')
    if val and val.startswith('token '):
        return val[len('token '):]
    return None
