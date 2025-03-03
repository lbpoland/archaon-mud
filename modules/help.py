
HELP_DB = {
    'combat': 'Combat is inevitable in Faerûn. See "syntax tactics" for details.',
    'skills': 'Skills define your abilities. See "skills" for your list.',
    'inventory': 'Your inventory holds your gear. See "syntax inventory".',
    'cast': 'Wizards cast spells. See "syntax cast".',
    'perform': 'Priests perform rituals. See "syntax perform".',
    'colours': 'Colours enhance your display. See "syntax colours".'
}
def get_help(topic):
    return HELP_DB.get(topic, 'Try "help topics" for a list.')
