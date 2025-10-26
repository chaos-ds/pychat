"""Minimal example client to connect to the PyChat WebSocket server.

Usage:
  python client_example.py --send "hello"
  python client_example.py

This script connects, optionally sends a JSON message, and prints incoming messages.
"""
import asyncio
import json
import argparse

import websockets


async def run(uri: str, send_text: str | None):
    async with websockets.connect(uri) as ws:
        if send_text:
            obj = {"sender": "cli", "text": send_text}
            await ws.send(json.dumps(obj, ensure_ascii=False))
        print('Connected to', uri)
        try:
            async for msg in ws:
                try:
                    data = json.loads(msg)
                except Exception:
                    data = {"text": msg}
                print('RECV>', data)
        except Exception:
            pass


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--uri", default="ws://localhost:8765")
    p.add_argument("--send", default=None)
    args = p.parse_args()
    asyncio.run(run(args.uri, args.send))


if __name__ == "__main__":
    main()
