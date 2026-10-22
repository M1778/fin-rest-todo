# fin-rest-todo

A REST todo API in [Fin](https://github.com/M1778/Fin) — the "Fin can
serve real web traffic" demo. In-memory store, JSON bodies, proper
status codes. Built on [zhttp](https://github.com/M1778/zhttp) (HTTP
server) and [finson](https://github.com/M1778/finson) (JSON).

## Routes

| Method | Path | Success | Notes |
|---|---|---|---|
| GET | `/todos` | 200 `[todo, ...]` | |
| POST | `/todos` | 201 `todo` | body `{"title": "..."}` |
| GET | `/todos/<id>` | 200 `todo` | else 404 |
| PUT | `/todos/<id>` | 200 `todo` | body `{"title"?, "done"?}`, else 404 |
| DELETE | `/todos/<id>` | 200 deleted `todo` | else 404 |
| anything else | | 404 `{"error": ...}` | |

Todo shape: `{"id": 1, "title": "Buy milk", "done": false}`.

Error contract: malformed JSON, a non-object body, or a wrongly-typed
field → 400 `{"error": "..."}`. The server never aborts on client
input — every request gets a response.

## Build & run

```sh
# finson and zhttp checkouts are needed on the search path:
finc -I <finson>/src -I <zhttp>/src src/main.fin -o fin-rest-todo
./fin-rest-todo [port]          # default port 8080
```

## Example session

```sh
$ ./fin-rest-todo 8080 &
$ curl -s -X POST localhost:8080/todos -d '{"title":"Buy milk"}'
{"id":1,"title":"Buy milk","done":false}
$ curl -s localhost:8080/todos
[{"id":1,"title":"Buy milk","done":false}]
$ curl -s -X PUT localhost:8080/todos/1 -d '{"done":true}'
{"id":1,"title":"Buy milk","done":true}
$ curl -s -X DELETE localhost:8080/todos/1
{"id":1,"title":"Buy milk","done":true}
$ curl -s localhost:8080/todos
[]
```

## Tests

```sh
python3 tests/smoke.py   # 20 checks over real HTTP, fresh port per run
```

## Notes & limits

- Single-threaded accept loop; in-memory store (cap 1024 todos), no
  persistence — restart wipes the list.
- Known stdlib caveat: `Socket::serve` lacks SO_REUSEADDR, so
  restarting on the SAME port within ~60s of serving a client fails to
  bind. The smoke test uses a fresh port per run to dodge it.
- Port is argv[1] via `/proc/self/cmdline` (Linux-only, fin-ssg's recipe).
- Ids are numeric only (`/todos/abc` → 404); a >9-digit id is rejected
  before `parse_int` to dodge its overflow blame on hostile input.

## License

MIT — see [LICENSE](LICENSE).
