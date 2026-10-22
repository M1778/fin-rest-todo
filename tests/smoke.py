#!/usr/bin/env python3
"""Smoke test for fin-rest-todo: boots the server on a fresh port
(fresh per run — see the SO_REUSEADDR note in src/main.fin) and drives
all 5 routes plus the error contract over real HTTP. Fails loudly.
"""
import http.client
import json
import socket
import subprocess
import sys
import time
import os

passed = 0
failed = 0


def check(name, cond, extra=""):
    global passed, failed
    if cond:
        passed += 1
    else:
        failed += 1
        print(f"FAIL {name} {extra}")


def req(method, path, body=None):
    conn = http.client.HTTPConnection("127.0.0.1", PORT, timeout=5)
    headers = {}
    data = None
    if body is not None:
        data = body if isinstance(body, str) else json.dumps(body)
        headers["Content-Type"] = "application/json"
    conn.request(method, path, body=data, headers=headers)
    resp = conn.getresponse()
    raw = resp.read().decode()
    conn.close()
    try:
        parsed = json.loads(raw) if raw else None
    except json.JSONDecodeError:
        parsed = None
    return resp.status, parsed, raw


def free_port():
    s = socket.socket()
    s.bind(("127.0.0.1", 0))
    port = s.getsockname()[1]
    s.close()
    return port


PORT = free_port()
HERE = os.path.dirname(os.path.abspath(__file__))
BIN = os.path.join(HERE, "..", "fin-rest-todo")
proc = subprocess.Popen([BIN, str(PORT)], stdout=subprocess.PIPE,
                        stderr=subprocess.STDOUT, text=True)
try:
    # Wait for the accept loop (Fin stdout is fully buffered: poll TCP).
    deadline = time.time() + 15
    while True:
        try:
            s = socket.create_connection(("127.0.0.1", PORT), timeout=1)
            s.close()
            break
        except OSError:
            if time.time() > deadline:
                print("server did not come up; output:")
                print(proc.stdout.read() if proc.stdout else "")
                sys.exit(2)
            time.sleep(0.2)
    # NOTE: the probe connection above opens a connection that sends no
    # request; the server's read fails and it replies 400 and moves on.
    # The accept loop survives it (verified by the requests below).

    st, body, _ = req("GET", "/todos")
    check("empty list", st == 200 and body == [], f"got {st} {body}")

    st, body, _ = req("POST", "/todos", {"title": "Buy milk"})
    check("create 1", st == 201 and body == {"id": 1, "title": "Buy milk", "done": False},
          f"got {st} {body}")

    st, body, _ = req("POST", "/todos", {"title": "Read book"})
    check("create 2", st == 201 and body["id"] == 2, f"got {st} {body}")

    st, body, _ = req("GET", "/todos")
    check("list has 2", st == 200 and isinstance(body, list) and len(body) == 2,
          f"got {st} {body}")

    st, body, _ = req("GET", "/todos/1")
    check("get one", st == 200 and body["title"] == "Buy milk", f"got {st} {body}")

    st, body, _ = req("PUT", "/todos/1", {"done": True})
    check("put done", st == 200 and body["done"] is True and body["title"] == "Buy milk",
          f"got {st} {body}")

    st, body, _ = req("PUT", "/todos/1", {"title": "Buy oat milk"})
    check("put title keeps done", st == 200 and body["title"] == "Buy oat milk"
          and body["done"] is True, f"got {st} {body}")

    st, body, _ = req("GET", "/todos/999")
    check("get missing 404", st == 404, f"got {st} {body}")

    st, body, _ = req("POST", "/todos", "{bad json")
    check("bad json 400", st == 400 and body and "error" in body, f"got {st} {body}")

    st, body, _ = req("POST", "/todos", {"title": 123})
    check("bad title type 400", st == 400, f"got {st} {body}")

    st, body, _ = req("POST", "/todos", {})
    check("missing title 400", st == 400, f"got {st} {body}")

    st, body, _ = req("PUT", "/todos/1", {"done": "yes"})
    check("bad done type 400", st == 400, f"got {st} {body}")

    st, body, _ = req("PUT", "/todos/999", {"done": True})
    check("put missing 404", st == 404, f"got {st} {body}")

    st, body, _ = req("DELETE", "/todos/2")
    check("delete", st == 200 and body["id"] == 2, f"got {st} {body}")

    st, body, _ = req("GET", "/todos")
    check("list has 1 after delete", st == 200 and len(body) == 1 and body[0]["id"] == 1,
          f"got {st} {body}")

    st, body, _ = req("GET", "/unknown")
    check("unknown route 404", st == 404, f"got {st} {body}")

    st, body, _ = req("GET", "/todos/abc")
    check("non-numeric id 404", st == 404, f"got {st} {body}")

    st, body, _ = req("POST", "/todos")
    check("empty body 400", st == 400, f"got {st} {body}")

    st, body, _ = req("GET", "/todos?x=1")
    check("query string stripped", st == 200 and len(body) == 1, f"got {st} {body}")

    st, body, _ = req("PUT", "/todos/1", {})
    check("put empty object no-op", st == 200 and body["title"] == "Buy oat milk"
          and body["done"] is True, f"got {st} {body}")

    print(f"fin-rest-todo smoke: {passed} passed, {failed} failed")
    if failed:
        sys.exit(1)
    print("SMOKE OK")
finally:
    proc.terminate()
    try:
        proc.wait(timeout=5)
    except subprocess.TimeoutExpired:
        proc.kill()
