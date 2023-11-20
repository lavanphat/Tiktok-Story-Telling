from random import choice
from edge_tts import Communicate, VoicesManager


class EdgeTTS:
    def __init__(self):
        pass

    async def random_voices(self, language: str = 'en-US'):
        voices = await VoicesManager.create()
        voices = voices.find(Locale=language)
        if len(voices) == 0:
            # Voice not found
            raise Exception("Specified TTS language not found. Make sure you are using the correct format. For example: en-US")

        self.voice = choice(voices)['ShortName']
        return self.voice

    async def tts(self, text: str, outfile: str = "tts.mp3") -> bool:
        """
        Converts text to speech using Microsoft Edge Text-to-Speech API.

        Args:
            text (str): The text to be converted to speech.
            outfile (str, optional): The name of the output file. Defaults to "tts.mp3".

        Returns:
            outfile: Path audio.
        """
        communicate = Communicate(text, self.voice)
        await communicate.save(outfile)

        return outfile