import json
import io
import subprocess
from PIL import Image, ImageDraw

class TimelapseVideoCreator:
    def __init__(self, ffmpeg_path, initial_canvas_image, changes_file, output_video, fps=30, scale_factor=1):
        self.initial_canvas_image = initial_canvas_image
        self.changes_file = changes_file
        self.output_video = output_video
        self.fps = fps
        self.scale_factor = scale_factor
        self.ffmpeg_path = ffmpeg_path

    def create_video(self):
        initial_image = Image.open(self.initial_canvas_image)

        with open(self.changes_file, 'r') as f:
            changes = json.load(f)

        try:
            scale_option = f'scale=iw*{self.scale_factor}:ih*{self.scale_factor}' if self.scale_factor != 1 else 'null'
            process = subprocess.Popen(
                [self.ffmpeg_path, '-y', '-f', 'image2pipe', '-vcodec', 'png', '-r', str(self.fps), '-i', '-', 
                    '-vf', scale_option, '-vcodec', 'libx264', '-pix_fmt', 'yuv420p', self.output_video],
                stdin=subprocess.PIPE
            )
        except Exception as e:
            print(f'Error starting FFmpeg process: {e}')
            return

        current_image = initial_image.copy()
        draw = ImageDraw.Draw(current_image)
        timestamps = [change['timestamp'] for change in changes]

        buffer = io.BytesIO()
        current_image.save(buffer, format='PNG')
        process.stdin.write(buffer.getvalue())

        previous_timestamp = timestamps[0]

        for change, timestamp in zip(changes, timestamps):
            self.apply_change(draw, change['change'])
            frame_duration = (timestamp - previous_timestamp) / 1000
            frame_count = int(frame_duration * self.fps)

            buffer = io.BytesIO()
            current_image.save(buffer, format='PNG')

            for _ in range(frame_count):
                process.stdin.write(buffer.getvalue())

            previous_timestamp = timestamp

        process.stdin.close()
        process.wait()

    def apply_change(self, draw, change):
        x, y = change['x'], change['y']
        color = change['color']
        draw.point((x, y), fill=color)