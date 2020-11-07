from moviepy import AudioFileClip, ImageClip, VideoFileClip, concatenate_videoclips

DEFAULT_IMAGE_VIDEO_FPS = 5
COLOR_DARK_GREY = ""
COLOR_BACKGROUND_SIZE = 30


class VideoEditor:
    def __init__(self, cfg):
        self.cfg = cfg

    def add_audio_to_image(self, image_path, audio_path, output_path):
        audio = AudioFileClip(audio_path)
        video = (
            ImageClip(image_path)
            .resize(1.2)
            .on_color(size=COLOR_BACKGROUND_SIZE, color=COLOR_DARK_GREY)
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
        concacted_video = concatenate_videoclips(videos)
        concacted_video.write_videofile(output_path)
        return output_path
