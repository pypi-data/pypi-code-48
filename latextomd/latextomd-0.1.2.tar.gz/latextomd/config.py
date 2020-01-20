DEFAULT_OPTIONS = {
    'remove_comments': True,
    'strip_lines': True
}

# Replace without regex
replace_simple = [
    ['\n$$', '\n$$\n'],
    ['$$\n', '\n$$\n'],
    [r'\[', '\n$$\n'],
    [r'\]', '\n$$\n'],
]

# Deleted with TexSoup
del_commands = ['vspace',
                'Bareme',
                'cornouaille',
                'renewcommand',
                'setbar',
                'esp',
                'encadre',
                'ref',
                'arraycolsep',
                'label',
                'renewcommand',
                'hspace',
                'parindent',
                'raisebox',
                'rhead',
                'lhead',
                'lfoot',
                'rfoot',
                'addtolength',
                'pagestyle',
                'thispagestyle',
                'marginpar',
                'newpage',
                'hfill',
                'medskip',
                'bigskip',
                'smallskip',
                'setlength',
                'decofourleft',
                'footrulewidth',
                'decofourright'
                ]

del_environnements = [r'\begin{center}', r'\end{center}']

del_blocks = ['center']

replace_commands = [['chapter', '# S_T_R'],
                    ['section', '## S_T_R'],
                    ['subsection', '### S_T_R'],
                    ['textbf', '**S_T_R**'],
                    ['textsc', 'S_T_R'],
                    ['emph', '_S_T_R_'],
                    ['Large', 'S_T_R']
                   ]

math_sub = [[r"\\np\{((?P<arg>.*?))\}",r'\1'],
[r"\\vect\{((?P<arg>.*?))\}", r"\\overrightarrow{\1}"]]
