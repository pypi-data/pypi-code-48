def add_app(appname, destfile):
    new_line = '\n'
    with open(destfile, encoding='utf-8') as fs:
        content = fs.read().split(new_line)
    start = 'INSTALLED_APPS'
    end = ']'
    space = ' '
    index_start = None
    index_end = None
    for i, line in enumerate(content):
        if start in line:
            index_start = i
        elif index_start and end in line:
            index_end = i
            break
    if index_end:
        content.insert(index_end, space * 4 + f"f'{{MODULE_DIR.name}}.{appname}',")
        with open(destfile, 'w') as fsw:
            fsw.write(new_line.join(content))
        return
    print('failed!')
