from pytubefix import YouTube
from requests import get

class PyYoutube:
  def __init__(self, url: str) -> None:
    self.yt = YouTube(url)

  def download_video(self, output_path: str) -> tuple[str, str, str]:
    streams = self.yt.streams

    # Download video
    video_stream = streams.filter(only_video =True, file_extension='mp4', resolution='720p').first()
    title = video_stream.title.replace(' ', '-').lower()
    video_filename = video_stream.download(output_path=output_path, filename=f"{title}.mp4")

    # Download audio
    audio_stream = streams.filter(only_audio=True, file_extension='mp4').first()
    audio_filename = audio_stream.download(output_path=output_path, filename=f"{title}.mp3")

    # Download thumbnail
    video_details = self.yt.vid_info['videoDetails']
    response = get(f"https://img.youtube.com/vi/{video_details['videoId']}/maxresdefault.jpg")
    thumbnail_filename = f"{output_path}/{title}.jpg"
    with open(thumbnail_filename, 'wb') as file:
      file.write(response.content)

    return video_filename, audio_filename, thumbnail_filename
