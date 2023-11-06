from ..data.moves.constants import MoveIds

class Move():

    def __init__(self, move_id):
        pass

    # We can cheat with just using the enum name as the move name
    # since there is no move that has any special characters in it
    @staticmethod
    def get_name_from_id(move_id, camel_case=False):
        move_name = MoveIds(move_id).name.replace('_', ' ')
        if camel_case:
            return move_name.title()
        return move_name