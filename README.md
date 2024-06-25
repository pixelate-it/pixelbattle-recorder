# Pixel Battle recorder
Utility for recording and playing back event chronologies

## Usage 
1. Install dependencies with `pip install -r requirements.txt`
2. Fill out `config.json` using the instructions below
3. Save the changes, and start script with `py ./src/main.py <record|parse> <input_file> [<output_file>] [-f <fps>] [-x <scale_factor>] [-o]`

## Arguments (record mode)
`<input_file>` - **.db** file with timelapse data (game.db for example)  

## Arguments (parse mode)
`<input_file>` - **.db** file with timelapse data (game.db for example)  
`<output_file>` - **.mp4** or other video format (timelapse.mp4 for example)  
`-f <fps>` - number of fps in video  
`-x <scale_factor>` - how many times should the image size be increased?  
`-o` - add this flag if you want 1 frame = drawn pixel  

## `config.json` form
`initial_image_url` - link to canvas (`/pixels.png`)  
`websocket_uri` - link to websocket (`/pixels/socket`)  
`ffmpeg_path` - path to ffmpeg (you can just use `ffmpeg` as the path in most cases)  
`fps` - fps in which the timelapse will be output using the `parse` command  