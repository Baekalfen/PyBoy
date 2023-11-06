from ..data.constants.moves import MoveIds

class Move():

    NONEXISTENT_MOVE_STR = "---"

    def __init__(self, move_id):
        pass

    # We can cheat with just using the enum name as the move name
    # since there is no move that has any special characters in it
    @classmethod
    def get_name_from_id(cls, move_id, camel_case=False):
        if move_id == 0:
            return cls.NONEXISTENT_MOVE_STR
        move_name = MoveIds(move_id).name.replace('_', ' ')
        if camel_case:
            return move_name.title()
        return move_name