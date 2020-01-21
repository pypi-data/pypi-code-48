#!/usr/bin/env python
from .run import pull
import argparse
"""
Program: pull_cli.py
Author: Andrew Blair and Robert Hu
Description: A command line interface for syncing Synapse to the local machine without overwriting local entitites
"""

def cli():
    '''
    Login command line interface 
    
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
    Pull Synapse to local machine

    Parameters
    ----------
    None

    Returns
    -------
    None
    '''
    username, password, project = cli()
    pull(username, password, project)

if __name__ == '__main__':
    main()