from .ttsRogue import RedditThief
from .videoEditor import VideoEditor
from .imageEditor import ImageEditor
from .cfg import Config


DEFAULT_OUTPUT_PATH = "unnamed.mp4"
VIDEO_CHUNK_FORMAT = "{working_dir}/video_{index}.mp4"


def create_reddit_video(
    cfg, submission_id=None, subreddit=None, render_tts=True, output_path=None
):
    cfg = get_cfg(cfg)
    if not submission_id and not subreddit:
        raise ValueError(
            "Must provide either a submission id or a subreddit to scrape from."
        )
    if submission_id and subreddit:
        raise ValueError("Can't do both.")

    reddit = RedditThief(cfg)
    if submission_id:
        submission_data = reddit.scrape_submission(
            submission_id, render_images=True, render_tts=render_tts
        )
    if subreddit:
        submission_data = reddit.scrape_hottest_from_subreddit(
            subreddit, render_images=True, render_tts=render_tts
        )

    editor = VideoEditor(cfg)
    working_dir = (
        f"{cfg.common.working_dir_root}/reddit/{submission_data.submission.id}"
    )

    if render_tts:
        video_chunks = merge_images_with_audio(
            editor=editor,
            image_files=submission_data.rendered_images,
            audio_files=submission_data.rendered_tts,
            working_dir=working_dir,
        )
    else:
        # TODO: replace this
        video_chunks = merge_images_with_audio(
            editor=editor,
            image_files=submission_data.rendered_images,
            audio_files=submission_data.rendered_tts,
            working_dir=working_dir,
        )

    output_path = output_path or DEFAULT_OUTPUT_PATH
    editor.concat_videos(video_chunks, output_path)
    return output_path


def merge_images_with_audio(editor, image_files, audio_files, working_dir):
    if not len(image_files) == len(audio_files):
        raise Exception(
            "The number of rendered comments and rendered tts files doesn't match."
        )
    ret = []
    for index, image_file in enumerate(image_files):
        ret.append(
            editor.add_audio_to_image(
                image_file,
                audio_files[index],
                VIDEO_CHUNK_FORMAT.format(working_dir=working_dir, index=index),
            )
        )
    return ret


def get_cfg(cfg):
    if isinstance(cfg, str):
        return Config(cfg)
    if isinstance(cfg, Config):
        return cfg
    raise ValueError("No valid config provided.")