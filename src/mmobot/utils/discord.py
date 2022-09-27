def handle_mentions(given_name, mentioned_members):
    if not (given_name.startswith('<@') and given_name.endswith('>')):
        return given_name
    mention_id = given_name[2:-1]
    for member in mentioned_members:
        if mention_id == str(member.id):
            return member.nick
    return given_name