from ..data.memory_addrs.battle import Battle

class Battle():

    def __init__(self, mem_addrs_to_track):

        self._mem_addrs_to_track = mem_addrs_to_track
        
        # ENEMY_MOVE_ID = (0xCFCC, 1)
        # ENEMY_MOVE_EFFECT = (0xCFCD, 1)
        # ENEMY_MOVE_POWER = (0xCFCE, 1)
        # ENEMY_MOVE_TYPE = (0xCFCF, 1)
        # ENEMY_MOVE_ACCURACY = (0xCFD0, 1)
        # ENEMY_MOVE_MAX_PP = (0xCFD1, 1)
        # PLAYER_MOVE_ID = (0xCFD2, 1)
        # PLAYER_MOVE_EFFECT = (0xCFD3, 1)
        # PLAYER_MOVE_POWER = (0xCFD4, 1)
        # PLAYER_MOVE_TYPE = (0xCFD5, 1)
        # PLAYER_MOVE_ACCURACY = (0xCFD6, 1)
        # PLAYER_MOVE_MAX_PP = (0xCFD7, 1)
        # ENEMY_POKEMON_ID = (0xCFD8, 1)
        # PLAYER_POKEMON_ID = (0xCFD9, 1)
        # ENEMY_NAME = (0xCFDA, 10)
        # # This seems to be a repat?
        # # ENEMY_POKEMON_ID = (0xCFE5, 1)
        # ENEMY_HP = (0xCFE6, 2)
        # ENEMY_LEVEL = (0xCFE8, 1)
        # ENEMY_STATUS = (0xCFE9, 1)
        # ENEMY_TYPE_1 = (0xCFEA, 1)
        # ENEMY_TPYE_2 = (0xCFEB, 1)
        # # ENEMY_CATCH_RATE_UNUSED only checked by move Transform
        # ENEMY_CATCH_RATE_UNUSED = (0xCFEC, 1)
        # ENEMY_MOVE_1 = (0xCFED, 1)
        # ENEMY_MOVE_2 = (0xCFEE, 1)
        # ENEMY_MOVE_3 = (0xCFEF, 1)
        # ENEMY_MOVE_4 = (0xCFF0, 1)
        # ENEMY_ATT_DEF_DVS = (0xCFF1, 1)
        # ENEMY_SPEED_SPEC_DVS = (0xCFF2, 1)
        # # Another repeat? 
        # # ENEMY_LEVEL = (0xCFEC)
        # ENEMY_MAX_HP = (0xCFF4, 2)
        # ENEMY_ATTACK = (0xCFF6, 2)
        # ENEMY_DEFENSE = (0xCFF8, 2)
        # ENEMY_SPEED = (0xCFFA, 2)
        # ENEMY_SPECIAL = (0xCFFC, 2)
        # ENEMY_MOVE_PP_1 = (0xCFFF, 1)
        # ENEMY_MOVE_PP_2 = (0xCFFF, 1)
        # ENEMY_MOVE_PP_3 = (0xD000, 1)
        # EMENY_MOVE_PP_4 = (0xD001, 1)
        # ENEMY_BASE_STATS = (0xD002, 5)
        # ENEMY_CATCH_RATE = (0xD007, 1)
        # ENEMY_BASE_EXP = (0xD008, 1)
        # TYPE_OF_BATTLE = (0xD057, 1)