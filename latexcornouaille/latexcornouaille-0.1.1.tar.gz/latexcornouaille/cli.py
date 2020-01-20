import codecs
import sys


# Liste des extensions des fichiers auxiliaires LaTeX
liste_ext = [".cor", ".bar", ".log", ".dvi", ".bbl", ".blg",
             ".out", ".ps", ".idx", ".ilg", ".ind", ".lof", ".lot"]


def main():
    rep = sys.argv[1]
    for fichier in os.listdir(rep):
        try:
            complet = rep + "/" + fichier
            (nom, extension) = os.path.splitext(fichier)
            if extension in liste_ext:
                os.remove(complet)
        except:
            print("Erreur")


if __name__ == '__main__':
    main()
