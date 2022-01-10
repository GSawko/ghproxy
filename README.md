# About

This server demonstrates how to emulate GitHub's REST API.
It implements handlers for a few custom extension methods (see [REST API](#rest-api)) and proxies all other requests
to the official [api.github.com](https://api.github.com) API.

# Running

With docker:

    docker build -t gsawko-ghproxy .
    docker run -t -p 8080:8080 gsawko-ghproxy

Without docker:

    python3 -m pip install -r requirements.txt
    python3 main.py

The server listens on `0.0.0.0:8080` by default (use `--addr` and `--port` to override).

# REST API

You may pass the `-H 'Authorization: token ${GITHUB_TOKEN}` personal token to avoid hitting GitHub's hourly rate limits.

## curl http://127.0.0.1:8080/users/${username}/stats/languages

Returns the top 10 languages used by the given user ranked by the number of bytes of source code.

    Status: 200 OK

    [
      {
        "language": "Java",
        "bytes": 2131623
      },
      {
        "language": "Python",
        "bytes": 725330
      }
    ]

## curl http://127.0.0.1:8080/users/${username}/stats/popularity

Returns the total number of stars the user has received across all repositories.

  Status: 200 OK

  [
    {
      "login": "gsawko",
      "total_stars": 15000
    }
  ]

## curl http://127.0.0.1:8080/users/${username}/stats/populairty_by_repo

Returns the user repositories, sorted descending by the count of stargazers.

  Status: 200 OK

  [
    {
      "login": "gsawko",
      "repository": "pie",
      "stargazers_count": 10000
    },
    {
      "login": "gsawko",
      "repository": "ton",
      "stargazers_count": 5000
    }
  ]

# Not implemented

- unit tests
- faithful emulation of api.github.com (e.g. rate limiting, paging)
- http tcp connection pooling
- caching
- clean error handling (too much boilerplate code)
- proxying of PUTs / POSTs
