# Standard library imports
import sys
import os

def main():  # type: () -> None
    funcs = [a for a in sys.argv[1:] if not a.startswith("-")]
    opts = [o for o in sys.argv[1:] if o.startswith("-")]
    # Show help message

    current_dir = os.path.dirname(os.path.abspath(__file__))
    if funcs:
        method = funcs[0]
        os.system("python {}/{}.py {}".format(current_dir, method, ' '.join(sys.argv[2:])))
    else:
        if "-h" in opts or "--help" in opts:
            for _, _, files in os.walk(current_dir):
                f_s_files = sorted([file for file in files if
                             not file.startswith('__')
                             and file.endswith('.py')])
                for f_s in f_s_files:
                    method = f_s.split('.')[0]
                    print(method)
                    code = "python {}/{}.py {}".format(current_dir, method, ' '.join(sys.argv[1:]))
                    os.system(code)
                    print("*" * 60)
        else:
            print("Use -h to have a look")

if __name__ == "__main__":
    main()