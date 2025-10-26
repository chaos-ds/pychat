"""Simple WebSocket broadcast server for PyChat.

Protocol: JSON messages. A client sends a JSON object (e.g. {"sender":"name","text":"hi"}).
The server broadcasts the same JSON to all connected clients except the sender.

Run: python server.py
"""
import asyncio
import json
import logging
from typing import Set

import websockets
from websockets.exceptions import ConnectionClosedOK


CONNECTED: Set[websockets.WebSocketServerProtocol] = set()


async def handler(ws: websockets.WebSocketServerProtocol, path: str):
    logging.info("Client connected: %s", ws.remote_address)
    CONNECTED.add(ws)
    try:
        async for raw in ws:
            # Accept either raw text or JSON
            try:
                data = json.loads(raw)
            except Exception:
                data = {"sender": "unknown", "text": raw}

            # Broadcast to other clients
            await broadcast(data, sender_ws=ws)
    except ConnectionClosedOK:
        pass
    except Exception as e:
        logging.exception("Error in connection: %s", e)
    finally:
        CONNECTED.discard(ws)
        logging.info("Client disconnected: %s", ws.remote_address)


async def broadcast(data: dict, sender_ws: websockets.WebSocketServerProtocol | None = None) -> None:
    payload = json.dumps(data, ensure_ascii=False)
    if not CONNECTED:
        return
    coros = [c.send(payload) for c in CONNECTED if c != sender_ws]
    if not coros:
        return
    results = await asyncio.gather(*coros, return_exceptions=True)
    # Log exceptions
    for r in results:
        if isinstance(r, Exception):
            logging.debug("Broadcast send error: %s", r)


def main(host: str = "0.0.0.0", port: int = 8765):
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    logging.info("Starting PyChat server on %s:%s", host, port)
    start = websockets.serve(handler, host, port)
    loop = asyncio.get_event_loop()
    loop.run_until_complete(start)
    loop.run_forever()


if __name__ == "__main__":
    main()
