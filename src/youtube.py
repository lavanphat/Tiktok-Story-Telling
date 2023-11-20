from os import makedirs
from pytube import YouTube

class PyYoutube:
  def download_video(self, url: str, output_path: str):
    video = YouTube(url).streams.get_highest_resolution()

    title = video.title.replace(' ', '-').lower()
    filename = f"{title}.mp4"

    makedirs(output_path, exist_ok=True)
    video.download(output_path=output_path, filename=filename)

    return f"{output_path}/{filename}"
  