from .ttsRogue import RedditThief
from .videoEditor import VideoEditor
from .imageEditor import ImageEditor
from .cfg import Config
from .metafiles import VideoMetafile

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

    submission = submission_data.submission
    editor = VideoEditor(cfg)
    working_dir = f"{cfg.common.working_dir_root}/reddit/{submission.id}"

    if render_tts:
        video_chunks = merge_images_with_audio(
            editor=editor,
            image_files=submission_data.rendered_images,
            audio_files=submission_data.rendered_tts,
            working_dir=working_dir,
        )
    else:
        # TODO: replace this for mute videos
        video_chunks = merge_images_with_audio(
            editor=editor,
            image_files=submission_data.rendered_images,
            audio_files=submission_data.rendered_tts,
            working_dir=working_dir,
        )

    video_path = output_path or f"{working_dir}/{submission.id}_final.mp4"
    editor.concat_videos(video_chunks, video_path)

    submission_title = submission.title or submission.selftext
    thumbnail_path = create_thumbnail_for_submission(
        cfg,
        text=submission_title,
        output_path=f"{working_dir}/{submission.id}_thumbnail.png",
    )

    metafile_path = create_video_metafile(
        output_path=f"{working_dir}/{submission.id}_metafile.json",
        thumbnail=thumbnail_path,
        video=video_path,
        channel="0",
        title=f"Ask Reddit | {submission.title}",
        description=create_description(submission_data),
    )

    return metafile_path


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


def create_thumbnail_for_submission(cfg, text, output_path):
    editor = ImageEditor(cfg)
    editor.add_highlighted_text_to_image(
        text, output_path=output_path, image_path=cfg.reddit.get("thumbnail_background")
    )
    return output_path


def create_video_metafile(output_path, **kwargs):
    metafile = VideoMetafile(output_path)
    metafile.set_attrs(**kwargs)
    metafile.save()
    return output_path


def create_description(submission_data):
    text = f"{submission_data.submission.title}\n{submission_data.submission.permalink}"
    text += "\n Thanks to all the users who participated: \n"
    for comment in submission_data.comments:
        text += str(comment.author)
    return text


def get_cfg(cfg):
    if isinstance(cfg, str):
        return Config(cfg)
    if isinstance(cfg, Config):
        return cfg
    raise ValueError("No valid config provided.")