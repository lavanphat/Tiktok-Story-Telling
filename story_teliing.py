from argparse import ArgumentParser
from asyncio import get_event_loop
from pathlib import Path
from sys import exit
from src.reddit import Reddit
from src.console import Console
from src.tts import EdgeTTS
from src.openai_whisper import Whisper
from src.youtube import PyYoutube
from src.video import Video
from os import makedirs, remove
from pydub import AudioSegment
from nltk import download, sent_tokenize


async def main():
    console.info("Tiktok Story Telling is running...")
    output_dir = f"{HOME}/output"
    makedirs(output_dir, exist_ok=True)

    parser = ArgumentParser()
    parser.add_argument("--model", default="small", help="Model to use", choices=["tiny", "base", "small", "medium", "large"], type=str)
    # parser.add_argument("--non_english", action='store_true', help="Don't use the english model.")
    parser.add_argument("--url", default="https://www.youtube.com/watch?v=FvSqM5EKEeg", help="Youtube URL to download as background video.", type=str)
    parser.add_argument("--list-voices", help="Use `edge-tts --list-voices` to list all voices", action='help')
    # parser.add_argument("--tts", default="en-US-ChristopherNeural", help="Voice to use for TTS", type=str)
    # parser.add_argument("--random_voice", action='store_true', help="Random voice for TTS", default=False)
    # parser.add_argument("--gender", choices=["Male", "Female"], help="Gender of the random TTS voice", type=str)
    # parser.add_argument("--language", help="Language of the random TTS voice for example: en-US", type=str)
    args = parser.parse_args()

    # Random voice
    edge_tts = EdgeTTS()
    voice = await edge_tts.random_voices()
    console.success(f"Choice voice {voice}")
    
    # Scrape posts from Reddit
    reddit = Reddit()
    posts = reddit.get_post('relationships')

    post = None
    # Filter post
    for item in posts:
        # Convert content post to tts
        console.info(f"Checking post {item['title']}")
        content_path = await edge_tts.tts(item['selftext'], f"{output_dir}/temp.mp3")
        
        # Skip if content audio < 60 seconds
        content_audio = AudioSegment.from_file(content_path)
        remove(content_path)
        if content_audio.duration_seconds < 60:
            console.info(f"Skip this post")
            continue
        
        console.success(f"Choice this post with audio time {content_audio.duration_seconds}")
        post = item
        break
    
    # Split to n part
    audio_limit = content_audio.duration_seconds
    if audio_limit >= 180:  audio_limit /= 3
    elif audio_limit >= 120:    audio_limit /= 2
    
    # Create sentences from content
    download('punkt', quiet=True)
    sentences = sent_tokenize(post['selftext'])
    console.success(f"Splited content to sentences")

    # Create folder output for this post
    post_dir = f"{output_dir}/{post['title'].replace(' ', '_').lower()}"
    makedirs(post_dir, exist_ok=True)
    console.success(f"Created folder output for this post")

    # OpenAI-Whisper Model
    whisper = Whisper(args.model)
    console.success(f"OpenAI-Whisper model loaded successfully ({args.model})")

    # Create audio and subtitle for post from sentences
    combined_audio = AudioSegment.empty()
    audio_paths = []
    for idx, sentence in enumerate(sentences):
        sentence_path = f"{post_dir}/{idx}.mp3"
        sentence_path = await edge_tts.tts(sentence, sentence_path)
        
        sentence_audio = AudioSegment.from_file(sentence_path)
        remove(sentence_path)

        combined_audio += sentence_audio
        if combined_audio.duration_seconds < audio_limit:
            continue

        # Create title audio
        title_path = f"{post_dir}/title-part-{len(audio_paths)+1}.mp3"
        title_path = await edge_tts.tts(f"{post['title']}\nPart{len(audio_paths)+1}\n", title_path)

        # Create content audio
        combined_audio = AudioSegment.from_file(title_path) + combined_audio
        audio_path = f"{post_dir}/audio-part-{len(audio_paths)+1}.mp3"
        combined_audio.export(audio_path)
        console.success(f"Created audio for part {len(audio_paths)+1}")

        # Create subtitles for content audio
        whisper.srt_create(audio_path, post_dir)
        subtitle_path = audio_path.replace('mp3', 'srt')

        audio_paths.append({'audio_path': audio_path, 'subtitle_path': subtitle_path})
        combined_audio = AudioSegment.empty()  
        remove(title_path)              

    # if combined_audio.duration_seconds > 0:
    #     console.info(f"Created audio for part backup")
    #     combined_audio.export(f"{post_dir}/audio-part-backup.mp3")

    #     videos[-1]['text'] += text
    
    console.success(f"Created audio and subtitle successfully!")
    
    # Download background
    py_youtube = PyYoutube()
    background_path = py_youtube.download_video(args.url, f"{HOME}/background")
    console.success(f"Downloaded background")
    
    # Create videos
    video = Video()
    for idx, audio in enumerate(audio_paths):
        output_file = f"{post_dir}/{post['title']} part {idx+1}.mp4"
        video.create_story_telling(
            audio['audio_path'], 
            background_path, 
            audio['subtitle_path'],
            output_file
        )

if __name__ == "__main__":
    # if system() == 'Windows':
    #     set_event_loop_policy(WindowsSelectorEventLoopPolicy())

    loop = get_event_loop()
    console = Console()
    HOME = Path.cwd()
    try:
        loop.run_until_complete(main())
    except Exception as e:
        loop.close()
        console.error(e)
    finally:
        loop.close()

    exit(0)