import os

from moviepy.editor import (
    AudioFileClip,
    ImageClip,
    VideoFileClip,
    concatenate_videoclips,
)
from pathlib import Path
from itertools import chain

from ezyt.base.utils import run_subprocess

DEFAULT_IMAGE_VIDEO_FPS = 5
COLOR_WHITE = (255, 255, 255)
COLOR_BACKGROUND_SIZE = None
DEFAULT_VIDEO_PADDING = 0.2
VIDEO_CONCAT_METHOD = "compose"
DEFAULT_IMAGEVIDEO_FPS = 30
CONCAT_FILE_NAME = "tmp_concat.txt"


class VideoEditor:
    def __init__(self, cfg=None):
        self.cfg = cfg

    def add_audio_to_image(self, image_path, audio_path, output_path, fps=None):
        audio = AudioFileClip(audio_path)
        video = (
            ImageClip(image_path)
            .on_color(size=COLOR_BACKGROUND_SIZE, color=COLOR_WHITE)
            .set_pos((0.5, 0.5), relative=True)
            .set_audio(audio)
            .set_duration(audio.duration)
            .set_fps(
                fps or self.cfg.video.get("image_video_fps", DEFAULT_IMAGEVIDEO_FPS)
            )
            .audio_fadein(0.1)
            .audio_fadeout(0.1)
        )
        video.write_videofile(
            output_path,
        )
        return output_path

    def concat_videos_complex(
        self,
        videos,
        output_path,
        padding=DEFAULT_VIDEO_PADDING,
        transition=None,
    ):
        """Slower, but capable of concacting videos with different attibutes."""
        if transition:
            videos = self._add_transitions_to_videos(transition, videos)
        videos = [VideoFileClip(video) for video in videos]

        fps = max([video.fps for video in videos])
        width = min([video.w for video in videos])
        height = min([video.h for video in videos])
        for i, video in enumerate(videos):
            videos[i] = video.resize(newsize=(width, height)).set_fps(fps)

        concacted_video = concatenate_videoclips(
            videos,
            padding=padding,
            method=VIDEO_CONCAT_METHOD,
        )
        concacted_video.write_videofile(output_path)
        print(f"Concacted video ready at: {output_path}")
        return output_path

    def concat_videos_simple(self, videos, output_path):
        """Only use to concat videos with the same attributes (codec, resolution, fps...)"""
        input_path = self._get_concat_file(videos)
        args = [
            self.cfg.video.ffmpeg_path,
            "-f",
            "concat",
            "-safe",
            "0",
            "-i",
            input_path,
            "-c",
            "copy",
            "-y",
            output_path,
        ]
        try:
            run_subprocess(args)
            print(f"Concacted video ready at: {output_path}")
        finally:
            pass
            # os.remove(input_path)
        return output_path

    def _add_transitions_to_videos(self, transition, videos):
        videos = _add_element_to_array_after_every_n_places(transition, videos, 1)
        return videos[:-1]

    def _get_concat_file(self, videos):
        working_dir = f"{self.cfg.common.working_dir_root}/tmp"
        Path(working_dir).mkdir(parents=True, exist_ok=True)
        output_path = f"{working_dir}/{CONCAT_FILE_NAME}"
        with open(output_path, "w+") as f:
            for video in videos:
                f.write(f"file '{video}'\n")
        return output_path


def _add_element_to_array_after_every_n_places(element, array, n):
    return list(
        chain(
            *[
                array[i : i + n] + [element]
                if len(array[i : i + n]) == n
                else array[i : i + n]
                for i in range(0, len(array), n)
            ]
        )
    )
