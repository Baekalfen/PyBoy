from .constants import ASCII_DELTA

def get_character_index(character):
    if character == ' ':
        return 0x7F
    if character == '?':
        return 0xE6
    if character == '!':
        return 0xE7
    if character == 'é':
        return 0xBA

    index = ord(character)
    if index > 47 and index < 58:
        # number
        return index + 197
    return index + ASCII_DELTA
