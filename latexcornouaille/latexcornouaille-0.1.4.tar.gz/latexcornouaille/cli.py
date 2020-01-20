import codecs
import os
import sys
import getopt





def usage():
    print('-h: --help: this message')
    print('-i , --input : input file')
    print('-f --foler: folder to clean')
    print('-a --all: keep only .tex and .pdf files')


def basic_clean(rep):
    liste_ext = [".cor", ".bar", ".log", ".dvi", ".bbl", ".blg",
             ".out", ".ps", ".idx", ".ilg", ".ind", ".lof", ".lot"]
    for fichier in os.listdir(rep):
        try:
            complet = rep + "/" + fichier
            (nom, extension) = os.path.splitext(fichier)
            if extension in liste_ext:
                os.remove(complet)
        except:
            print("Erreur")
def process_file(file):
    pass


def deep_clean(rep):
    liste_ext=[".cor",".bar",".aux",".log",".dvi"
           ,".bbl",".blg",".out",".synctex"
           ,".ps",".toc",".lua",".lub",".tab"
           ,".idx",".ilg",".ind",".lof",".lot"]
    try:
        if rep ==".":
            list_files = os.listdir()
        else:
            list_files = os.listdir(rep)
        for fichier in os.listdir(rep):
            try:
                complet = rep + "/" + fichier
                (nom, extension) = os.path.splitext(fichier)
                if extension in liste_ext:
                    os.remove(complet)
            except:
                print("Erreur")
    except:
        print('Erreur')
    

def main():
    argv = sys.argv[1:]
    try:
        opts, args = getopt.getopt(
            argv, "ha:i:f:", ["help", "all=", "input=", "folder="])
        for opt, arg in opts:
            if opt == '-h':
                usage()
            elif opt == '-f':
                basic_clean(arg)
            elif opt == '-i':
                process_file(arg)
            elif opt == '-a':
                deep_clean(arg)

    except getopt.GetoptError:
        usage()
        sys.exit(2)


if __name__ == '__main__':
    main()
