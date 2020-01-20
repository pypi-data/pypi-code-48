#!/usr/bin/env python3

# Libraries
import collections
import oyaml as yaml

# Components
from .main import NAME, term

# Reader
def reader(options):

    # Read GitLab CI YAML
    with open(options.configuration, 'r') as configuration_data:
        try:
            data = yaml.safe_load(configuration_data)
            return parser(options, data)
        except yaml.YAMLError as exc:
            print('%s%s: %sERROR: %s%s%s' %
                  (term.green + term.bold, NAME, term.red + term.bold,
                   term.normal + term.bold, exc, term.normal))
        except:
            print(
                '%s%s: %sERROR: %s%s' % (term.green + term.bold, NAME, term.red +
                                         term.bold, term.normal + term.bold, term.normal))

    # Failure
    return None

# Parser
def parser(options, data):

    # Variables
    global_values = dict({
        'after_script': [],
        'before_script': [],
        'image': '',
        'variables': dict()
    })
    jobs = dict()
    stages = dict()

    # Iterate through stages
    for node in data:

        # Filter services node
        if node == 'services':
            continue

        # Filter image node
        if node == 'image':
            global_values['image'] = data[node]
            continue

        # Filter before_script node
        if node == 'before_script':
            global_values['before_script'] = data[node]
            continue

        # Filter after_script node
        if node == 'after_script':
            global_values['after_script'] = data[node]
            continue

        # Filter stages node
        if node == 'stages':
            for i, stage in enumerate(data['stages']):
                stages[stage] = i
            continue

        # Filter variables node
        if node == 'variables':
            global_values['variables'] = data['variables']
            continue

        # Validate job node
        if 'stage' not in data[node]:
            continue

        # Ignore template stage
        if node[0:1] == '.':
            continue

        # Register job
        jobs[node] = stager(options, node, data[node], global_values)

    # Sort jobs based on stages
    jobs = collections.OrderedDict(
        sorted(jobs.items(), key=lambda x: stages[x[1]['stage']]))

    # Result
    return jobs

# Stager
def stager(options, job_name, job_data, global_values):

    # Variables
    job = dict()

    # Prepare stage
    job['name'] = job_name
    job['stage'] = job_data['stage']
    job['image'] = global_values['image']
    job['variables'] = dict(global_values['variables'])
    job['before_script'] = global_values['before_script'][:]
    job['script'] = []
    job['after_script'] = global_values['after_script'][:]
    job['when'] = 'on_success'
    job['tags'] = []

    # Extract job image
    if 'image' in job_data and job_data['image']:
        job['image'] = job_data['image']

    # Extract job variables
    if 'variables' in job_data and job_data['variables']:
        job['variables'].update(job_data['variables'])

    # Extract job before_script
    if 'before_script' in job_data and job_data['before_script']:
        job['before_script'] = job_data['before_script'][:]

    # Extract job script
    if 'script' in job_data and job_data['script']:
        job['script'] = job_data['script'][:]

    # Extract job after_script
    if 'after_script' in job_data and job_data['after_script']:
        job['after_script'] = job_data['after_script'][:]

    # Extract job when
    if 'when' in job_data and job_data['when'] in [
            'on_success', 'on_failure', 'always', 'manual'
    ]:
        job['when'] = job_data['when']

    # Extract job tags
    if 'tags' in job_data and job_data['tags']:
        job['tags'] = job_data['tags'][:]

    # Configure job tags
    if (set(job['tags']) & set(options.manual_tags)):
        job['when'] = 'manual'

    # Result
    return job
