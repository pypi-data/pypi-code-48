import sys
def print_lol(prtlist,indent=False,level=0,fh=sys.stdout):
    for item in prtlist:
        if isinstance(item,list):
            print_lol(item,indent,level+1,fh)
        else:
            if indent:
                for tab_stop in range(level):
                    print("\t",end="",file=fh)
            print(item,file=fh)

