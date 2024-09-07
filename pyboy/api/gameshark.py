
class GameShark():
    def __init__(self, mb):
        '''
        This class allows for the conversion and usage of Gameshark codes. The cheats_path should
        point to a saved .txt file containing the codes with the following format a name for the code and the code itself seperated by a space:
        {code_name} {code}

        Ex. 
        NoWildEncounters 01033CD1
        '''
        self.mb = mb
        self.cheats_path = None
        self.cheats = {}
        self.cheats_enabled = False

    def _get_cheats(self, _is_path):
        if _is_path == True:
            with open(self.cheats_path, 'r') as f:
                lines = f.readlines()
                for line in lines:
                    parts = line.strip().split()
                    cheat_name, gameshark_code = parts[0], parts[1]
                    self._convert_cheat(cheat_name, gameshark_code)
        else:
            parts = self.cheats_path.strip().split()
            if len(parts) == 2:
                    cheat_name, gameshark_code = parts[0], parts[1]
                    self._convert_cheat(cheat_name, gameshark_code)
            elif len(parts) == 1:
                cheat_name = ''
                gameshark_code = parts[0]
                self._convert_cheat(cheat_name, gameshark_code)
            else:
                raise ValueError("invalid code or path")




    def _convert_cheat(self, cheat_name: str, gameshark_code: str):
        '''
        A GameShark code for these consoles is written in the format ttvvaaaa. tt specifies the code type and VRAM bank, which is usually 01. vv specifies the hexadecimal value the code will write into the game's memory. aaaa specifies the memory address that will be modified, with the low byte first (e.g. address C056 is written as 56C0).
        Example 011556C0 would output:
        location = 01
        value = 0x15
        address = 0x56C0
        '''
        # Check if the input cheat code has the correct length (8 characters)
        if len(gameshark_code) != 8:
            raise ValueError("Invalid cheat code length. Cheat code must be 8 characters long.")

        # Extract components from the cheat code
        code_type = gameshark_code[:2]
        value = int((f'0x{gameshark_code[2:4]}'), 16)  # Convert hexadecimal value to an integer
        unconverted_address = gameshark_code[4:]  # Ex:   1ED1
        lower = unconverted_address[:2]  # Ex:  1E
        upper = unconverted_address[2:]  # Ex:  D1
        address_converted = '0x' + upper + lower   # Ex: 0xD11E   # Converting to Ram Readable address 
        address = int(address_converted, 16)

        # Format the output
        formatted_output = {
            'location': code_type,
            'value': value,
            'address': address
        }
        self.cheats[cheat_name] = formatted_output



    def _update_codes(self, _is_path):
        self.cheats = {}
        self._get_cheats(_is_path)

    def set_cheats_path(self, cheats_path, _is_path):
        '''
        Sets the path to the .txt file containing the cheat codes if _is_path = True.
        If _is_path = False then the cheat code can be passed directly.
        The cheats_path should
        point to a saved .txt file containing the codes with one code per line formatted with a name for the code and the code itself seperated by a space:
        {code_name} {code}

        Ex. 
        NoWildEncounters 01033CD1
        InfiniteMoney 019947D3
        '''
        self.cheats_enabled = True
        self.cheats_path = cheats_path
        if self.cheats_path != None:
            self._update_codes(_is_path)
        else:
            raise ValueError('Error: Cheat code path not set!')

        return self.cheats_enabled

    def run_cheats(self, cheats_path, _is_path: True):
        '''
        Run this function on Tick to have the codes run in-game, as well as allowing
        for the change of cheats at runtime by modifying the {cheat_path.txt} file. 
        Ensure to save the {cheat_path.txt} file after modifications.
        '''
        self.cheats_enabled = self.set_cheats_path(cheats_path, _is_path)
        if self.cheats_enabled:
            for key in self.cheats.keys():
                if key in self.cheats:
                    cheat = self.cheats[key]
                    address = cheat['address']
                    value = cheat['value']
                    self.mb.setitem(address, value)

                    raise ValueError("cheat implemented!")
                else:
                    raise ValueError(f"Cheat '{key}' not found in the cheats database.")
        else:
            raise ValueError('Error: Need to run pyboy.set_cheats_path(cheat_path) to set the path of the cheat codes file.')
    
    
