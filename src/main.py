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
                change = { 
                    'x': data['x'], 
                    'y': data['y'], 
                    'color': data['color'] 
                }
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

    recorder.close()

def parse(input_file, output_file, fps, scale_factor, frame_per_pixel):
    initial_image = input_file.replace('.db', '_initial.png')
    ffmpeg_path = Configuration('config.json').get('ffmpeg_path', 'ffmpeg')

    video_creator = TimelapseVideoCreator(ffmpeg_path, initial_image, input_file, output_file, fps, scale_factor, frame_per_pixel)
    video_creator.create_video()

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print('Usage: py main.py <record|parse> <input_file> [<output_file>] [-f <fps>] [-x <scale_factor>] [-o]')
        sys.exit(1)

    mode = sys.argv[1]
    input_file = sys.argv[2]
    scale_factor = 1
    frame_per_pixel = False
    fps = 30

    if mode == 'record':
        asyncio.run(record(input_file))
    elif mode == 'parse':
        if len(sys.argv) < 4:
            print('Usage: py main.py parse <input_file> <output_file> [-f <fps>] [-x <scale_factor>] [-o]')
            sys.exit(1)

        output_file = sys.argv[3]

        if '-f' in sys.argv:
            fps_index = sys.argv.index('-f') + 1
            if fps_index < len(sys.argv):
                fps = int(sys.argv[fps_index])

        if '-x' in sys.argv:
            scale_factor_index = sys.argv.index('-x') + 1
            if scale_factor_index < len(sys.argv):
                scale_factor = int(sys.argv[scale_factor_index])

        if '-o' in sys.argv:
            frame_per_pixel = True

        parse(input_file, output_file, fps, scale_factor, frame_per_pixel)
    else:
        print('Unknown mode:', mode)
        print('Usage: py main.py <record|parse> <input_file> [<output_file>] [-f <fps>] [-x <scale_factor>] [-o]')
        sys.exit(1)