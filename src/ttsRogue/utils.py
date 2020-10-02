
from jinja2 import Environment, PackageLoader, select_autoescape

env = Environment(
    loader=PackageLoader('ezyt', 'templates'),
    autoescape=select_autoescape(['html', 'xml'])
)

def get_rendered_template(template, args):
    template = env.get_template(template)
    return template.render(args)