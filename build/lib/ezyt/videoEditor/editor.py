from moviepy.editor import (
    AudioFileClip,
    ImageClip,
    VideoFileClip,
    concatenate_videoclips,
)

DEFAULT_IMAGE_VIDEO_FPS = 5
COLOR_BLACK = (255, 255, 255)
COLOR_BACKGROUND_SIZE = None
DEFAULT_VIDEO_PADDING = 0.2
VIDEO_CONCAT_METHOD = "compose"


class VideoEditor:
    def __init__(self, cfg):
        self.cfg = cfg

    def add_audio_to_image(self, image_path, audio_path, output_path):
        audio = AudioFileClip(audio_path)
        video = (
            ImageClip(image_path)
            .on_color(size=COLOR_BACKGROUND_SIZE, color=COLOR_BLACK)
            .set_pos((0.5, 0.5), relative=True)
            .set_audio(audio)
            .set_duration(audio.duration)
            .set_fps(self.cfg.video.get("image_video_fps", DEFAULT_IMAGE_VIDEO_FPS))
        )
        video.write_videofile(
            output_path,
        )
        return output_path

    def concat_videos(self, videos, output_path):
        videos = [VideoFileClip(video) for video in videos]
        concacted_video = concatenate_videoclips(
            videos, padding=DEFAULT_VIDEO_PADDING, method=VIDEO_CONCAT_METHOD
        )
        concacted_video.write_videofile(output_path)
        return output_path
