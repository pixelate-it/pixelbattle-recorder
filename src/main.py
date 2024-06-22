import asyncio
import sys
import json
from utils.conf import Configuration
from services.websocket_listener import WebSocketListener
from services.canvas_recorder import CanvasRecorder
from services.video_creator import TimelapseVideoCreator

async def record(output_file):
    config = Configuration('config.json')

    initial_image_url = config.get('initial_image_url')
    websocket_uri = config.get('websocket_uri')

    recorder = CanvasRecorder(initial_image_url, output_file)

    async def on_message(message):
        try:
            data = json.loads(message)
            if 'x' in data and 'y' in data and 'color' in data:
                change = {'x': data['x'], 'y': data['y'], 'color': data['color']}
                recorder.record_change(change)
            else:
                print(f'Ignoring unexpected message format: {data}')
        except json.JSONDecodeError as e:
            print(f'Error decoding JSON: {e}')
        except Exception as e:
            print(f'Error processing message: {e}')

    async def on_connect():
        recorder.load_initial_image()

    listener = WebSocketListener(websocket_uri, on_message, on_connect)
    await listener.listen()

def parse(ffmpeg_path, input_file, output_file, fps, scale_factor=1):
    initial_image = input_file.replace('.json', '_initial.png')
    
    video_creator = TimelapseVideoCreator(ffmpeg_path, initial_image, input_file, output_file, fps, scale_factor)
    video_creator.create_video()

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print('Usage: py main.py <record|parse> <input_file> [<output_file>] [-x <scale_factor>]')
        sys.exit(1)
    
    mode = sys.argv[1]
    input_file = sys.argv[2]
    scale_factor = 1

    if mode == 'record':
        asyncio.run(record(input_file))
    elif mode == 'parse':
        if len(sys.argv) < 4:
            print('Usage: py main.py parse <input_file> <output_file> [-x <scale_factor>]')
            sys.exit(1)
        output_file = sys.argv[3]
        if '-x' in sys.argv:
            scale_factor_index = sys.argv.index('-x') + 1
            if scale_factor_index < len(sys.argv):
                scale_factor = int(sys.argv[scale_factor_index])
        config = Configuration('config.json')
        fps = config.get('fps', 30)
        ffmpeg_path = config.get('ffmpeg_path')
        parse(ffmpeg_path, input_file, output_file, fps, scale_factor)
    else:
        print('Unknown mode:', mode)
        print('Usage: py main.py <record|parse> <input_file> [<output_file>] [-x <scale_factor>]')
        sys.exit(1)