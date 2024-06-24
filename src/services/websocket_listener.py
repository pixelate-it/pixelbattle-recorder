import asyncio
import websockets

class WebSocketListener:
    def __init__(self, uri, on_message, on_connect):
        self.uri = uri
        self.on_message = on_message
        self.on_connect = on_connect

    async def listen(self):
        while True:
            try:
                async with websockets.connect(self.uri) as websocket:
                    await self.on_connect()
                    async def send_ping():
                        while True:
                            try:
                                await websocket.send('ping')
                            except Exception as e:
                                print(f'Error sending ping: {e}')
                                break
                            await asyncio.sleep(10)

                    ping_task = asyncio.create_task(send_ping())

                    async for message in websocket:
                        await self.on_message(message)

                    ping_task.cancel()
                    await ping_task
            except Exception as e:
                print(f'WebSocket connection error: {e}')
                await asyncio.sleep(5)