#!/bin/sh
# Demo: boot fin-rest-todo on a fresh port, run a curl session, shut down.
# Usage: sh examples/demo.sh   (run from the repo root)
set -eu
cd "$(dirname "$0")/.."
PORT=$(python3 -c 'import socket; s=socket.socket(); s.bind(("127.0.0.1",0)); print(s.getsockname()[1]); s.close()')
./fin-rest-todo "$PORT" &
SRV=$!
trap 'kill $SRV 2>/dev/null || true' EXIT
sleep 1
echo "== create =="
curl -s -X POST "localhost:$PORT/todos" -d '{"title":"Buy milk"}'; echo
echo "== list =="
curl -s "localhost:$PORT/todos"; echo
echo "== update =="
curl -s -X PUT "localhost:$PORT/todos/1" -d '{"done":true}'; echo
echo "== missing =="
curl -s "localhost:$PORT/todos/999"; echo
echo "== bad json =="
curl -s -X POST "localhost:$PORT/todos" -d '{bad'; echo
echo "== delete =="
curl -s -X DELETE "localhost:$PORT/todos/1"; echo
echo "== list again =="
curl -s "localhost:$PORT/todos"; echo
