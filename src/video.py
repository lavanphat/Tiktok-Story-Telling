from multiprocessing import cpu_count
from time import strptime
from typing import List
from ffmpeg import input, output, overwrite_output, run, probe
from pydub import AudioSegment

class Video:
    def get_info(self, path: str):
        """
        Get information about a video file.

        Args:
            video_path (str): The path to the video file.

        Returns:
            dict: A dictionary containing information about the video file, including width, height, bit rate, and duration.
        """
        info = probe(path)
        video_stream = next(
            (stream for stream in info['streams'] if stream['codec_type'] == 'video'), None)
        audio_stream = next(
            (stream for stream in info['streams'] if stream['codec_type'] == 'audio'), None)
        try:
            duration = float(audio_stream['duration'])
        except Exception:
            print('MP4 default metadata not found')
            duration = (strptime(audio_stream['DURATION'], '%H:%M:%S.%f') - min).total_seconds()
        if video_stream is None:
            return {'path': path, 'duration': duration, 'width': 0, 'height': 0}

        width = int(video_stream['width'])
        height = int(video_stream['height'])
        return {'path': path, 'width': width, 'height': height, 'duration': duration}

    def create_story_telling(self, audio_path: str, background_path: str, subtitle_path: str, filename: str):
        audio = input(audio_path)
        audio_duration = AudioSegment.from_file(audio_path).duration_seconds

        background = input(background_path).video \
            .crop('(in_w-out_w)/2', '(in_h-out_h)/2', 'ih/16*9', 'ih') \
            .filter('scale', '1080', '1920') \
            .filter('subtitles', subtitle_path, force_style='Alignment=10,BorderStyle=7,Outline=2,Blur=15,Fontsize=15,FontName=Lexend Bold')

        # Render video
        video = output(background, audio, t=audio_duration, filename=filename, threads=f"{cpu_count()}")
        video = overwrite_output(video)
        run(video)

    def split_audio(self, video_path: str, start_time: int, end_time: int, output_path: str, speed_up: float = 1.1):
        video_input = input(video_path, ss=start_time, to=end_time)

        # Render audio
        audio = video_input.audio.filter('atempo', speed_up)
        audio_stream = output(audio, filename=output_path)
        audio_stream = overwrite_output(audio_stream)
        run(audio_stream)

    def reup(self, video_path: str, font_path: str, subtitle_path: str, start_time: int, end_time: int, output_path: str, titles: List[str], num_part: str, speed_up: float = 1.1):
        video_input = input(video_path, ss=start_time, to=end_time)

        # Edit video
        audio = video_input.audio.filter('atempo', speed_up)
        video = video_input.video \
                    .setpts(f'(PTS-STARTPTS)/{speed_up}') \
                    .filter('scale', 'iw*1.5', 'ih*1.5') \
                    .crop('(in_w-out_w)/2', '(in_h-out_h)/2', 1080, 'ih') \
                    .filter('pad', 1080, 1920, '(ow-iw)/2', '(oh-ih)/2') \
                    .drawtext(num_part, '(w-tw)/2', 'h-(420/2)', fontfile=font_path, fontcolor='white', fontsize=100)  \
                    .filter('subtitles', subtitle_path, force_style='Alignment=10,BorderStyle=7,Outline=2,Blur=15,Fontsize=15,FontName=Lexend Bold')
    
        fontsize = 75
        padding_top = (1920 - 720 * 1.5)/2
        drawtext_y = (padding_top - fontsize * len(titles)) / 2
        for idx, title in enumerate(titles):
            video = video.drawtext(title, '(w-tw)/2', drawtext_y + fontsize * idx, fontcolor='white', fontsize=fontsize, fontfile=font_path)

        # Render video
        output_stream = output(video, audio, output_path)
        output_stream = overwrite_output(output_stream)
        run(output_stream)

