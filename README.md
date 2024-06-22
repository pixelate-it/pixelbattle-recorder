# Pixel Battle recorder
Utility for recording and playing back event chronologies

## Usage 
1. Install dependencies with `pip install -r requirements.txt`
2. Fill out `config.json` using the instructions below
3. Save the changes, and start script with `py ./src/main.py <record|parse> <input_file> [<output_file>] [-x <scale_factor>]`

## `config.json` form
`initial_image_url` - link to canvas (`/pixels.png`)  
`websocket_uri` - link to websocket (`/pixels/socket`)  
`ffmpeg_path` - path to ffmpeg (you can just use `ffmpeg` as the path in most cases)  
`fps` - fps in which the timelapse will be output using the `parse` command  