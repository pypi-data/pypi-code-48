import argparse
import sys
from pprint import pprint

import requests
from selectolax.parser import HTMLParser

from py_terminal_notifier import TerminalNotifier

BASE_URL = 'https://android-arsenal.com'


def get_submission(_sort, _show):
    params = {
        'sort': _sort
    }
    if _show != "all":
        params.update({'category': _show})

    webpage = requests.get(BASE_URL, params=params).text
    tree = HTMLParser(webpage)

    entries = filter(lambda x: not bool(x.css('#adsBlock1')),
                     tree.css('#projects > .pi'))
    submission = next(entries)

    anchor_elm = submission.css_first('.header a')
    tag = submission.css_first('.header a.tags').text()
    title = anchor_elm.text()
    badge = submission.css_first('.header a.badge').text()
    submission_link = anchor_elm.attrs.get('href')
    open_link = f"{BASE_URL}{submission_link}"
    description = submission.css_first('.desc').text()
    date = submission.css_first('.ftr.l').text().strip()
    user = submission.css_first('.ftr.r').text().strip()

    subtitle = f"{date} | {tag} | {badge}"

    terminal_notifier_obj = {
        'title': title,
        'subtitle': subtitle,
        'message': description,
        'open': open_link,
        'app_icon': 'https://android-arsenal.com/apple-touch-icon-precomposed.png'
    }
    TerminalNotifier(**terminal_notifier_obj).run_cmd()


def get_used_arg(group, arguments):
    args_gen = ({'cmd': g.dest, 'val': getattr(arguments, g.dest)}
                for g in group._group_actions)
    try:
        f_res = filter(lambda x: x.get('val'), args_gen)
        return next(f_res).get('cmd')
    except StopIteration:
        return next(ga.dest for ga in group._group_actions)


def main():
    parser = argparse.ArgumentParser(description='Android Arsenal Notifier')
    show_group = parser.add_mutually_exclusive_group()
    show_group.add_argument('-a', '--all', dest='all',
                            help='Show all submissions', action='store_true')
    show_group.add_argument('-f', '--free', dest='1',
                            help='Show free submissions', action='store_true')
    show_group.add_argument('-p', '--paid', dest='2',
                            help='Show paid submissions', action='store_true')
    show_group.add_argument('-d', '--demo', dest='3',
                            help='Show demo submissions', action='store_true')

    sort_group = parser.add_mutually_exclusive_group()
    sort_group.add_argument('--registration', dest='created',
                            help='Sort by registration', action='store_true')
    sort_group.add_argument('--update', dest='updated',
                            help='Sort by last updated', action='store_true')
    sort_group.add_argument('--rating', dest='rating',
                            help='Sort by rating', action='store_true')
    sort_group.add_argument(
        '--name', dest='name', help='Sort by name', action='store_true')
    args = parser.parse_args()

    sort_group_cmd = get_used_arg(sort_group, args)
    show_group_cmd = get_used_arg(show_group, args)
    get_submission(sort_group_cmd, show_group_cmd)

    return 0


if __name__ == "__main__":
    sys.exit(main())
