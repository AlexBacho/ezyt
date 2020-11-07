import praw
import subprocess
import logging

from pathlib import Path

from .errors import ProcessingError
from .utils import get_rendered_template, run_subprocess

"""
class Submission(SubmissionListingMixin, UserContentMixin, FullnameMixin, RedditBase):
    A class for submissions to reddit.

    **Typical Attributes**

    This table describes attributes that typically belong to objects of this
    class. Since attributes are dynamically provided (see
    :ref:`determine-available-attributes-of-an-object`), there is not a
    guarantee that these attributes will always be present, nor is this list
    necessarily complete.

    =========================== ===============================================
    Attribute                   Description
    =========================== ===============================================
    ``author``                  Provides an instance of :class:`.Redditor`.
    ``clicked``                 Whether or not the submission has been clicked
                                by the client.
    ``comments``                Provides an instance of
                                :class:`.CommentForest`.
    ``created_utc``             Time the submission was created, represented in
                                `Unix Time`_.
    ``distinguished``           Whether or not the submission is distinguished.
    ``edited``                  Whether or not the submission has been edited.
    ``id``                      ID of the submission.
    ``is_original_content``     Whether or not the submission has been set
                                as original content.
    ``is_self``                 Whether or not the submission is a selfpost
                                (text-only).
    ``link_flair_template_id``  The link flair's ID, or None if not flaired.
    ``link_flair_text``         The link flair's text content, or None if not
                                flaired.
    ``locked``                  Whether or not the submission has been locked.
    ``name``                    Fullname of the submission.
    ``num_comments``            The number of comments on the submission.
    ``over_18``                 Whether or not the submission has been marked
                                as NSFW.
    ``permalink``               A permalink for the submission.
    ``poll_data``               A :class:`.PollData` object representing the
                                data of this submission, if it is a poll
                                submission.
    ``score``                   The number of upvotes for the submission.
    ``selftext``                The submissions' selftext - an empty string if
                                a link post.
    ``spoiler``                 Whether or not the submission has been marked
                                as a spoiler.
    ``stickied``                Whether or not the submission is stickied.
    ``subreddit``               Provides an instance of :class:`.Subreddit`.
    ``title``                   The title of the submission.
    ``upvote_ratio``            The percentage of upvotes from all votes on the
                                submission.
    ``url``                     The URL the submission links to, or the
                                permalink if a selfpost.
    =========================== ===============================================

"""

REDDIT_TEMPLATE_FILEPATH = "resources/redditTemplate"


class RedditThief:
    def __init__(self, cfg):
        self.cfg = cfg
        self.reddit = praw.Reddit(
            client_id=cfg.reddit.client_id,
            client_secret=cfg.reddit.client_id,
            user_agent=cfg.reddit.user_agent,
        )
        self.already_scraped_file = cfg.reddit.already_scraped_file

    def process(self, url):
        pass

    def auto_scrape(self, subreddit):
        already_scraped = self._get_already_scraped()
        for submission in self.reddit.subreddit(subreddit).hot():
            if submission.id not in already_scraped and not submission.stickied:
                return self.scrape(submission)

    def scrape(self, submission):
        return SubmissionData(self.cfg, submission).get_rendered_comments()

    def _get_already_scraped(self):
        lst = []
        with open(self.already_scraped_file) as f:
            for line in f:
                lst.append(line)
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
        self.working_dir = f"{cfg.common.working_dir_root}/reddit/{submission.id}"
        self.submission = submission

    def get_rendered_comments(self, render_text=True, generate_tts=True):
        Path(self.working_dir).mkdir(exist_ok=True, parents=True)
        original_comments = self.submission.selftext + self.submission.comments
        rendered_text = self.get_rendered_text_from_submission() if render_text else []
        generated_tts = self.get_generated_tts_from_submission() if generate_tts else []
        return zip(original_comments, rendered_text, generated_tts)

    def get_rendered_text_from_submission(self):
        images = []
        part_counter = 0
        images.append(self._get_rendered_text_from_comment(self, part_counter))
        for comment in self.submission.comments:
            images.append(self._get_rendered_text_from_comment(comment, part_counter))
        return images

    def _get_rendered_text_from_comment(self, comment, part):
        rendered_template = self._get_rendered_template_from_comment(comment)
        args = [
            self.html_to_img_bin_path,
            rendered_template,
            f"{self.working_dir}/{part}",
        ]
        stdout = run_subprocess(args)
        if not stdout:
            logging.error(f"Rendering of comment: {comment.id} failed.")
        return f"{self.working_dir}/{part}"

    def _get_rendered_template_from_comment(self, comment):
        args = {
            "author": comment.author,
            "created_utc": comment.created_utc,
            "score": comment.score,
            "body": comment.body,
        }
        filepath = f"{self.working_dir}/{comment.id}.txt"
        with open(filepath, "w+") as f:
            f.write(get_rendered_template(REDDIT_TEMPLATE_FILEPATH, args))
        return filepath

    def get_generated_tts_from_submission(self):
        tts = []
        tts.append(self._get_generated_tts_from_text(self))
        for comment in self.submission.comments:
            tts.append(self._get_generated_tts_from_text(comment))
        return tts

    def _get_generated_tts_from_text(self, text):
        pass
