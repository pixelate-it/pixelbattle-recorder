import json
import time
import requests
import io
from PIL import Image, ImageDraw

class CanvasRecorder:
    def __init__(self, initial_image_url, output_file):
        self.initial_image_url = initial_image_url
        self.output_file = output_file
        self.changes = []
        self.load_initial_image()

    def load_initial_image(self):
        response = requests.get(self.initial_image_url)
        self.canvas = Image.open(io.BytesIO(response.content))
        self.draw = ImageDraw.Draw(self.canvas)
        
        initial_image_output = self.output_file.replace('.json', '_initial.png')
        self.canvas.save(initial_image_output)

    def record_change(self, change):
        timestamp = time.time() * 1000
        self.changes.append({ 'timestamp': timestamp, 'change': change })
        self.apply_change(change)
        self.save_changes()

    def apply_change(self, change):
        x, y = change['x'], change['y']
        color = change['color']
        self.draw.point((x, y), fill=color)

    def save_changes(self):
        with open(self.output_file, 'w') as file:
            json.dump(self.changes, file, indent=2)

    def get_current_frame(self):
        buffer = io.BytesIO()
        self.canvas.save(buffer, format='PNG')
        return buffer.getvalue()