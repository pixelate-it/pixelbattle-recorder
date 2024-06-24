import asyncio
import websockets
import json

class WebSocketListener:
    def __init__(self, uri, on_message, on_connect, ping_interval=10):
        self.uri = uri
        self.on_message = on_message
        self.on_connect = on_connect
        self.ping_interval = ping_interval

    async def listen(self):
        while True:
            try:
                async with websockets.connect(self.uri) as websocket:
                    await self.on_connect()

                    async def send_keepalive():
                        while True:
                            try:
                                await websocket.send(json.dumps({ "op": "keepalive" }))
                            except Exception as e:
                                print(f"Error sending keepalive message: {e}")
                                break
                            await asyncio.sleep(self.ping_interval)

                    keepalive_task = asyncio.create_task(send_keepalive())

                    async for message in websocket:
                        await self.on_message(message)

                    keepalive_task.cancel()
                    await keepalive_task
            except Exception as e:
                print(f"WebSocket connection error: {e}")
                await asyncio.sleep(5)