from whisper import load_model, utils
from torch import cuda

class Whisper:
    def __init__(self, model: str) -> None:
        if model != "large":
            model = model + ".en"
        self.model = load_model(model)

    def srt_create(self, audio_path: str, output_dir: str):
        """
        Create an SRT file for a given video file using the specified model.

        Args:
            audio_path (str): The path of audio file.
            output_dir (str): The path of ouput dir.

        Returns:
            bool: True if the SRT file was created successfully, False otherwise.
        """
        word_options = {
            "highlight_words": True,
            "max_line_count": 1,
            "max_line_width": 10,
            "preserve_segments": False,
        }

        transcribe = self.model.transcribe(
            audio_path, 
            task="transcribe", 
            word_timestamps=True, 
            fp16=cuda.is_available()
        )
        vtt_writer = utils.get_writer(output_format="srt", output_dir=output_dir)
        vtt_writer(transcribe, audio_path, word_options)

# Whisper('small').srt_create('output/husband_resents_me_for_having_kids/audio-part-1.mp3','')