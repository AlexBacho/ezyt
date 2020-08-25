class VideoObject():
    def __init__(self, account, name, **kwargs):
        self.account = account
        self.name = name
        self.description = kwargs.get('description')
        self.title = kwargs.get('title')
        self.tags = kwargs.get('tags')

    def __str__(self):
        raise NotImplementedError()

    def __repr__(self):
        return str(self)

    def set_description_from_template(self, template_file, **kwargs):
        with open(template_file) as f:
            self.description = f.read().format(kwargs)
