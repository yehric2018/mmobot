def is_mention(name):
    return name.startswith('<@') and name.endswith('>') and name[2:-1].isnumeric()
