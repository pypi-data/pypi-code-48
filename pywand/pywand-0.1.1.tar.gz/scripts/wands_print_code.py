#! /usr/bin/env python3

from pywand.wandreader import WandInputReader

if __name__ == '__main__':
    reader = WandInputReader()

    print("Reading codes, press CTRL-C to stop")
    try:
        for i in reader.get_codes():
            print(i['wand'])
    except KeyboardInterrupt:
        reader.popen.terminate()
