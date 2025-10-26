"""Simple WebSocket broadcast server for PyChat.

This server persists messages in SQLite (via aiosqlite) and, when a client
connects, sends recent history before processing incoming messages.

Protocol: clients send JSON like {"sender":"name","text":"hi"}.
Server stores the message, then broadcasts to other clients.
"""
import asyncio
import json
import logging
from typing import Set

import websockets
from websockets.exceptions import ConnectionClosedOK

from .storage import Storage


CONNECTED: Set[websockets.WebSocketServerProtocol] = set()
STORAGE: Storage | None = None


async def handler(ws: websockets.WebSocketServerProtocol, path: str):
    logging.info("Client connected: %s", ws.remote_address)
    CONNECTED.add(ws)

    # On new connection, send recent history
    try:
        if STORAGE is not None:
            try:
                msgs = await STORAGE.get_messages()
                for m in msgs:
                    try:
                        await ws.send(json.dumps(m, ensure_ascii=False))
                    except Exception:
                        # ignore send errors to the new client
                        pass
            except Exception:
                logging.exception("Failed to load/send history")

        async for raw in ws:
            # Accept either raw text or JSON
            try:
                data = json.loads(raw)
            except Exception:
                data = {"sender": "unknown", "text": raw}

            # Persist message
            try:
                if STORAGE is not None:
                    # store with provided timestamp if present
                    ts = data.get("timestamp")
                    attachment = data.get("attachment")
                    await STORAGE.add_message(data.get("sender", "unknown"), data.get("text", ""), timestamp=ts, attachment=attachment)
            except Exception:
                logging.exception("Failed to persist message")

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


async def main_async(host: str = "0.0.0.0", port: int = 8765):
    global STORAGE
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    STORAGE = Storage("server_chat_history.db")
    await STORAGE.init()
    logging.info("Starting PyChat server on %s:%s", host, port)
    async with websockets.serve(handler, host, port):
        await asyncio.Future()  # run forever


def main(host: str = "0.0.0.0", port: int = 8765):
    asyncio.run(main_async(host, port))


if __name__ == "__main__":
    main()
