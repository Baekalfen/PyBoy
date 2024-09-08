class GameShark:
    def __init__(self, mb):
        self.mb = mb
        self.cheats = {}

    def load_from_file(self, path):
        with open(path, 'r') as f:
            lines = f.readlines()
            for line in lines:
                parts = line.strip().split()
                cheat_name, gameshark_code = parts[0], parts[1]
                self._convert_cheat(cheat_name, gameshark_code)

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
        address_converted = '0x' + upper + lower  # Ex: 0xD11E   # Converting to Ram Readable address
        address = int(address_converted, 16)

        # Format the output
        formatted_output = {
            'location': code_type,
            'value': value,
            'address': address
        }
        self.cheats[cheat_name] = formatted_output

    def add_cheat(self, cheat_name, gameshark_code):
        self._convert_cheat(cheat_name, gameshark_code)

    def remove_cheat(self, cheat_name):
        if cheat_name in self.cheats:
            del self.cheats[cheat_name]

    def clear(self):
        self.cheats = {}

    def tick(self):
        for key in self.cheats.keys():
            cheat = self.cheats[key]
            address = cheat['address']
            value = cheat['value']
            self.mb.setitem(address, value)
