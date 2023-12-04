from os import makedirs, remove
from src.logger import Logger
from src.video import Video
from src.youtube import PyYoutube
from src.font import Font
from src.openai_whisper import Whisper
from pathlib import Path
from argparse import ArgumentParser
from ffmpeg import input, run, output, overwrite_output
from PIL import ImageFont


def text_wrap(text: str, max_width: int, font: str):
    lines = []
    font = ImageFont.truetype(font, 75)
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
    parser.add_argument("--font_url", default='https://www.dafontfree.net/data/36/t/128322/typewriter-serial-heavy-regular.ttf', help="URL font will download.", type=str)
    parser.add_argument("--num_parts", required=True, help="Number parts.", type=int)
    parser.add_argument("--title", required=True, help="Number parts.", type=str)
    args = parser.parse_args()

    # Init tool
    log = Logger()
    HOME = Path.cwd()
    log.info("Tiktok reup is running...")
    
    output_dir = f"{HOME}/output"
    makedirs(output_dir, exist_ok=True)
    
    # Download font
    font = Font()
    font_path = font.download(args.font_url, f"{HOME}/fonts")
    log.info("Download font success")

    # Wrap video title
    video_title_wrap = text_wrap(args.title, 1080, font_path)
    log.info("Wrap text success")

    # OpenAI-Whisper Model
    whisper = Whisper('small')
    log.info(f"OpenAI-Whisper model loaded successfully (small)")

    # Download video
    py_youtube = PyYoutube()
    log.info(f"Downloading video")
    video_path = py_youtube.download_video(args.url, f"{HOME}/backgrounds")
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

        # Split audio from video
        audio_path = f"{output_dir}/audio.mp3"
        video.split_audio(video_path, start_time, end_time, audio_path)
        
        # Create subtitles for content audio
        whisper.srt_create(audio_path, output_dir)
        subtitle_path = audio_path.replace('mp3', 'srt')
        whisper.format_subtitle(subtitle_path)

        # Edit video
        output_path = f"{output_dir}/{args.title} part {i + 1}.mp4"
        video.reup(
            video_path,
            font_path,
            subtitle_path,
            start_time,
            end_time,
            output_path,
            video_title_wrap,
            f"Part {i + 1}"
        )

    # Remove resources files
    remove(video_path)

if __name__ == "__main__":
    main()