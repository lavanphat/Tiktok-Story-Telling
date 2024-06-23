from os import makedirs
from pytube import YouTube

class PyYoutube:
  def download_video(self, url: str, output_path: str):
    streams = YouTube(url).streams

    video_stream = streams.filter(only_video =True, file_extension='mp4', resolution='720p').first()
    audio_stream = streams.filter(only_audio=True, file_extension='mp4').first()

    title = video_stream.title.replace(' ', '-').lower()
    video_filename = video_stream.download(output_path=output_path, filename=f"{title}.mp4")
    audio_filename = audio_stream.download(output_path=output_path, filename=f"{title}.mp3")

    return video_filename, audio_filename
  