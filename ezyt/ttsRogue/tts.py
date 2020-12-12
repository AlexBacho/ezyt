import os

from google.cloud import texttospeech
from pathlib import Path

from .languageFilter import get_tts_compatible_version_of_text
from .ttsVoices import GOOGLE_STANDARD_VOICES, GOOGLE_WAVENET_VOICES
from .errors import InvalidParamsError


DEFAULT_MP3_FILENAME_FORMAT = "unnamed{index}.mp3"
UNIVERSAL_LANGUAGE_CODE = "en-US"


class TTS:
    def __init__(self, cfg):
        self.cfg = cfg
        self.voices = {}
        self.working_dir = f"{cfg.common.working_dir_root}/tts"
        self.paid_voices = GOOGLE_WAVENET_VOICES + GOOGLE_STANDARD_VOICES
        self.paid_voices_index = 0
        self.free_voices = []
        self.free_voices_index = 0
        Path(self.working_dir).mkdir(exist_ok=True)

    def get_mp3_from_text(
        self,
        text=None,
        text_path=None,
        mp3_path=None,
        voice_id=None,
        use_paid_tts=False,
    ):

        if not text:
            if not text_path:
                raise InvalidParamsError("No text or textpath specified.")
            text = self._read_file_and_replace_profanities(text_path)
        else:
            text = self._get_tts_compatible_text(text)

        if not mp3_path:
            mp3_path = self._next_path()

        if use_paid_tts:
            self._create_paid_tts(text, mp3_path, voice_id)
        else:
            self._create_free_tts()

        return mp3_path

    def _create_free_tts(self):
        # TODO: neplatene tts cez lokalny encoding
        raise NotImplementedError

    def _create_paid_tts(self, text, mp3_path, voice_id=None):
        client = texttospeech.TextToSpeechClient()
        synthesis_input = texttospeech.SynthesisInput(text=text)
        voice = self._get_voice_from_id(voice_id, use_paid_voices=True)
        audio_config = texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.MP3
        )
        response = client.synthesize_speech(
            input=synthesis_input, voice=voice, audio_config=audio_config
        )
        with open(mp3_path, "wb") as out:
            out.write(response.audio_content)

    def _read_file_and_replace_profanities(self, filename):
        with open(filename, "r") as f:
            return self._get_tts_compatible_text(f.read())

    def _get_tts_compatible_text(self, text):
        # TODO: cenzurujeme dynamicky, silna cenzura staci na nadpis, thumbnail a prvych 30s videa
        censorship_level = self.cfg.tts.get("censorship_level", 3)
        return get_tts_compatible_version_of_text(text, filter_level=censorship_level)

    def _get_voice_from_id(self, voice_id, use_paid_voices=False):
        if voice_id and voice_id in self.voices:
            return self.voices[voice_id]

        if use_paid_voices:
            voice_name = self.paid_voices[self.paid_voices_index]
            voice = texttospeech.VoiceSelectionParams(
                language_code=UNIVERSAL_LANGUAGE_CODE,
                ssml_gender=texttospeech.SsmlVoiceGender.NEUTRAL,
                name=voice_name,
            )
            self.paid_voices_index = _round_robin(
                self.paid_voices_index, self.paid_voices
            )
            self.voices[voice_id] = voice
            return voice
        voice = self.free_voices[self.free_voices_index]
        self.free_voices_index = _round_robin(self.free_voices_index, self.free_voices)
        self.voices[voice_id] = voice
        return voice

    def _next_path(self, working_dir=None):
        working_dir = working_dir or self.working_dir
        i = 0
        while os.path.exists(f"{working_dir}/{DEFAULT_MP3_FILENAME_FORMAT.format(i)}"):
            i += 1
        return f"{working_dir}/{DEFAULT_MP3_FILENAME_FORMAT.format(i)}"


def _round_robin(index, array):
    return index + 1 if index < len(array) - 1 else 0
