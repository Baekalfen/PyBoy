from ..data.memory_addrs.pokemon import PokemonBaseAddrs, PokemonOffsets
from ..data.constants.pokemon import PokemonIds, _POKEMON_NAMES, _POKEMON_POKEDEX_INDEX
from .move import Move

class Pokemon:

    def __init__(self,
                 pokemon_id,
                 current_hp,
                 status,
                 type_1,
                 type_2,
                 catch_rate,
                 move_1,
                 move_2,
                 move_3,
                 move_4,
                 trainer_id,
                 experience,
                 hp_ev,
                 attack_ev,
                 defense_ev,
                 speed_ev,
                 special_ev,
                 attack_defense_iv,
                 speed_special_iv,
                 pp_move_1,
                 pp_move_2,
                 pp_move_3,
                 pp_move_4,
                 level,
                 max_hp,
                 attack,
                 defense,
                 speed,
                 special):
        self.pokemon_id = pokemon_id
        self.current_hp = current_hp
        self.status = status
        self.type_1 = type_1
        self.type_2 = type_2
        self.catch_rate = catch_rate
        self.moves = [move_1, move_2, move_3, move_4]
        self.trainer_id = trainer_id
        self.experience = experience
        self.hp_ev = hp_ev
        self.attack_ev = attack_ev
        self.defense_ev = defense_ev
        self.speed_ev = speed_ev
        self.special_ev = special_ev
        self.attack_defense_iv = attack_defense_iv
        self.speed_special_iv = speed_special_iv
        self.pp_move_1 = pp_move_1
        self.pp_move_2 = pp_move_2
        self.pp_move_3 = pp_move_3
        self.pp_move_4 = pp_move_4
        self.level = level
        self.max_hp = max_hp
        self.attack = attack
        self.defense = defense
        self.speed = speed
        self.special = special

    @property
    def name(self):
        return Pokemon.get_pokemon_name_from_id(self.pokemon_id)
    
    @property
    def move_1(self):
        return self.moves[0]
    
    @property
    def move_2(self):
        return self.moves[1]
    
    @property
    def move_3(self):
        return self.moves[2]
    
    @property
    def move_4(self):
        return self.moves[3]
    
    @staticmethod
    def get_pokemon_name_from_id(pokemon_id):
        return _POKEMON_NAMES.get(PokemonIds(pokemon_id))

    @staticmethod
    def get_pokedex_id_from_pokemon_id(pokemon_id):
        return _POKEMON_POKEDEX_INDEX.get(PokemonIds(pokemon_id))

    
    @staticmethod
    def _load_pokemon_from_address(pyboy, pokemon_base_address):

        pokemon_values = []

        for offset_enum in PokemonOffsets:
            offset, num_bytes = offset_enum.value[0], offset_enum.value[1]
            memory_value = pyboy.get_memory_value(pokemon_base_address+offset, num_bytes)
            pokemon_values.append(memory_value)

        return Pokemon(*pokemon_values)
    
    @classmethod
    def load_pokemon_from_party(cls, pyboy, party_location):
        # party_location goes from 1 to 6
        pokemon_base_address = list(PokemonBaseAddrs)[party_location-1].value
        return cls._load_pokemon_from_address(pyboy, pokemon_base_address)
    
    def _generate_move_str(self):
        s = f"Moves:\n" + \
            f"\t{Move.get_name_from_id(self.move_1)} ({self.pp_move_1}/)\n" + \
            f"\t{Move.get_name_from_id(self.move_2)} ({self.pp_move_2}/)\n" + \
            f"\t{Move.get_name_from_id(self.move_3)} ({self.pp_move_3}/)\n" + \
            f"\t{Move.get_name_from_id(self.move_4)} ({self.pp_move_4}/)\n"
        
        return s
    
    def _generate_stat_str(self):

        s = f"Stats:\n" + \
            f"\tHP: {self.max_hp}\n" + \
            f"\tAttack: {self.attack}\n" + \
            f"\tDefense: {self.defense}\n" + \
            f"\tSpeed: {self.speed}\n" + \
            f"\tSpecial: {self.special}\n" 

    def pretty_stringify(self):
        s = f"{self.name}\n" + self._generate_stats_str() + self._generate_move_str() 
        return s