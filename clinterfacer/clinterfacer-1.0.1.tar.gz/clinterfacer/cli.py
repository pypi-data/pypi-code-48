#!/usr/bin/env python
# -*- coding: utf-8 -*-


"""cli.py: This python script implements the CommandLineInterface class."""


# standard library(ies)
import argparse
import importlib
import typing

# local source(s)
from clinterfacer.parser import Parser


class CommandLineInterface(object):

    def __init__(self: object, name) -> None:
        self.name = name
        self.parser = Parser(name)


    def parse(self: object, args: typing.List[str] = None) -> argparse.Namespace:
        return self.parser.parse(args)
        

    def main(self: object, args: typing.List[str] = None) -> int:
        args = self.parse(args)
        module = f'{self.name}.commands'
        if args.command:
            module += f'.{args.command}'.replace('-', '_')
        module = importlib.import_module(module)
        return module.main(args)
