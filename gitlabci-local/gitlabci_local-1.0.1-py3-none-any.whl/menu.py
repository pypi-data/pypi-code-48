#!/usr/bin/env python3

# Libraries
import PyInquirer

# Components
from .main import NAME, term
from .runner import launcher

# Selector theme
SelectorTheme = PyInquirer.style_from_dict({
    PyInquirer.Token.Separator: '#FFFF00 bold',
    PyInquirer.Token.QuestionMark: '#FFFF00 bold',
    PyInquirer.Token.Selected: '#00FF00 bold',
    PyInquirer.Token.Instruction: '#00FFFF bold',
    PyInquirer.Token.Pointer: '#FFFF00 bold',
    PyInquirer.Token.Answer: '#00FFFF bold',
    PyInquirer.Token.Question: '#00FF00 bold',
})

# Configurations theme
ConfigurationsTheme = PyInquirer.style_from_dict({
    PyInquirer.Token.Selected: '#00FF00 bold',
    PyInquirer.Token.Instruction: '#00FFFF bold',
    PyInquirer.Token.Pointer: '#FFFF00 bold',
    PyInquirer.Token.Answer: '#00FFFF bold',
    PyInquirer.Token.Question: '#FFFF00 bold',
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
        answers = PyInquirer.prompt(selection_prompt, style=SelectorTheme)
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

# Configurator
def configurator(configurations):

    # Variables
    configurations_defaults = dict()
    configurations_prompt = []
    result = dict()

    # Header
    print(' ')
    print(' %s===[ %sConfigurations menu %s]===%s' %
          (term.green + term.bold, term.yellow + term.bold, term.green + term.bold,
           term.normal))
    print(' ', flush=True)

    # Walk through configurations
    for variable in configurations['variables']:

        # Extract configuration fields
        variable_fields = configurations['variables'][variable].split('# ')
        variable_values = variable_fields[0].split(',')
        variable_description = variable_fields[1]
        variable_choices = []

        # Register default values
        configurations_defaults[variable] = variable_values[0]

        # Prepare configuration choices
        for choice in variable_values:
            variable_choices += [{
                'name': '%s' % (choice),
                'value': choice,
                'checked': False
            }]

        # Prepare configuration selection
        configurations_prompt += [{
            'type': 'list',
            'qmark': '',
            'message': 'Variable %s: %s:' % (variable, variable_description),
            'name': variable,
            'choices': variable_choices
        }]

    # Request configurations selection
    if configurations_prompt:
        try:
            answers = PyInquirer.prompt(configurations_prompt, style=ConfigurationsTheme)
        except:
            for configuration in configurations_prompt:
                print(' %s%s  %s%s%s' %
                      (term.yellow + term.bold, configuration['message'],
                       term.cyan + term.bold,
                       configurations_defaults[configuration['name']], term.normal))
            answers = configurations_defaults
    else:
        print(
            '%s%s: %sERROR: %sNo configuration found%s' %
            (term.green + term.bold, NAME, term.red + term.bold, term.normal + term.bold,
             term.normal), flush=True)
        answers = None

    # Extract configurations selection
    if answers:
        result = answers
    else:
        result = configurations_defaults

    # Footer
    print(' ', flush=True)

    # Result
    return result
