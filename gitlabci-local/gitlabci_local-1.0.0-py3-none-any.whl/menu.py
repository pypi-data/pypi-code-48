#!/usr/bin/env python3

# Libraries
import PyInquirer

# Components
from .main import NAME, term
from .runner import launcher

# Menu theme
MenuTheme = PyInquirer.style_from_dict({
    PyInquirer.Token.Separator: '#FFFF00 bold',
    PyInquirer.Token.QuestionMark: '#FFFF00 bold',
    PyInquirer.Token.Selected: '#00FF00 bold',
    PyInquirer.Token.Instruction: '#00FFFF bold',
    PyInquirer.Token.Pointer: '#FFFF00 bold',
    PyInquirer.Token.Answer: '#00FFFF bold',
    PyInquirer.Token.Question: '#00FF00 bold',
})

# Selector
def selector(options, jobs):

    # Variables
    jobs_available = False
    jobs_choices = []
    result = True
    stage = ''

    # Stages groups
    for job in jobs:

        # Filtered jobs
        if options.names and job not in options.names:
            continue

        # Stages separator
        if stage != jobs[job]['stage']:
            stage = jobs[job]['stage']
            jobs_choices += PyInquirer.Separator('\n Stage %s:' % (stage)),

        # Disabled jobs
        disabled = False
        when = ''
        if jobs[job]['when'] in ['manual'] and not options.manual:
            disabled = 'Manual'
        else:
            if jobs[job]['when'] == 'manual':
                when = ' (Manual)'
            elif jobs[job]['when'] == 'on_failure':
                when = ' (On failure)'
            jobs_available = True

        # Register job tags
        tags = ''
        if jobs[job]['tags']:
            tags = ' [%s]' % (','.join(jobs[job]['tags']))

        # Job choices
        jobs_choices += [{
            'name': '%s%s%s' % (jobs[job]['name'], tags, when),
            'value': job,
            'checked': False,
            'disabled': disabled
        }]

    # Prepare jobs selection
    selection_type = 'list' if options.list else 'checkbox'
    selection_prompt = [{
        'type': selection_type,
        'qmark': '',
        'message': '===[ Jobs selector ]===',
        'name': 'jobs',
        'choices': jobs_choices
    }]

    # Request jobs selection
    if jobs_choices and jobs_available:
        answers = PyInquirer.prompt(selection_prompt, style=MenuTheme)
    else:
        print(
            '%s%s: %sERROR: %sNo jobs found for selection%s' %
            (term.green + term.bold, NAME, term.red + term.bold, term.normal + term.bold,
             term.normal), flush=True)
        answers = None

    # Parse jobs selection
    if answers and 'jobs' in answers:
        options.names = answers['jobs']
    else:
        options.names = []

    # Footer
    print(' ')
    print(' ', flush=True)

    # Launch jobs
    if options.names:
        result = launcher(options, jobs)

    # Result
    return result
