import os
import shutil
import argparse


def split_dir(path, remove):
    if not path:
        path = os.getcwd()
    files = os.listdir(path)
    for f in files:
        end = f.split(".")[-1]
        if not os.path.exists(path + "/" + end):
            os.makedirs(path + "/" + end)
        if remove:
            shutil.move(path + "/" + f, path + "/" + end)
        else:
            shutil.copy(path + "/" + f, path + "/" + end)

if __name__ == '__main__':
    description = """
    Split files to a new directory for same type
    Eg:
        norepeat split_dir -p=test
        before:
            dir
                a.txt
                b.txt
                a.png
                b.png
        after:
            dir
                a.txt
                b.txt
                a.png
                b.png
                txt
                    a.txt
                    b.txt
                png
                    a.png
                    b.png
    """
    parser = argparse.ArgumentParser(description=description,
                                     prog='split_dir',
                                     formatter_class=argparse.RawDescriptionHelpFormatter,
                                     )

    parser.add_argument('-p', '--path', help='dir path, default is current dir', default='')
    parser.add_argument('-r', '--remove', help='if remove old files, default is No', default='')

    args = parser.parse_args()
    try:
        split_dir(args.path, args.remove)
    except Exception as e:
        print(str(e))
        print('Use -h to have a try')
