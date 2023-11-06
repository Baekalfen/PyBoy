from enum import Enum

class Pokemon(Enum):
    RHYDON = 0x01
    KANGASKHAN = 0x02
    NIDORAN_M = 0x03
    CLEFAIRY = 0x04
    SPEAROW = 0x05
    VOLTORB = 0x06
    NIDOKING = 0x07
    SLOWBRO = 0x08
    IVYSAUR = 0x09
    EXEGGUTOR = 0x0A
    LICKITUNG = 0x0B
    EXEGGCUTE = 0x0C
    GRIMER = 0x0D
    GENGAR = 0x0E
    NIDORAN_F = 0x0F
    NIDOQUEEN = 0x10
    CUBONE = 0x11
    RHYHORN = 0x12
    LAPRAS = 0x13
    ARCANINE = 0x14
    MEW = 0x15
    GYARADOS = 0x16
    SHELLDER = 0x17
    TENTACOOL = 0x18
    GASTLY = 0x19
    SCYTHER = 0x1A
    STARYU = 0x1B
    BLASTOISE = 0x1C
    PINSIR = 0x1D
    TANGELA = 0x1E
    MISSINGNO_1F = 0x1F
    MISSINGNO_20 = 0x20
    GROWLITHE = 0x21
    ONIX = 0x22
    FEAROW = 0x23
    PIDGEY = 0x24
    SLOWPOKE = 0x25
    KADABRA = 0x26
    GRAVELER = 0x27
    CHANSEY = 0x28
    MACHOKE = 0x29
    MR_MIME = 0x2A
    HITMONLEE = 0x2B
    HITMONCHAN = 0x2C
    ARBOK = 0x2D
    PARASECT = 0x2E
    PSYDUCK = 0x2F
    DROWZEE = 0x30
    GOLEM = 0x31
    MISSINGNO_32 = 0x32
    MAGMAR = 0x33
    MISSINGNO_34 = 0x34
    ELECTABUZZ = 0x35
    MAGNETON = 0x36
    KOFFING = 0x37
    MISSINGNO_38 = 0x38
    MANKEY = 0x39
    SEEL = 0x3A
    DIGLETT = 0x3B
    TAUROS = 0x3C
    MISSINGNO_3D = 0x3D
    MISSINGNO_3E = 0x3E
    MISSINGNO_3F = 0x3F
    FARFETCHD = 0x40
    VENONAT = 0x41
    DRAGONITE = 0x42
    MISSINGNO_43 = 0x43
    MISSINGNO_44 = 0x44
    MISSINGNO_45 = 0x45
    DODUO = 0x46
    POLIWAG = 0x47
    JYNX = 0x48
    MOLTRES = 0x49
    ARTICUNO = 0x4A
    ZAPDOS = 0x4B
    DITTO = 0x4C
    MEOWTH = 0x4D
    KRABBY = 0x4E
    MISSINGNO_4F = 0x4F
    MISSINGNO_50 = 0x50
    MISSINGNO_51 = 0x51
    VULPIX = 0x52
    NINETALES = 0x53
    PIKACHU = 0x54
    RAICHU = 0x55
    MISSINGNO_56 = 0x56
    MISSINGNO_57 = 0x57
    DRATINI = 0x58
    DRAGONAIR = 0x59
    KABUTO = 0x5A
    KABUTOPS = 0x5B
    HORSEA = 0x5C
    SEADRA = 0x5D
    MISSINGNO_5E = 0x5E
    MISSINGNO_5F = 0x5F
    SANDSHREW = 0x60
    SANDSLASH = 0x61
    OMANYTE = 0x62
    OMASTAR = 0x63
    JIGGLYPUFF = 0x64
    WIGGLYTUFF = 0x65
    EEVEE = 0x66
    FLAREON = 0x67
    JOLTEON = 0x68
    VAPOREON = 0x69
    MACHOP = 0x6A
    ZUBAT = 0x6B
    EKANS = 0x6C
    PARAS = 0x6D
    POLIWHIRL = 0x6E
    POLIWRATH = 0x6F
    WEEDLE = 0x70
    KAKUNA = 0x71
    BEEDRILL = 0x72
    MISSINGNO_73 = 0x73
    DODRIO = 0x74
    PRIMEAPE = 0x75
    DUGTRIO = 0x76
    VENOMOTH = 0x77
    DEWGONG = 0x78
    MISSINGNO_79 = 0x79
    MISSINGNO_7A = 0x7A
    CATERPIE = 0x7B
    METAPOD = 0x7C
    BUTTERFREE = 0x7D
    MACHAMP = 0x7E
    MISSINGNO_7F = 0x7F
    GOLDUCK = 0x80
    HYPNO = 0x81
    GOLBAT = 0x82
    MEWTWO = 0x83
    SNORLAX = 0x84
    MAGIKARP = 0x85
    MISSINGNO_86 = 0x86
    MISSINGNO_87 = 0x87
    MUK = 0x88
    MISSINGNO_89 = 0x89
    KINGLER = 0x8A
    CLOYSTER = 0x8B
    MISSINGNO_8C = 0x8C
    ELECTRODE = 0x8D
    CLEFABLE = 0x8E
    WEEZING = 0x8F
    PERSIAN = 0x90
    MAROWAK = 0x91
    MISSINGNO_92 = 0x92
    HAUNTER = 0x93
    ABRA = 0x94
    ALAKAZAM = 0x95
    PIDGEOTTO = 0x96
    PIDGEOT = 0x97
    STARMIE = 0x98
    BULBASAUR = 0x99
    VENUSAUR = 0x9A
    TENTACRUEL = 0x9B
    MISSINGNO_9C = 0x9C
    GOLDEEN = 0x9D
    SEAKING = 0x9E
    MISSINGNO_9F = 0x9F
    MISSINGNO_A0 = 0xA0
    MISSINGNO_A1 = 0xA1
    MISSINGNO_A2 = 0xA2
    PONYTA = 0xA3
    RAPIDASH = 0xA4
    RATTATA = 0xA5
    RATICATE = 0xA6
    NIDORINO = 0xA7
    NIDORINA = 0xA8
    GEODUDE = 0xA9
    PORYGON = 0xAA
    AERODACTYL = 0xAB
    MISSINGNO_AC = 0xAC
    MAGNEMITE = 0xAD
    MISSINGNO_AE = 0xAE
    MISSINGNO_AF = 0xAF
    CHARMANDER = 0xB0
    SQUIRTLE = 0xB1
    CHARMELEON = 0xB2
    WARTORTLE = 0xB3
    CHARIZARD = 0xB4
    MISSINGNO_B5 = 0xB5
    FOSSIL_KABUTOPS = 0xB6
    FOSSIL_AERODACTYL = 0xB7
    MON_GHOST = 0xB8
    ODDISH = 0xB9
    GLOOM = 0xBA
    VILEPLUME = 0xBB
    BELLSPROUT = 0xBC
    WEEPINBELL = 0xBD
    VICTREEBEL = 0xBE

