from .utils import s
from os.path import getsize
from os import listdir
import math
import sys
import time


class Builder:
    parts = []
    part_sizes = []

    def __init__(self, file, output="./"):
        self.file = file
        self.file_name = file.split("/")[-1]

        if not output.endswith("/"):
            self.output = output + "/"
        else:
            self.output = output

    def build(self):
        start_time = time.time()

        print("[*] Searching for parts...")

        files = listdir(self.output)
        for file in files:
            if file.startswith(self.file_name) and file.endswith(".part"):
                self.parts.append(file)
                self.part_sizes.append(getsize(self.output+file))

        self.parts.sort()
        self.part_sizes.sort()
        part_size = self.part_sizes[-1]
        last_part_size = self.part_sizes[0]
        
        print("[*] Found (" + str(len(self.parts)) + ") parts")
        print()
        print("[*] File name:     " + self.file_name)
        print("[*] File parts:    " + str(self.part_sizes.count(part_size)) + " × [" + str(part_size) + " {}]".format(s("byte", part_size)) + " + [" + str(last_part_size) + " {}]".format(s("byte", last_part_size)))
        print("[*] Output folder: " + self.output)

        dst = open(self.output + self.file, "wb")

        for i, part_file in enumerate(self.parts):
            src = open(self.output + part_file, "rb")
            part = src.read()
            src.close()

            write_start = time.time()
            dst.write(part)
        
            write_size = len(part)
            write_time = time.time() - write_start
            write_speed = round(write_size / 1024**2 / write_time * 10) / 10
            progress = round((i+1)/len(self.parts)*100)
            
            print("\b" * 164, end="")
            print("[*] Writing... [" + "=" * progress + ">" + "." * (100-progress) + "] " + str(progress) + " %" + " | " + str(write_speed) + " MB/s          ", end="", flush=True)
            #print("[*] Wrote " + str(write_size) + " {} (part ".format(s("byte", write_size)) + str(i + 1) + ")")
            
            part = b"" # Clears part data from memory
            
            time.sleep(0.01)

        dst.close()
        end_time = time.time()
        proc_time = end_time - start_time
        
        print()
        print("[*] Done. Took: " + str(round(proc_time*10)/10) + " seconds")
