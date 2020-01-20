#!/usr/bin/env python3

# Libraries
import docker
import os
from pathlib import Path
import tempfile

# Components
from .main import term

# Launcher
def launcher(options, jobs):

    # Variables
    result = None

    # Run selected jobs
    for job in jobs:

        # Filter jobs list
        if not options.pipeline and job not in options.names:
            continue

        # Filter stages list
        if options.pipeline and options.names and jobs[job]['stage'] not in options.names:
            continue

        # Filter manual jobs
        job_manual = (jobs[job]['when'] == 'manual')
        if job_manual and not options.manual and job not in options.names:
            continue

        # Raise initial result
        if result == None:
            result = True

        # Run job
        result = runner(options, jobs[job], result)

    # Result
    return True if result else False

# Runner
def runner(options, job_data, last_result):

    # Variables
    result = False

    # Filter when
    if last_result and job_data['when'] not in ['on_success', 'manual', 'always']:
        return last_result
    if not last_result and job_data['when'] not in ['on_failure']:
        return last_result

    # Header
    if not options.quiet:
        print(' %s===[ %s%s: %s%s %s(%s) %s]===%s' %
              (term.green + term.bold, term.yellow + term.bold, job_data['stage'],
               term.yellow + term.bold, job_data['name'], term.cyan + term.bold,
               job_data['image'], term.green + term.bold, term.normal))
        print(' ', flush=True)

    # Create Docker client
    client = docker.from_env()

    # Acquire project path
    pathProject = options.path
    pathParent = str(Path(pathProject).parent)

    # Prepare entrypoint and scripts
    entrypoint = 'sh -ex'
    scripts = []

    # Append before_scripts, scripts, after_scripts
    if options.before:
        scripts += job_data['before_script']
    scripts += job_data['script']
    if options.after:
        scripts += job_data['after_script']

    # Prepare commands
    with tempfile.NamedTemporaryFile(mode='w') as script:
        script.write('\n'.join(scripts))
        script.flush()

        # Prepare mounts
        temp_dir = tempfile.gettempdir()
        volumes = {
            pathParent: {
                'bind': pathParent,
                'mode': 'rw'
            },
            temp_dir: {
                'bind': temp_dir,
                'mode': 'rw'
            },
            '/var/run/docker.sock': {
                'bind': '/var/run/docker.sock',
                'mode': 'rw'
            }
        }

        # Prepare variables
        variables = dict()
        for variable in job_data['variables']:
            variables[variable] = os.path.expandvars(job_data['variables'][variable])

        # Launch container
        container = client.containers.run(
            job_data['image'], auto_remove=True, command=script.name, detach=True,
            entrypoint=entrypoint, environment=variables, network_mode='bridge',
            stdout=True, stderr=True, stream=True, volumes=volumes,
            working_dir=pathProject)

        # Execution wrapper
        success = False
        try:

            # Show container logs
            for line in container.logs(stream=True):
                print(line.decode('utf-8'), end='', flush=True)

            # Check container status
            wait = container.wait()
            success = (wait['StatusCode'] == 0)

            # Stop container
            container.stop()

        # Intercept execution failures
        except:

            # Stop container
            try:
                container.stop()
            except:
                pass

        # Result evaluation
        if job_data['when'] in ['on_failure', 'always']:
            result = last_result
        elif success:
            result = True

    # Footer
    print(' ', flush=True)
    if not options.quiet:
        print(' %s> Result: %s%s' %
              (term.yellow + term.bold, term.green + term.bold +
               'Success' if result else term.red + term.bold + 'Failure', term.normal))
        print(' ')
        print(' ', flush=True)

    # Result
    return result
