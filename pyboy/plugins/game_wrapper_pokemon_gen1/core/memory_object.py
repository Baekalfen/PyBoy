class MemoryObject():

    _enum = {}
    _lookup = {}

    def __init__(self, fields_to_track):
        if fields_to_track is None:
            fields_to_track = [e for e in self._enum]
        self._fields_to_track = fields_to_track
        print(self._fields_to_track)
        self._data = {}

    def _load_field_from_memory(self, mem_manager, field_enum):
        self.data[field_enum] = mem_manager.read_memory_address(self._lookup[field_enum])

    def load_from_memory(self, mem_manager):
        for field_enum in self._fields_to_track:
            self._load_field_from_memory(mem_manager, field_enum)

    def get_value(self, k):
        return self._data.get(k)

