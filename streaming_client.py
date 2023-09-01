import asyncio
from websockets.sync.client import connect

websocket_addr = ""

async def send_prompt():
    with connect(f"ws://{websocket_addr}") as websocket:
        websocket.send("What is the meaning of life?\n")
        while True:
            message = await websocket.recv()
            print(message)


