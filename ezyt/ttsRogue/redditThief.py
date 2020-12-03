import praw
import subprocess
import sys

from pathlib import Path

from .errors import ProcessingError
from .utils import get_rendered_template, run_subprocess, debug
from .tts import TTS


REDDIT_TEMPLATE_FILEPATH = "resources/redditTemplate"
REDDIT_OP_TEMPLATE = "{title}\n{selftext}"
COMMENT_IMG_FILEPATH_TEMPLATE = "img_{index}.jpg"
COMMENT_HTML_FILEPATH_TEMPLATE = "html_{index}.html"
COMMENTS_TTS_FILEPATH_TEMPLATE = "tts_{index}.mp3"


class RedditThief:
    def __init__(self, cfg):
        self.cfg = cfg
        self.reddit = praw.Reddit(
            client_id=cfg.reddit.client_id,
            client_secret=cfg.reddit.client_secret,
            user_agent=cfg.reddit.user_agent,
        )
        self.already_scraped_file = cfg.reddit.already_scraped_file

    def scrape_hottest_from_subreddit(
        self, subreddit, render_images=True, render_tts=True
    ):
        already_scraped = self._get_already_scraped()
        for submission in self.reddit.subreddit(subreddit).hot():
            if submission.id not in already_scraped and not submission.stickied:
                debug(f"Scraping submission: {submission.id}.")
                return self._scrape(
                    submission, render_images=render_images, render_tts=render_tts
                )
            else:
                debug(f"Skipping submission: {submission.id}.")

    def scrape_submission(self, submission_id, render_images=True, render_tts=True):
        submission = self.reddit.submission(id=submission_id)
        return self._scrape(
            submission, render_images=render_images, render_tts=render_tts
        )

    def _scrape(self, submission, render_images=True, render_tts=True):
        return SubmissionData(self.cfg, submission).get_rendered_comments(
            render_images=render_images, render_tts=render_tts
        )

    def _get_already_scraped(self):
        lst = []
        try:
            with open(self.already_scraped_file, "r") as f:
                for line in f:
                    lst.append(line.strip())
        except:
            pass
        return lst

    def _write_submission_into_scraped_file(self, submission):
        with open(self.already_scraped_file, "a+") as f:
            f.write(f"{submission.id}\n")


class SubmissionData:
    """
    rendered_comments:
    list of tuples:
    [(text,text-image,tts)]
    includes OP
    """

    def __init__(self, cfg, submission):
        self.cfg = cfg
        self.html_to_img_bin_path = cfg.reddit.html_to_img_bin_path
        self.max_size_of_comment_tree = cfg.reddit.get(
            "max_size_of_comment_tree", sys.maxsize
        )
        self.working_dir = f"{cfg.common.working_dir_root}/reddit/{submission.id}"
        self.submission = submission

    def get_rendered_comments(self, render_images=True, render_tts=True):
        Path(self.working_dir).mkdir(exist_ok=True, parents=True)
        self.comments = self.get_interesting_comments_from_submission()
        debug(
            f"Found {len(self.comments)} interesting comments for submission: {self.submission.id}"
        )
        self.rendered_images = (
            self.get_rendered_images_from_comments(self.comments)
            if render_images
            else []
        )
        self.rendered_tts = (
            self.get_generated_tts_from_comments(self.comments)
            if render_tts
            else []
        )
        return self

    def get_interesting_comments_from_submission(self):
        op = self._get_data_from_op()
        original_comments = [
            c for c in self.submission.comments if isinstance(c, praw.models.Comment)
        ]
        original_comments_and_replies = self._get_sorted_comments_and_their_replies(
            original_comments
        )
        comments = [op] + original_comments_and_replies[
            : int(self.max_size_of_comment_tree)
        ]
        comments = self._remove_link_comments(comments)
        return comments

    def _remove_link_comments(self, comments):
        for index, comment in enumerate(comments):
            if len(comment.body.split()) == 1:
                if "http" in comment.body:
                    comments[index] = None
        return list(filter(None, comments))

    def _get_data_from_op(self):
        body = REDDIT_OP_TEMPLATE.format(
            title=self.submission.title, selftext=self.submission.selftext
        )
        return Comment(
            id=self.submission.id,
            author=self.submission.author,
            created_utc=self.submission.created_utc,
            score=self.submission.score,
            body=body,
        )

    def _get_data_from_comment(self, comment):
        return Comment(
            id=comment.id,
            author=comment.author,
            created_utc=comment.created_utc,
            score=comment.score,
            body=comment.body,
        )

    def _get_sorted_comments_and_their_replies(self, comments):
        comments_and_replies = []
        for comment in comments:
            comments_and_replies.append(self._get_data_from_comment(comment))
            replies = [r for r in comment.replies if isinstance(r, praw.models.Comment)]
            for reply in replies:
                comments_and_replies.append(self._get_data_from_comment(reply))
        return comments_and_replies

    def get_rendered_images_from_comments(self, comments):
        rendered_comments = []
        for i, comment in enumerate(comments):
            debug(f"Rendering image .jpg file for {comment.id}.")
            rendered_comments.append(self._get_rendered_image_from_comment(i, comment))
        return rendered_comments

    def _get_rendered_image_from_comment(self, index, comment):
        rendered_template_filepath = self._get_rendered_template_from_comment(
            index, comment
        )
        rendered_image_filepath = (
            f"{self.working_dir}/{COMMENT_IMG_FILEPATH_TEMPLATE.format(index=index)}"
        )
        args = [
            self.html_to_img_bin_path,
            rendered_template_filepath,
            rendered_image_filepath,
        ]
        _, stderr = run_subprocess(args)
        if not stderr:
            debug(f"Rendering of comment: {comment.id} successful.")
        return rendered_image_filepath

    def _get_rendered_template_from_comment(self, index, comment):
        args = {
            "author": comment.author,
            "created_utc": comment.created_utc,
            "score": comment.score,
            "body": comment.body,
        }
        filepath = (
            f"{self.working_dir}/{COMMENT_HTML_FILEPATH_TEMPLATE.format(index=index)}"
        )
        with open(filepath, "w+") as f:
            f.write(
                get_rendered_template(self.cfg.reddit.comment_template_filepath, args)
            )
        return filepath

    def get_generated_tts_from_comments(self, comments):
        tts = TTS(self.cfg)
        generated_tts = []
        for index, comment in enumerate(comments):
            debug(f"Rendering text-to-speech mp3 file for {comment.id}.")
            generated_tts.append(
                tts.get_mp3_from_text(
                    text=comment.body,
                    mp3_path=f"{self.working_dir}/{COMMENTS_TTS_FILEPATH_TEMPLATE.format(index=index)}",
                    use_paid_tts=bool(self.cfg.reddit.get("use_paid_tts", False)),
                    voice_id=comment.author,
                )
            )
        return generated_tts


class Comment:
    def __init__(self, id, author, created_utc, score, body):
        self.id = id
        self.author = author
        self.created_utc = created_utc
        self.score = score
        self.body = body
