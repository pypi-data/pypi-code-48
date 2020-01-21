#!/usr/bin/env python
"""
Program: push_cli.py
Author: Andrew Blair and Robert Hu
Description: A command line interface for syncing Synapse to a local machine without overwriting local entitites
"""

from .run import push
import argparse

def cli():
    '''
    Push local updates to Synapse

    Parameters
    ----------
    None

    Returns
    -------
    args.username : str
        Synapse username
    args.password : str
        Synapse password
    args.project : str
        Synapse project
    '''
    parser = argparse.ArgumentParser()
    parser.add_argument("--username", type=str, help="Synapse username")
    parser.add_argument("--password", type=str, help="Synapse password")
    parser.add_argument("--project", type=str, help="Synapse project")
    args = parser.parse_args()
    return args.username, args.password, args.project

def main():
    '''
    Push local updates to Synapse

    Parameters
    ----------
    None

    Returns
    -------
    None
    '''
    username, password, project = cli()
    push(username, password, project)

if __name__ == '__main__':
    main()