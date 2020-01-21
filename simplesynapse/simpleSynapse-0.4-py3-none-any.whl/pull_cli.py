#!/usr/bin/env python
from .run import pull
import argparse

def cli():
    parser = argparse.ArgumentParser()
    parser.add_argument("--username", type=str, help="Synapse username")
    parser.add_argument("--password", type=str, help="Synapse password")
    parser.add_argument("--project", type=str, help="Synapse project")
    args = parser.parse_args()
    return args.username, args.password, args.project

def main():
    username, password, project = cli()
    pull(username, password, project)

if __name__ == '__main__':
    main()