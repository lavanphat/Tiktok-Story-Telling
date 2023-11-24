from os import makedirs, remove
from src.logger import Logger
from src.video import Video
from src.youtube import PyYoutube
from pathlib import Path
from argparse import ArgumentParser
from ffmpeg import input, run, output, overwrite_output
from PIL import ImageFont


def text_wrap(text, max_width):
    lines = []
    font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 75)
    max_width -= 10
    # If the width of the text is smaller than image width
    # we don't need to split it, just add it to the lines array
    # and return
    if font.getbbox(text)[2] <= max_width:
        lines.append(text)
    else:
        # split the line by spaces to get words
        words = text.split(' ')
        i = 0
        # append every word to a line while its width is shorter than image width
        while i < len(words):
            line = ''
            while i < len(words) and font.getbbox(line + words[i])[2] <= max_width:
                line = line + words[i] + " "
                i += 1
            if not line:
                line = words[i]
                i += 1
            # when the line gets longer than the max width do not append the word,
            # add the line to the lines array
            lines.append(line)
    return lines

def main():
    parser = ArgumentParser()
    parser.add_argument("--url", required=True, help="Youtube URL to download video.", type=str)
    parser.add_argument("--num_parts", required=True, help="Number parts.", type=int)
    parser.add_argument("--title", required=True, help="Number parts.", type=str)
    args = parser.parse_args()

    # Init tool
    log = Logger()
    HOME = Path.cwd()
    log.info("Tiktok reup is running...")
    
    output_dir = f"{HOME}/output"
    makedirs(output_dir, exist_ok=True)

    # Wrap video title
    video_title_wrap = text_wrap(args.title, 1080)
    log.info("Wrap text success")

    # Download video
    py_youtube = PyYoutube()
    log.info(f"Downloading video")
    video_path = py_youtube.download_video(args.url, f"{HOME}/background")
    log.info(f"Downloaded video")

    # Render video
    video = Video()
    video_info = video.get_info(video_path)
    duration = video_info['duration']
    part_duration = duration / args.num_parts

    for i in range(args.num_parts):
        log.info(f"Rendering part {i+1}")

        start_time = i * part_duration
        end_time = min((i + 1) * part_duration, duration)
        video_input = input(video_path, ss=start_time, to=end_time)

        # Edit video
        audio = video_input.audio.filter('atempo', 1.1)
        video = video_input.video \
                    .setpts('(PTS-STARTPTS)/1.1') \
                    .filter('scale', 'iw*1.5', 'ih*1.5') \
                    .crop('(in_w-out_w)/2', '(in_h-out_h)/2', 1080, 'ih') \
                    .filter('pad', 1080, 1920, '(ow-iw)/2', '(oh-ih)/2') \
                    .drawtext(f"Part {i+1}", '(w-tw)/2', 'h-(420/2)', fontcolor='white', fontsize=100)
        
        fontsize = 75
        padding_top = (1920 - 720 * 1.5)/2
        drawtext_y = (padding_top - fontsize * len(video_title_wrap)) / 2
        for idx, title in enumerate(video_title_wrap):
            video = video.drawtext(title, '(w-tw)/2', drawtext_y + fontsize * idx, fontcolor='white', fontsize=fontsize, line_spacing=10)

        # Render video
        output_name = f"{output_dir}/{args.title} part {i + 1}.mp4"
        output_stream = output(video, audio, output_name)
        output_stream = overwrite_output(output_stream)
        run(output_stream)

    # Remove resources files
    remove(video_path)


if __name__ == "__main__":
    main()