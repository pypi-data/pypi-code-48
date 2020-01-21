

reserved = {}

tokens = [
             # Literals (identifier, integer constant, float constant, string constant, char const)
             'ID',

             # NUMBER
             'VAL_INTEGER', 'VAL_FLOAT', 'VAL_STRING', 'VAL_CHARACTER',

             # Assignment (=, *=, /=, %=, +=, -=, <<=, >>=, &=, ^=, |=)
             'EQUALS',

             # COMMENT
             'COMMENT',

             # Delimeters ( ) [ ] { } , . ; :
             'LPAREN', 'RPAREN',
             'LBRACKET', 'RBRACKET',
             'LBRACE', 'RBRACE',
             'COMMA', 'PERIOD', 'SEMI', 'COLON',

             # Ellipsis (...)
             'ELLIPSIS',

             # DOTDOT
             'DOTDOT',

             # ADDRESS
             'ADDRESS',

         ]

# Operators


# Assignment operators

t_EQUALS = r':='

# Increment/decrement


# ->


# ?


# Delimeters
t_LPAREN = r'\('
t_RPAREN = r'\)'
t_LBRACKET = r'\['
t_RBRACKET = r'\]'
t_LBRACE = r'\{'
t_RBRACE = r'\}'
t_COMMA = r','
t_PERIOD = r'\.'
t_SEMI = r';'
t_COLON = r':'
t_ELLIPSIS = r'\.\.\.'

# t_ID = r'[A-Za-z_][A-Za-z0-9_]*'

# Integer literal
t_VAL_INTEGER = r'\d+([uU]|[lL]|[uU][lL]|[lL][uU])?'

# Floating literal
t_VAL_FLOAT = r'((\d+)(\.\d+)(e(\+|-)?(\d+))? | (\d+)e(\+|-)?(\d+))([lL]|[fF])?'

# String literal
t_VAL_STRING = r'\"([^\\\n]|(\\.))*?\"'

# Character constant 'c' or L'c'
t_VAL_CHARACTER = r'(L)?\'([^\\\n]|(\\.))*?\''

# OUTPUT
t_DOTDOT = r'\.\.'

t_ADDRESS = r'%'


# Identifiers
def t_ID(t):
    r'[a-zA-Z_][a-zA-Z_0-9]*'
    t.type = reserved.get(t.value, 'ID')  # Check for reserved words
    return t


# Comment (C-Style)
def t_COMMENT(t):
    r'\(\*(.|\n)*?\*\)'
    t.lexer.lineno += t.value.count('\n')
    return t


# Comment (C++-Style)
def t_CPPCOMMENT(t):
    r'//.*\n'
    t.lexer.lineno += 1
    return t


# Ignored characters
t_ignore = " \t"


def t_newline(t):
    r'\n+'
    t.lexer.lineno += t.value.count("\n")


def t_error(t):
    print("Illegal character '%s'" % t.value[0])
    t.lexer.skip(1)


# Build the lexer
import ply.lex as lex

lexer = lex.lex(debug=False)

# Parsing rules

# exp = 'dd.aa.c[1].a'
# #
# lexer.input(exp)
# while True:
#     tok = lexer.token()
#     if not tok:
#         break      # No more input
#     print(tok)