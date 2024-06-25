import sqlite3
from PIL import Image, ImageDraw
import io
import subprocess

class TimelapseVideoCreator:
    def __init__(self, ffmpeg_path, initial_canvas_image, db_file, output_video, fps, scale_factor, frame_per_pixel):
        self.initial_canvas_image = initial_canvas_image
        self.ffmpeg_path = ffmpeg_path
        self.db_file = db_file
        self.output_video = output_video
        self.fps = fps
        self.scale_factor = scale_factor
        self.frame_per_pixel = frame_per_pixel

    def create_video(self):
        initial_image = Image.open(self.initial_canvas_image)

        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        cursor.execute("SELECT timestamp, x, y, color FROM changes ORDER BY timestamp")

        try:
            scale_option = f'scale=iw*{self.scale_factor}:ih*{self.scale_factor}:flags=neighbor' if self.scale_factor != 1 else 'null'
            process = subprocess.Popen(
                [self.ffmpeg_path, '-y', '-f', 'image2pipe', '-vcodec', 'png', '-r', str(self.fps), '-i', '-', 
                    '-vf', scale_option, '-vcodec', 'libx264', '-pix_fmt', 'yuv420p', self.output_video],
                stdin=subprocess.PIPE
            )
        except Exception as e:
            print(f"Error starting FFmpeg process: {e}")
            return

        current_image = initial_image.copy()
        draw = ImageDraw.Draw(current_image)
        previous_timestamp = None

        for timestamp, x, y, color in cursor:
            if previous_timestamp is not None and not self.frame_per_pixel:
                frame_duration = (timestamp - previous_timestamp) / 1000
                frame_count = int(frame_duration * self.fps)

                buffer = io.BytesIO()
                current_image.save(buffer, format='PNG')

                for _ in range(frame_count):
                    process.stdin.write(buffer.getvalue())

            draw.point((x, y), fill=color)
            if self.frame_per_pixel:
                buffer = io.BytesIO()
                current_image.save(buffer, format='PNG')
                process.stdin.write(buffer.getvalue())
            previous_timestamp = timestamp

        buffer = io.BytesIO()
        current_image.save(buffer, format='PNG')
        process.stdin.write(buffer.getvalue())

        process.stdin.close()
        process.wait()

        conn.close()