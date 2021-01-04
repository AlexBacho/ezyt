import os

from .ttsRogue import RedditThief
from .videoEditor import VideoEditor
from .imageEditor import ImageEditor
from .cfg import Config
from .metafiles import VideoMetafile
from .base.utils import get_tmp_filepath_in_dir, debug

VIDEO_CHUNK_FORMAT = "{working_dir}/video_{index}.mp4"
DEFAULT_MAX_TITLE_LENGTH = 10
YOUTUBE_TITLE_PREFIX = "Ask Reddit |"


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
    cuts = get_cuts_in_reddit_video(submission_data.comments)

    concat_reddit_chunks(
        editor,
        video_chunks,
        video_path,
        cuts=cuts,
        transition=cfg.reddit.transition_video,
    )

    short_submission_title = get_shorter_title_if_necessary(submission.title)
    thumbnail_path = create_thumbnail_for_submission(
        cfg,
        text=short_submission_title,
        output_path=f"{working_dir}/{submission.id}_thumbnail.png",
        nsfw=submission.over_18,
    )

    metafile_path = create_video_metafile(
        output_path=f"{working_dir}/{submission.id}_metafile.json",
        thumbnail=thumbnail_path,
        video=video_path,
        channel="0",
        title=f"Ask Reddit | {short_submission_title}",
        description=create_description(submission_data),
    )

    return metafile_path


def get_cuts_in_reddit_video(comments):
    cuts = []
    for i in range(1, len(comments) - 1):
        if comments[i].is_parent and not comments[i - 1].is_parent:
            cuts.append(i)
    return cuts


def concat_reddit_chunks(editor, video_chunks, output_path, cuts=[], transition=None):
    if cuts and transition:
        tmp_file_dir = f"{editor.cfg.common.working_dir_root}/tmp"
        video_blocks = []
        files_to_delete = []
        last_cut = 0
        debug(cuts)
        for cut in cuts:
            debug(cut)
            tmp_file = get_tmp_filepath_in_dir(tmp_file_dir, suffix=".mp4")
            block = editor.concat_videos_simple(video_chunks[last_cut:cut], tmp_file)
            video_blocks.append(block)
            last_cut = cut
        files_to_delete.extend(video_blocks)

        video_blocks_with_transition = []
        for video_block in video_blocks[:-1]:
            tmp_file = get_tmp_filepath_in_dir(tmp_file_dir, suffix=".mp4")
            video_block_with_transition = editor.concat_videos_complex(
                [video_block] + [transition], tmp_file
            )
            video_blocks_with_transition.append(video_block_with_transition)
        video_blocks_with_transition.append(video_blocks[-1])
        files_to_delete.extend(video_blocks_with_transition)

        output = editor.concat_videos_simple(video_blocks_with_transition, output_path)
        for block in files_to_delete:
            pass
            # os.remove(block)
        return output
    return editor.concat_videos_simple(video_chunks, output_path)


def get_shorter_title_if_necessary(title, max_length=DEFAULT_MAX_TITLE_LENGTH):
    words = title.split()
    if len(words) > max_length:
        return f"{' '.join(words[:max_length])}..."
    return title


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


def create_thumbnail_for_submission(cfg, text, output_path, nsfw=False):
    editor = ImageEditor(cfg)
    if nsfw and cfg.reddit.get("thumbnail_background_nsfw"):
        image_path = cfg.reddit.get("thumbnail_background_nsfw")
    else:
        image_path = cfg.reddit.get("thumbnail_background")
    editor.add_highlighted_text_to_image(
        text, output_path=output_path, image_path=image_path
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
        text += str(comment.author) + ","
    return text


def get_cfg(cfg):
    if isinstance(cfg, str):
        return Config(cfg)
    if isinstance(cfg, Config):
        return cfg
    raise ValueError("No valid config provided.")