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
from ezyt.base.utils import debug

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

    def add_audio_to_image(
        self, image_path, audio_path, output_path, fps=None, logger=None
    ):
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
            logger=logger,
        )
        return output_path

    def concat_videos_complex(
        self,
        videos,
        output_path,
        transition=None,
    ):
        """Slower, but capable of concacting videos with different attibutes."""
        if transition:
            videos = self._add_transitions_to_videos(transition, videos)
        debug(
            f"Concacting videos: {videos[0]} {'...' if len(videos) > 2 else ''} {videos[-1]}"
        )
        _concat_videos_with_melt(videos, output_path)
        debug(f"Concacted video ready at: {output_path}")
        return output_path

    def concat_videos_simple(self, videos, output_path):
        """Only use to concat videos with the same attributes (codec, resolution, fps...)"""
        ffmpeg_concat_file = self._get_concat_file(videos)
        args = [
            self.cfg.video.ffmpeg_path,
            "-f",
            "concat",
            "-safe",
            "0",
            "-i",
            ffmpeg_concat_file,
            "-c",
            "copy",
            "-y",
            output_path,
        ]
        try:
            run_subprocess(args)
            debug(f"Concacted video ready at: {output_path}")
        finally:
            os.remove(ffmpeg_concat_file)
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


def _concat_videos_with_melt(video_paths, output_path):
    args = (
        ["melt"]
        + video_paths
        + [
            "-consumer",
            f"avformat:{output_path}.mp4",
            "acodec=libmp3lame",
            "vcodec=libx264",
        ]
    )
    run_subprocess(args)
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
