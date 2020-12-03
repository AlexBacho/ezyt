import json

from pathlib import Path


class Metafile:
    def __init__(self, path):
        if Path(path).exists():
            self.load(path)
        self.path = path

    def __str__(self):
        return str(self.__dict__)

    def __repr__(self):
        return str(self)

    def get(self, item, default=None):
        return self.__dict__.get(item, default)

    def set_attrs(self, **kwargs):
        self.__dict__.update(kwargs)

    def save(self):
        self._save_to_path(self.path)

    def save_as(self, path):
        self._save_to_path(path)
        self.path = path

    def load(self, path):
        with open(path, "r") as f:
            self.__dict__ = json.load(f)

    def _save_to_path(self, path):
        with open(path, "w+") as f:
            f.write(json.dumps(self.__dict__))


class VideoMetafile(Metafile):
    def __init__(self, path):
        self.channel = ""
        self.description = ""
        self.title = ""
        self.tags = ""
        super().__init__(path)
