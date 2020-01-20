#! /usr/bin/env python3

from ha_magiwand import HomeAssistantWands

if __name__ == '__main__':

    myclass = HomeAssistantWands()

    try:
        myclass.run()
    except KeyboardInterrupt:
        myclass.wandreader.popen.terminate()
