import PySimpleGUI as sg
import logging
import sys
from datetime import datetime
from configparser import ConfigParser
import os
from auto_mechop.runner import Runner

main_layout =[[sg.ReadFormButton('Setup', key='Setup'), sg.ReadFormButton('Submit', key='Submit'),
               sg.ReadFormButton('Release', key='Release'),sg.ReadFormButton('Report', key='Report'),
               sg.Text("Assignment name:"), sg.Input(key='-IN-')],
              [sg.Output(size=(100, 40), key='output')]]

window = sg.Window('AME 341 grading distribution').Layout(main_layout).Finalize()

log_path = '../logs'
if not os.path.exists(log_path):
    os.mkdir(log_path)
log_name = datetime.now().strftime('/%d_%m_%Y-%H_%M_%S')
logging.basicConfig(format='%(asctime)s,%(msecs)d %(levelname)s %(message)s',
                    datefmt='%H:%M:%S',
                    level=logging.DEBUG,
                    handlers=[
                        logging.FileHandler("{0}/{1}.logger".format(log_path, log_name)),
                    ])
logger = logging.getLogger()

h = logging.StreamHandler(window.FindElement('output').TKOut)
formatter = logging.Formatter('%(asctime)s - %(message)s', "%Y-%m-%d %H:%M:%S")
h.setFormatter(formatter)
h.setLevel(logging.INFO)
logger.addHandler(h)

logger.debug("Running GUI")

logger.debug("Parsing config file")
config = ConfigParser()
config.read("settings.ini")

logger.info('start mainloop')

def submit(args, config):
    runner = Runner()
    runner.run_submit_flow(args)


def release(args, config):
    runner = Runner()
    runner.run_release_flow(args)


def report(args, config):
    runner = Runner()
    runner.run_report_flow(args)


def clear(args, config):
    runner = Runner()
    runner.run_clear_flow(args)

while True:
    button, values = window.Read()
    if button and values:
        runner = Runner()
        if button == "Setup":
            logger.info("Running setup flow")
            # runner.run_setup_flow(args)

        if button == "Submit":
            if values['-IN-'] is not "":
                logger.info("Running submit flow for assignment {}".format(values['-IN-']))
                # runner.run_submit_flow(args)
            else:
                logger.info("Please set assignment name")

        if button == "Release":
            if values['-IN-'] is not "":
                logger.info("Running release flow for assignment {}".format(values['-IN-']))
                # runner.run_release_flow(args)
            else:
                logger.info("Please set assignment name")

        if button == "Report":
            if values['-IN-'] is not "":
                logger.info("Running report flow for assignment {}".format(values['-IN-']))
                # runner.run_release_flow(args)
            else:
                logger.info("Please set assignment name")