POKEMON_POKEDEX_INDEX = {
    Pokemon.BULBASAUR: 1,
    Pokemon.IVYSAUR:  2,
    Pokemon.VENUSAUR: 3,
    Pokemon.CHARMANDER: 4,
    Pokemon.CHARMELEON: 5,
    Pokemon.CHARIZARD: 6,
    Pokemon.SQUIRTLE: 7,
    Pokemon.WARTORTLE: 8,
    Pokemon.BLASTOISE: 9,
    Pokemon.CATERPIE: 10,
    Pokemon.METAPOD: 11,
    Pokemon.BUTTERFREE: 12,
    Pokemon.WEEDLE: 13,
    Pokemon.KAKUNA: 14,
    Pokemon.BEEDRILL: 15,
    Pokemon.PIDGEY: 16,
    Pokemon.PIDGEOTTO: 17,
    Pokemon.PIDGEOT: 18,
    Pokemon.RATTATA: 19,
    Pokemon.RATICATE: 20,
    Pokemon.SPEAROW: 21,
    Pokemon.FEAROW: 22,
    Pokemon.EKANS: 23,
    Pokemon.ARBOK: 24,
    Pokemon.PIKACHU: 25,
    Pokemon.RAICHU: 26,
    Pokemon.SANDSHREW: 27,
    Pokemon.SANDSLASH: 28,
    Pokemon.NIDORAN_F: 29,
    Pokemon.NIDORINA: 30,
    Pokemon.NIDOQUEEN: 31,
    Pokemon.NIDORAN_M: 32,
    Pokemon.NIDORINO: 33,
    Pokemon.NIDOKING: 34,
    Pokemon.CLEFAIRY: 35,
    Pokemon.CLEFABLE: 36,
    Pokemon.VULPIX: 37,
    Pokemon.NINETALES: 38,
    Pokemon.JIGGLYPUFF: 39,
    Pokemon.WIGGLYTUFF: 40,
    Pokemon.ZUBAT: 41,
    Pokemon.GOLBAT: 42,
    Pokemon.ODDISH: 43,
    Pokemon.GLOOM: 44,
    Pokemon.VILEPLUME: 45,
    Pokemon.PARAS: 46,
    Pokemon.PARASECT: 47,
    Pokemon.VENONAT: 48,
    Pokemon.VENOMOTH: 49,
    Pokemon.DIGLETT: 50,
    Pokemon.DUGTRIO: 51,
    Pokemon.MEOWTH: 52,
    Pokemon.PERSIAN: 53,
    Pokemon.PSYDUCK: 54,
    Pokemon.GOLDUCK: 55,
    Pokemon.MANKEY: 56,
    Pokemon.PRIMEAPE: 57,
    Pokemon.GROWLITHE: 58,
    Pokemon.ARCANINE: 59,
    Pokemon.POLIWAG: 60,
    Pokemon.POLIWHIRL: 61,
    Pokemon.POLIWRATH: 62,
    Pokemon.ABRA: 63,
    Pokemon.KADABRA: 64,
    Pokemon.ALAKAZAM: 65,
    Pokemon.MACHOP: 66,
    Pokemon.MACHOKE: 67,
    Pokemon.MACHAMP: 68,
    Pokemon.BELLSPROUT: 69,
    Pokemon.WEEPINBELL: 70,
    Pokemon.VICTREEBEL: 71,
    Pokemon.TENTACOOL: 72,
    Pokemon.TENTACRUEL: 73,
    Pokemon.GEODUDE: 74,
    Pokemon.GRAVELER: 75,
    Pokemon.GOLEM: 76,
    Pokemon.PONYTA: 77,
    Pokemon.RAPIDASH: 78,
    Pokemon.SLOWPOKE: 79,
    Pokemon.SLOWBRO: 80,
    Pokemon.MAGNEMITE: 81,
    Pokemon.MAGNETON: 82,
    Pokemon.FARFETCHD: 83,
    Pokemon.DODUO: 84,
    Pokemon.DODRIO: 85,
    Pokemon.SEEL: 86,
    Pokemon.DEWGONG: 87,
    Pokemon.GRIMER: 88,
    Pokemon.MUK: 89,
    Pokemon.SHELLDER: 90,
    Pokemon.CLOYSTER: 91,
    Pokemon.GASTLY: 92,
    Pokemon.HAUNTER: 93,
    Pokemon.GENGAR: 94,
    Pokemon.ONIX: 95,
    Pokemon.DROWZEE: 96,
    Pokemon.HYPNO: 97,
    Pokemon.KRABBY: 98,
    Pokemon.KINGLER: 99,
    Pokemon.VOLTORB: 100,
    Pokemon.ELECTRODE: 101,
    Pokemon.EXEGGCUTE: 102,
    Pokemon.EXEGGUTOR: 103,
    Pokemon.CUBONE: 104,
    Pokemon.MAROWAK: 105,
    Pokemon.HITMONLEE: 106,
    Pokemon.HITMONCHAN: 107,
    Pokemon.LICKITUNG: 108,
    Pokemon.KOFFING: 109,
    Pokemon.WEEZING: 110,
    Pokemon.RHYHORN: 111,
    Pokemon.RHYDON: 112,
    Pokemon.CHANSEY: 113,
    Pokemon.TANGELA: 114,
    Pokemon.KANGASKHAN: 115,
    Pokemon.HORSEA: 116,
    Pokemon.SEADRA: 117,
    Pokemon.GOLDEEN: 118,
    Pokemon.SEAKING: 119,
    Pokemon.STARYU: 120,
    Pokemon.STARMIE: 121,
    Pokemon.MR_MIME: 122,
    Pokemon.SCYTHER: 123,
    Pokemon.JYNX: 124,
    Pokemon.ELECTABUZZ: 125,
    Pokemon.MAGMAR: 126,
    Pokemon.PINSIR: 127,
    Pokemon.TAUROS: 128,
    Pokemon.MAGIKARP: 129,
    Pokemon.GYARADOS: 130,
    Pokemon.LAPRAS: 131,
    Pokemon.DITTO: 132,
    Pokemon.EEVEE: 133,
    Pokemon.VAPOREON: 134,
    Pokemon.JOLTEON: 135,
    Pokemon.FLAREON: 136,
    Pokemon.PORYGON: 137,
    Pokemon.OMANYTE: 138,
    Pokemon.OMASTAR: 139,
    Pokemon.KABUTO: 140,
    Pokemon.KABUTOPS: 141,
    Pokemon.AERODACTYL: 142,
    Pokemon.SNORLAX: 143,
    Pokemon.ARTICUNO: 144,
    Pokemon.ZAPDOS: 145,
    Pokemon.MOLTRES: 146,
    Pokemon.DRATINI: 147,
    Pokemon.DRAGONAIR: 148,
    Pokemon.DRAGONITE: 149,
    Pokemon.MEWTWO: 150,
    Pokemon.MEW: 151
}

