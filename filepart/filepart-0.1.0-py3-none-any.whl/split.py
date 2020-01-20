from .utils import s
from os.path import getsize
import math
import sys
import time

class Splitter:
    part_sizes = []

    def __init__(self, file, parts, output="./"):
        file = file.replace("\\","/")
        self.file = file
        self.file_name = file.split("/")[-1]
        self.parts = parts

        if not output.endswith("/"):
            self.output = output + "/"
        else:
            self.output = output

    def split(self):
        start_time = time.time()
        size = self.file_size()

        print("[*] File name:     " + self.file_name)
        print("[*] File parts:    " + self.parts["formatted"])

        if self.parts["size_in_bytes"] != 0:
            part_size = int(self.parts["size_in_bytes"])
            part_count = math.ceil(round(size / part_size * 10) / 10)
            try:
                last_part_size = int(size % (part_size * (part_count - 1)))
            except:
                print("[!] You must give a smaller part size.")
                sys.exit(2)

            if last_part_size > 0:
                self.part_sizes = [part_size] * (part_count - 1)
                self.part_sizes.append(last_part_size)
                print(" " * 19 + str(part_count-1) + " × [" + str(part_size) + " {}] + [".format(s("byte", part_size)) + str(last_part_size) + " {}]".format(s("byte", last_part_size)))
            else:
                if part_count > 0:
                    self.part_sizes = [part_size] * (part_count - 1)
                    print(" " * 19 + str(part_count) + " × [" + str(part_size) + " {}]".format(s("byte", part_size)))
                else:
                    print("[!] You must give a smaller value.")
                    sys.exit(2)

        else:
            part_count = int(self.parts["size"])
            part_size = round(size / part_count)

            if part_count * part_size != size:
                temp_size = part_count * part_size
                last_part_size = part_size + (size - temp_size)
                if part_size < 1 or last_part_size < 1:
                    print("[!] You must give fewer parts.")
                    sys.exit(2)
                self.part_sizes = [part_size] * (part_count - 1)
                self.part_sizes.append(last_part_size)
                print(" " * 19 + str(part_count-1) + " × [" + str(part_size) + " {}] + [".format(s("byte", part_size)) + str(last_part_size) + " {}]".format(s("byte", last_part_size)))    
            else:
                self.part_sizes = [part_size] * (part_count)
                print(" " * 19 + str(part_count) + " × [" + str(part_size) + " {}]".format(s("byte", part_size)))
        
        print("[*] Output folder: " + self.output)
        print()
        print("[*] Splitting " + self.file_name + "...")

        try:
            src = open(self.file, "rb")
        except FileNotFoundError:
            print("[!] Error: " + self.file_name + " does not exist")
            sys.exit(2)

        for i, part_size in enumerate(self.part_sizes):
            part = src.read(part_size)
            dst_file = self.output + self.file_name + "." + str(i + 1) + ".part"
            
            dst = open(dst_file, "wb")
            write_start = time.time()
            dst.write(part)
            dst.close()

            write_size = len(part)
            write_time = time.time() - write_start
            write_speed = round(write_size / 1024**2 / write_time * 10) / 10
            progress = round((i+1)/part_count*100)
            
            print("\b" * 164, end="")
            print("[*] Writing... [" + "=" * progress + ">" + "." * (100-progress) + "] " + str(progress) + " %" + " | " + str(write_speed) + " MB/s          ", end="", flush=True)
            #print("[*] Wrote " + str(write_size) + " {} (part ".format(s("byte", write_size)) + str(i + 1) + ")")
            
            part = b"" # Clears part data from memory
            time.sleep(0.01)

        src.close()
        end_time = time.time()
        proc_time = end_time - start_time
        
        print()
        print("[*] Done. Took: " + str(round(proc_time*10)/10) + " seconds")

    def file_size(self):
        return getsize(self.file)