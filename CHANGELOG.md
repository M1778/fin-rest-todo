# Changelog — fin-rest-todo

All notable changes to this app are documented here. Format follows
[Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

## [0.1.0] — 2026-10-21

### Added
- Initial release: REST todo API in Fin (zhttp server + finson JSON).
- 5 routes: `GET /todos`, `POST /todos` (201), `GET /todos/<id>`,
  `PUT /todos/<id>` (partial updates), `DELETE /todos/<id>`
  (returns the deleted todo). In-memory store, cap 1024 todos.
- Error contract: malformed JSON / non-object body / wrongly-typed
  field → 400; unknown route/id → 404; never `blame` on client input.
- Full lifecycle: README (routes + example session), `tests/smoke.py`
  (20 checks over real HTTP, fresh port per run, SMOKE OK), GitHub
  Actions CI, real-format `finn.toml`, MIT license.
- Port from argv[1] via `/proc/self/cmdline` (fin-ssg's recipe);
  default 8080.

### Notes
- PUT validates all fields before mutating anything (no partial
  update on a 400).
- Ids are numeric-only and capped at 9 digits before `parse_int`
  (overflow blame guard on hostile input).
- Same-port restart within ~60s of serving a client fails to bind
  (stdlib SO_REUSEADDR gap, documented in README).
