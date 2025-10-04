import asyncio
import websockets


async def test_ws():
    uri = "ws://localhost:8082/ws"
    async with websockets.connect(uri) as websocket:
        print("Connected to WebSocket")

        # kirim pesan ke server
        await websocket.send("Hello from Python client!")

        # terima pesan dari server
        while True:
            msg = await websocket.recv()
            print("Message from server:", msg)

asyncio.run(test_ws())