POKEMON_NAMES = {
    Pokemon.BULBASAUR: "Bulbasaur",
    Pokemon.IVYSAUR: "Ivysaur",
    Pokemon.VENUSAUR: "Venusaur",
    Pokemon.CHARMANDER: "Charmander",
    Pokemon.CHARMELEON: "Charmeleon",
    Pokemon.CHARIZARD: "Charizard",
    Pokemon.SQUIRTLE: "Squirtle",
    Pokemon.WARTORTLE: "Wartortle",
    Pokemon.BLASTOISE: "Blastoise",
    Pokemon.CATERPIE: "Caterpie",
    Pokemon.METAPOD: "Metapod",
    Pokemon.BUTTERFREE: "Butterfree",
    Pokemon.CATERPIE: "Weedle",
    Pokemon.KAKUNA: "Kakuna",
    Pokemon.BEEDRILL: "Beedrill",
    Pokemon.PIDGEY: "Pidgey",
    Pokemon.PIDGEOTTO: "Pidgeotto",
    Pokemon.PIDGEOT: "Pidgeot",
    Pokemon.RATTATA: "Rattata",
    Pokemon.RATICATE: "Raticate",
    Pokemon.SPEAROW: "Spearow",
    Pokemon.FEAROW: "Fearow",
    Pokemon.EKANS: "Ekans",
    Pokemon.ARBOK: "Arbok",
    Pokemon.PIKACHU: "Pikachu",
    Pokemon.RAICHU: "Raichu",
    Pokemon.SANDSHREW: "Sandshrew",
    Pokemon.SANDSLASH: "Sandslash",
    Pokemon.NIDORAN_F: "Nidoran♀",
    Pokemon.NIDORINA: "Nidorina",
    Pokemon.NIDOQUEEN: "Nidoqueen",
    Pokemon.NIDORAN_M: "Nidoran♂",
    Pokemon.NIDORINO: "Nidorino",
    Pokemon.NIDOKING: "Nidoking",
    Pokemon.CLEFAIRY: "Clefairy",
    Pokemon.CLEFABLE: "Clefable",
    Pokemon.VULPIX: "Vulpix",
    Pokemon.NINETALES: "Ninetales",
    Pokemon.JIGGLYPUFF: "Jigglypuff",
    Pokemon.WIGGLYTUFF: "Wigglytuff",
    Pokemon.ZUBAT: "Zubat",
    Pokemon.GOLBAT: "Golbat",
    Pokemon.ODDISH: "Oddish",
    Pokemon.GLOOM: "Gloom",
    Pokemon.VILEPLUME: "Vileplume",
    Pokemon.PARAS: "Paras",
    Pokemon.PARASECT: "Parasect",
    Pokemon.VENONAT: "Venonat",
    Pokemon.VENOMOTH: "Venomoth",
    Pokemon.DIGLETT: "Diglett",
    Pokemon.DUGTRIO: "Dugtrio",
    Pokemon.MEOWTH: "Meowth",
    Pokemon.PERSIAN: "Persian",
    Pokemon.PSYDUCK: "Psyduck",
    Pokemon.GOLDUCK: "Golduck",
    Pokemon.MANKEY: "Mankey",
    Pokemon.PRIMEAPE: "Primeape",
    Pokemon.GROWLITHE: "Growlithe",
    Pokemon.ARCANINE: "Arcanine",
    Pokemon.POLIWAG: "Poliwag",
    Pokemon.POLIWHIRL: "Poliwhirl",
    Pokemon.POLIWRATH: "Poliwrath",
    Pokemon.ABRA: "Abra",
    Pokemon.KADABRA: "Kadabra",
    Pokemon.ALAKAZAM: "Alakazam",
    Pokemon.MACHOP: "Machop",
    Pokemon.MACHOKE: "Machoke",
    Pokemon.MACHAMP: "Machamp",
    Pokemon.BELLSPROUT: "Bellsprout",
    Pokemon.WEEPINBELL: "Weepinbell",
    Pokemon.VICTREEBEL: "Victreebel",
    Pokemon.TENTACOOL: "Tentacool",
    Pokemon.TENTACRUEL: "Tentacruel",
    Pokemon.GEODUDE: "Geodude",
    Pokemon.GRAVELER: "Graveler",
    Pokemon.GOLEM: "Golem",
    Pokemon.PONYTA: "Ponyta",
    Pokemon.RAPIDASH: "Rapidash",
    Pokemon.SLOWPOKE: "Slowpoke",
    Pokemon.SLOWBRO: "Slowbro",
    Pokemon.MAGNEMITE: "Magnemite",
    Pokemon.MAGNETON: "Magneton",
    Pokemon.FARFETCHD: "Farfetch’d",
    Pokemon.DODUO: "Doduo",
    Pokemon.DODRIO: "Dodrio",
    Pokemon.SEEL: "Seel",
    Pokemon.DEWGONG: "Dewgong",
    Pokemon.GRIMER: "Grimer",
    Pokemon.MUK: "Muk",
    Pokemon.SHELLDER: "Shellder",
    Pokemon.CLOYSTER: "Cloyster",
    Pokemon.GASTLY: "Gastly",
    Pokemon.HAUNTER: "Haunter",
    Pokemon.GENGAR: "Gengar",
    Pokemon.ONIX: "Onix",
    Pokemon.DROWZEE: "Drowzee",
    Pokemon.HYPNO: "Hypno",
    Pokemon.KRABBY: "Krabby",
    Pokemon.KINGLER: "Kingler",
    Pokemon.VOLTORB: "Voltorb",
    Pokemon.ELECTRODE: "Electrode",
    Pokemon.EXEGGCUTE: "Exeggcute",
    Pokemon.EXEGGUTOR: "Exeggutor",
    Pokemon.CUBONE: "Cubone",
    Pokemon.MAROWAK: "Marowak",
    Pokemon.HITMONLEE: "Hitmonlee",
    Pokemon.HITMONCHAN: "Hitmonchan",
    Pokemon.LICKITUNG: "Lickitung",
    Pokemon.KOFFING: "Koffing",
    Pokemon.WEEZING: "Weezing",
    Pokemon.RHYHORN: "Rhyhorn",
    Pokemon.RHYDON: "Rhydon",
    Pokemon.CHANSEY: "Chansey",
    Pokemon.TANGELA: "Tangela",
    Pokemon.KANGASKHAN: "Kangaskhan",
    Pokemon.HORSEA: "Horsea",
    Pokemon.SEADRA: "Seadra",
    Pokemon.GOLDEEN: "Goldeen",
    Pokemon.SEAKING: "Seaking",
    Pokemon.STARYU: "Staryu",
    Pokemon.STARMIE: "Starmie",
    Pokemon.MR_MIME: "Mr. Mime",
    Pokemon.SCYTHER: "Scyther",
    Pokemon.JYNX: "Jynx",
    Pokemon.ELECTABUZZ: "Electabuzz",
    Pokemon.MAGMAR: "Magmar",
    Pokemon.PINSIR: "Pinsir",
    Pokemon.TAUROS: "Tauros",
    Pokemon.MAGIKARP: "Magikarp",
    Pokemon.GYARADOS: "Gyarados",
    Pokemon.LAPRAS: "Lapras",
    Pokemon.DITTO: "Ditto",
    Pokemon.EEVEE: "Eevee",
    Pokemon.VAPOREON: "Vaporeon",
    Pokemon.JOLTEON: "Jolteon",
    Pokemon.FLAREON: "Flareon",
    Pokemon.PORYGON: "Porygon",
    Pokemon.OMANYTE: "Omanyte",
    Pokemon.OMASTAR: "Omastar",
    Pokemon.KABUTO: "Kabuto",
    Pokemon.KABUTOPS: "Kabutops",
    Pokemon.AERODACTYL: "Aerodactyl",
    Pokemon.SNORLAX: "Snorlax",
    Pokemon.ARTICUNO: "Articuno",
    Pokemon.ZAPDOS: "Zapdos",
    Pokemon.MOLTRES: "Moltres",
    Pokemon.DRATINI: "Dratini",
    Pokemon.DRAGONAIR: "Dragonair",
    Pokemon.DRAGONITE: "Dragonite",
    Pokemon.MEWTWO: "Mewtwo",
    Pokemon.MEW: "Mew",
}