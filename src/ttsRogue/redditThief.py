import praw
import subprocess

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


class RedditScraper:
    def __init__(self, cfg):
        self.reddit = praw.Reddit(
            client_id=cfg.reddit.client_id
            client_secret=cfg.reddit.client_id
            user_agent=cfg.reddit.user_agent
        )
        self.already_scraped_file = cfg.reddit.already_scraped_file

    def process(self, url):
        pass

    def auto_scrape(self, subreddit):
        already_scraped = self._get_already_scraped()
        for submission in self.reddit.subreddit(subreddit).hot():
            if submission.id not in already_scraped and not submission.stickied:
                data = self.scrape(submission)

    def scrape(self, submission):
        return 

    def _get_already_scraped(self):
        lst = []
        with open(self.already_scraped_file) as f:
            for line in f:
                lst.append(line)
        return lst
    
    def _write_submission_into_scraped_file(self, submission):
        with open(self.already_scraped_file, 'w+') as f:
            f.write(submission.id)


class SubmissionData:
    """
    rendered_comments:
    list of tuples:
    [(text,text-image,tts)]
    includes OP
    """
    def __init__(self, cfg, submission):
        self.html_to_img_bin_path = cfg.reddit.html_to_img_bin_path
        self.__dict__ = submission.__dict__
        rendered_images = self.get_rendered_images_from_submission()
        generated_tts = self.get_generated_tts_from_submission()
        self.rendered_comments = zip(self.comments, rendered_images, generated_tts)
    
    def get_rendered_images_from_submission(self):
        images = []
        images.append(self.get_rendered_image_from_comment(self))
        for comment in self.comments:
            images.append(self.get_rendered_image_from_comment(comment))
        return images

    def get_rendered_image_from_comment(self, comment):
        args = [
            self.html_to_img_bin_path,
            
        ]

    def get_generated_tts_from_submission(self):
        tts = []
        tts.append(self.get_single_generated_tts_from_text(self))
        for comment in self.comments:
            tts.append(self.get_single_generated_tts_from_text(comment))
        return tts

    def get_single_generated_tts_from_text(self, text):
        pass
    
    def _run(self, args):
        process = subprocess.Popen(
            args,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        stdout, stderr = process.communicate()
        if process.returncode != 0:
            logging.error(
                f'Subprocess failed with code: {process.returncode} msg: {stderr}')
            raise ProcessingError(stderr)
        return stdout
    
