# -*- coding: utf-8 -*-
#!/usr/bin/env python

from lib.ExpressToken import lexer as lexer


###############################################
#针对字典的表达式取值
###############################################









class CDictExpressParse():
    def __init__(self):
        pass


    def get(self,dc,exp):

        lttok = []

        lexer.input(exp)
        while True:
            tok = lexer.token()
            if not tok:
                break      # No more input
            # print(tok)
            lttok.append(tok)


        node = dc

        blist = False

        for tok in lttok:
            if tok.type == 'ID':
                name = tok.value
                node = node[name]
                pass
            elif tok.type == 'PERIOD':
                pass
            elif tok.type == 'LBRACKET':
                blist = True
                pass
            elif tok.type == 'RBRACKET':
                blist = False
                pass
            elif tok.type == 'VAL_INTEGER':
                if blist == True:
                    name = int(tok.value)
                    node = node[name]
                else:
                    name = (tok.value)
                    node = node[name]
                pass

        val = node
        return val

        pass


    def set(self,dc,exp,val):
        lttok = []

        lexer.input(exp)
        while True:
            tok = lexer.token()
            if not tok:
                break  # No more input
            # print(tok)
            lttok.append(tok)

        xpath = ''
        name = ''
        blist = False

        for tok in lttok:
            if tok.type == 'ID':
                name = tok.value
                pass
            elif tok.type == 'PERIOD':
                if name <> '':
                    xpath += '["' + name + '"]'
                    name = ''
                pass
            elif tok.type == 'LBRACKET':
                if name <> '':
                    xpath += '["' + name + '"]'
                    name = ''
                xpath += '['
                blist = True
                pass
            elif tok.type == 'RBRACKET':
                xpath += ']'
                name = ''
                blist = False
                pass
            elif tok.type == 'VAL_INTEGER':
                xpath += str(tok.value)

        if name <> '':
            xpath += '["' + name + '"]'
            name = ''
        # print xpath
        code = 'dc' + xpath + '=' + 'val'
        # print code
        exec(code)
        # print dc
        return dc

# #
# parse = CDictExpressParse()
#
# tDC = {
#     'dd':'11',
#     'aa':{
#         'a':1,
#         'b':2,
#         'c':[
#             {
#                 'a':1,
#                 'b':1
#             },
#             {
#                 'a':1,
#                 'b':1
#             }
#         ]
#     }
# }
#
#
# exp = 'aa.c[1].a'
#
# print parse.get(tDC,exp)
#
#
# print parse.set(tDC,exp,2222)



