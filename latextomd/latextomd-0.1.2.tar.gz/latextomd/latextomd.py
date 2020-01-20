import re

from latextomd import config
from latextomd.soup import Latex
from latextomd.text_manipulation import LatexString





def _process_preamble(latex_string):
    """Detect latex preamble"""
    if r"\begin{document}" in latex_string:
        preamble, content = latex_string.split(r"\begin{document}")
        if r"\end{document}" in content:
            content = content.split(r"\end{document}")[0]
    else:
        preamble = 'default header\n'
        content = latex_string
    return preamble, content


def _strip_lines(latex_string):
    lines = latex_string.splitlines()
    result = []
    for line in lines:
        result.append(line.strip())
    return '\n'.join(result)


def _clean_lines(latex_string):
    lines = latex_string.splitlines()
    while lines[0] == '':
        lines = lines[1:]
    while lines[-1] == '':
        lines = lines[:-1]
    content = '\n'.join(lines)
    while '\n\n\n' in content:
        content = content.replace('\n\n\n', '\n\n')
    return content


def _delete_blocks(latex_string):
    content = latex_string
    for env in config.del_environnements:
        content = content.replace(env, '')
    return content


def to_markdown(latex_string, export_file_name=""):
    content = latex_string
    content = _strip_lines(content)
   
    preamble, content = _process_preamble(content)
    content = LatexString(content).process()
    content = Latex(content).process()
    content = _delete_blocks(content)
    content = _strip_lines(content)

    content = _clean_lines(content)
    return content
