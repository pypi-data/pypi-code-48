import re

from latextomd import config


class LatexString(object):
    def __init__(self, latex_string):
        self.content = latex_string

    def process(self):
        self._remove_comments()
        self._replace_simple()
        self._math_replace()
        self._convertEnumerate()
        return self.content

    def _remove_comments(self):
        self.content = re.sub('(?<!\\\\)%.*$', '', self.content, flags=re.M)
    
    def _replace_simple(self):
        for replace_simple in config.replace_simple:
            self.content = self.content.replace(replace_simple[0],replace_simple[1])

    def _math_replace(self):
        for item in config.math_sub:
            p=re.compile(item[0])
            self.content = p.sub(item[1],self.content)
    
    def _convertEnumerate(self):
        """Agit sur les lignes.
        Converti les environnements enumerate en listes html"""
        level_enumerate = 0
        enumi = 0
        enumii = 0
        new_lines = []
        arabic = "abcdefghijklmnopqrstuvwxz"
        self.lines = self.content.splitlines()

        for line in self.lines:
            if r"\begin{enumerate}" in line or r"\begin{colenumerate}" in line:
                level_enumerate = level_enumerate + 1
                line = ""
            elif r"\end{enumerate}" in line or r"\end{colenumerate}" in line:
                if level_enumerate == 2:
                    enumii = 0
                else:
                    enumi = 0
                level_enumerate = level_enumerate - 1
                line = ""
            elif r"\item" in line and level_enumerate != 0:
                if level_enumerate == 1:
                    enumi = enumi + 1
                    line = line.replace(r"\item", str(enumi)+". ")
                    line = "\n\n" + line
                else:
                    line = line.replace(r"\item", arabic[enumii]+") ")
                    enumii = enumii + 1
                    line = "\n\n" + line
            new_lines.append(line)
        self.lines = new_lines
        self.content = '\n'.join(self.lines)
