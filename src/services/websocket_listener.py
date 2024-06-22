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
                    while True:
                        message = await websocket.recv()
                        await self.on_message(message)
            except Exception as e:
                print(f'WebSocket connection error: {e}')
                await asyncio.sleep(5)