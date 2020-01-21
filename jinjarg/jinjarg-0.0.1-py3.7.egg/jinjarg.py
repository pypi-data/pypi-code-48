# coding: utf-8

"""CLI-template renderer like m4 but based on Jinja2"""

from jinja2 import Template
from argparse import ArgumentParser


class Jinjarg:
    def __init__(self):
        self.parser = ArgumentParser()
        self._default_setup()
        self.setup()
        self.args = self.parser.parse_args()

    def _default_setup(self):
        self.parser.description = __doc__
        self.parser.add_argument('-t', '--template', required=True, help="Path to template-file")

    def setup(self):
        raise NotImplementedError("""Do not use Jinjarg directly!
        
Usage example:
```        
from jinjarg import Jinjarg


class Example(Jinjarg):
    def setup(self):
        self.parser.add_argument("--example", type=str, help="Example variable passed to template", required=True)


if __name__ == '__main__':
    print(Example())
```
""")

    def __str__(self):
        with open(self.args.template) as fd:
            template = Template(fd.read())
            return template.render(args=self.args)
