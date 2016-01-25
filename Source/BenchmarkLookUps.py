import timeit
import random
import numpy

dummyOpcodes2 = [n for n in range(2)]*100


lookupNumArr2 = numpy.array([(lambda x: x**8) for i in range(2)])
lookupList2 = [(lambda x: x**8) for i in range(2)]
lookupTuple2 = tuple((lambda x: x**8) for i in range(2))

def testIf2(n):
    if n == 0:
        return 8**8
    elif n == 1:
        return 8**8


print "Test of long lookup tables (2)"
print timeit.repeat("for n in dummyOpcodes2: lookupList2[n](8)", "from __main__ import lookupList2, dummyOpcodes2", number=100)
print timeit.repeat("for n in dummyOpcodes2: lookupTuple2[n](8)", "from __main__ import lookupTuple2, dummyOpcodes2", number=100)
print timeit.repeat("for n in dummyOpcodes2: testIf2(n)", "from __main__ import testIf2, dummyOpcodes2", number=100)
print timeit.repeat("for n in dummyOpcodes2: lookupNumArr2[n](8)", "from __main__ import lookupNumArr2, dummyOpcodes2", number=100)


dummyOpcodes4 = [n for n in range(4)]*100

lookupNumArr4 = numpy.array([(lambda x: x**8) for i in range(4)])
lookupList4 = [(lambda x: x**8) for i in range(4)]
lookupTuple4 = tuple((lambda x: x**8) for i in range(4))

def testIf4(n):
    if n == 0:
        return 8**8
    elif n == 1:
        return 8**8
    elif n == 2:
        return 8**8
    elif n == 3:
        return 8**8


print "Test of long lookup tables (4)"
print timeit.repeat("for n in dummyOpcodes4: lookupList4[n](8)", "from __main__ import lookupList4, dummyOpcodes4", number=100)
print timeit.repeat("for n in dummyOpcodes4: lookupTuple4[n](8)", "from __main__ import lookupTuple4, dummyOpcodes4", number=100)
print timeit.repeat("for n in dummyOpcodes4: testIf4(n)", "from __main__ import testIf4, dummyOpcodes4", number=100)
print timeit.repeat("for n in dummyOpcodes4: lookupNumArr4[n](8)", "from __main__ import lookupNumArr4, dummyOpcodes4", number=100)


dummyOpcodes8 = [n for n in range(8)]*100

lookupNumArr8 = numpy.array([(lambda x: x**8) for i in range(8)])
lookupList8 = [(lambda x: x**8) for i in range(8)]
lookupTuple8 = tuple((lambda x: x**8) for i in range(8))

def testIf8(n):
    if n == 0:
        return 8**8
    elif n == 1:
        return 8**8
    elif n == 2:
        return 8**8
    elif n == 3:
        return 8**8
    elif n == 4:
        return 8**8
    elif n == 5:
        return 8**8
    elif n == 6:
        return 8**8
    elif n == 7:
        return 8**8


print "Test of long lookup tables (8)"
print timeit.repeat("for n in dummyOpcodes8: lookupList8[n](8)", "from __main__ import lookupList8, dummyOpcodes8", number=100)
print timeit.repeat("for n in dummyOpcodes8: lookupTuple8[n](8)", "from __main__ import lookupTuple8, dummyOpcodes8", number=100)
print timeit.repeat("for n in dummyOpcodes8: testIf8(n)", "from __main__ import testIf8, dummyOpcodes8", number=100)
print timeit.repeat("for n in dummyOpcodes8: lookupNumArr8[n](8)", "from __main__ import lookupNumArr8, dummyOpcodes8", number=100)


dummyOpcodes16 = [n for n in range(16)]*100

lookupNumArr16 = numpy.array([(lambda x: x**8) for i in range(16)])
lookupList16 = [(lambda x: x**8) for i in range(16)]
lookupTuple16 = tuple((lambda x: x**8) for i in range(16))

def testIf16(n):
    if n == 0:
        return 8**8
    elif n == 1:
        return 8**8
    elif n == 2:
        return 8**8
    elif n == 3:
        return 8**8
    elif n == 4:
        return 8**8
    elif n == 5:
        return 8**8
    elif n == 6:
        return 8**8
    elif n == 7:
        return 8**8
    elif n == 8:
        return 8**8
    elif n == 9:
        return 8**8
    elif n == 10:
        return 8**8
    elif n == 11:
        return 8**8
    elif n == 12:
        return 8**8
    elif n == 13:
        return 8**8
    elif n == 14:
        return 8**8
    elif n == 15:
        return 8**8


print "Test of long lookup tables (16)"
print timeit.repeat("for n in dummyOpcodes16: lookupList16[n](8)", "from __main__ import lookupList16, dummyOpcodes16", number=100)
print timeit.repeat("for n in dummyOpcodes16: lookupTuple16[n](8)", "from __main__ import lookupTuple16, dummyOpcodes16", number=100)
print timeit.repeat("for n in dummyOpcodes16: testIf16(n)", "from __main__ import testIf16, dummyOpcodes16", number=100)
print timeit.repeat("for n in dummyOpcodes16: lookupNumArr16[n](8)", "from __main__ import lookupNumArr16, dummyOpcodes16", number=100)


dummyOpcodes32 = [n for n in range(32)]*100

lookupNumArr32 = numpy.array([(lambda x: x**8) for i in range(32)])
lookupList32 = [(lambda x: x**8) for i in range(32)]
lookupTuple32 = tuple((lambda x: x**8) for i in range(32))

def testIf32(n):
    if n == 0:
        return 8**8
    elif n == 1:
        return 8**8
    elif n == 2:
        return 8**8
    elif n == 3:
        return 8**8
    elif n == 4:
        return 8**8
    elif n == 5:
        return 8**8
    elif n == 6:
        return 8**8
    elif n == 7:
        return 8**8
    elif n == 8:
        return 8**8
    elif n == 9:
        return 8**8
    elif n == 10:
        return 8**8
    elif n == 11:
        return 8**8
    elif n == 12:
        return 8**8
    elif n == 13:
        return 8**8
    elif n == 14:
        return 8**8
    elif n == 15:
        return 8**8
    elif n == 16:
        return 8**8
    elif n == 17:
        return 8**8
    elif n == 18:
        return 8**8
    elif n == 19:
        return 8**8
    elif n == 20:
        return 8**8
    elif n == 21:
        return 8**8
    elif n == 22:
        return 8**8
    elif n == 23:
        return 8**8
    elif n == 24:
        return 8**8
    elif n == 25:
        return 8**8
    elif n == 26:
        return 8**8
    elif n == 27:
        return 8**8
    elif n == 28:
        return 8**8
    elif n == 29:
        return 8**8
    elif n == 30:
        return 8**8
    elif n == 31:
        return 8**8


print "Test of long lookup tables (32)"
print timeit.repeat("for n in dummyOpcodes32: lookupList32[n](8)", "from __main__ import lookupList32, dummyOpcodes32", number=100)
print timeit.repeat("for n in dummyOpcodes32: lookupTuple32[n](8)", "from __main__ import lookupTuple32, dummyOpcodes32", number=100)
print timeit.repeat("for n in dummyOpcodes32: testIf32(n)", "from __main__ import testIf32, dummyOpcodes32", number=100)
print timeit.repeat("for n in dummyOpcodes32: lookupNumArr32[n](8)", "from __main__ import lookupNumArr32, dummyOpcodes32", number=100)



dummyOpcodes64 = [n for n in range(64)]*100

lookupNumArr64 = numpy.array([(lambda x: x**8) for i in range(64)])
lookupList64 = [(lambda x: x**8) for i in range(64)]
lookupTuple64 = tuple((lambda x: x**8) for i in range(64))

def testIf64(n):
    if n == 0:
        return 8**8
    elif n == 1:
        return 8**8
    elif n == 2:
        return 8**8
    elif n == 3:
        return 8**8
    elif n == 4:
        return 8**8
    elif n == 5:
        return 8**8
    elif n == 6:
        return 8**8
    elif n == 7:
        return 8**8
    elif n == 8:
        return 8**8
    elif n == 9:
        return 8**8
    elif n == 10:
        return 8**8
    elif n == 11:
        return 8**8
    elif n == 12:
        return 8**8
    elif n == 13:
        return 8**8
    elif n == 14:
        return 8**8
    elif n == 15:
        return 8**8
    elif n == 16:
        return 8**8
    elif n == 17:
        return 8**8
    elif n == 18:
        return 8**8
    elif n == 19:
        return 8**8
    elif n == 20:
        return 8**8
    elif n == 21:
        return 8**8
    elif n == 22:
        return 8**8
    elif n == 23:
        return 8**8
    elif n == 24:
        return 8**8
    elif n == 25:
        return 8**8
    elif n == 26:
        return 8**8
    elif n == 27:
        return 8**8
    elif n == 28:
        return 8**8
    elif n == 29:
        return 8**8
    elif n == 30:
        return 8**8
    elif n == 31:
        return 8**8
    elif n == 32:
        return 8**8
    elif n == 33:
        return 8**8
    elif n == 34:
        return 8**8
    elif n == 35:
        return 8**8
    elif n == 36:
        return 8**8
    elif n == 37:
        return 8**8
    elif n == 38:
        return 8**8
    elif n == 39:
        return 8**8
    elif n == 40:
        return 8**8
    elif n == 41:
        return 8**8
    elif n == 42:
        return 8**8
    elif n == 43:
        return 8**8
    elif n == 44:
        return 8**8
    elif n == 45:
        return 8**8
    elif n == 46:
        return 8**8
    elif n == 47:
        return 8**8
    elif n == 48:
        return 8**8
    elif n == 49:
        return 8**8
    elif n == 50:
        return 8**8
    elif n == 51:
        return 8**8
    elif n == 52:
        return 8**8
    elif n == 53:
        return 8**8
    elif n == 54:
        return 8**8
    elif n == 55:
        return 8**8
    elif n == 56:
        return 8**8
    elif n == 57:
        return 8**8
    elif n == 58:
        return 8**8
    elif n == 59:
        return 8**8
    elif n == 60:
        return 8**8
    elif n == 61:
        return 8**8
    elif n == 62:
        return 8**8
    elif n == 63:
        return 8**8


print "Test of long lookup tables (64)"
print timeit.repeat("for n in dummyOpcodes64: lookupList64[n](8)", "from __main__ import lookupList64, dummyOpcodes64", number=100)
print timeit.repeat("for n in dummyOpcodes64: lookupTuple64[n](8)", "from __main__ import lookupTuple64, dummyOpcodes64", number=100)
print timeit.repeat("for n in dummyOpcodes64: testIf64(n)", "from __main__ import testIf64, dummyOpcodes64", number=100)
print timeit.repeat("for n in dummyOpcodes64: lookupNumArr64[n](8)", "from __main__ import lookupNumArr64, dummyOpcodes64", number=100)


dummyOpcodes128 = [n for n in range(128)]*100

lookupNumArr128 = numpy.array([(lambda x: x**8) for i in range(128)])
lookupList128 = [(lambda x: x**8) for i in range(128)]
lookupTuple128 = tuple((lambda x: x**8) for i in range(128))

def testIf128(n):
    if n == 0:
        return 8**8
    elif n == 1:
        return 8**8
    elif n == 2:
        return 8**8
    elif n == 3:
        return 8**8
    elif n == 4:
        return 8**8
    elif n == 5:
        return 8**8
    elif n == 6:
        return 8**8
    elif n == 7:
        return 8**8
    elif n == 8:
        return 8**8
    elif n == 9:
        return 8**8
    elif n == 10:
        return 8**8
    elif n == 11:
        return 8**8
    elif n == 12:
        return 8**8
    elif n == 13:
        return 8**8
    elif n == 14:
        return 8**8
    elif n == 15:
        return 8**8
    elif n == 16:
        return 8**8
    elif n == 17:
        return 8**8
    elif n == 18:
        return 8**8
    elif n == 19:
        return 8**8
    elif n == 20:
        return 8**8
    elif n == 21:
        return 8**8
    elif n == 22:
        return 8**8
    elif n == 23:
        return 8**8
    elif n == 24:
        return 8**8
    elif n == 25:
        return 8**8
    elif n == 26:
        return 8**8
    elif n == 27:
        return 8**8
    elif n == 28:
        return 8**8
    elif n == 29:
        return 8**8
    elif n == 30:
        return 8**8
    elif n == 31:
        return 8**8
    elif n == 32:
        return 8**8
    elif n == 33:
        return 8**8
    elif n == 34:
        return 8**8
    elif n == 35:
        return 8**8
    elif n == 36:
        return 8**8
    elif n == 37:
        return 8**8
    elif n == 38:
        return 8**8
    elif n == 39:
        return 8**8
    elif n == 40:
        return 8**8
    elif n == 41:
        return 8**8
    elif n == 42:
        return 8**8
    elif n == 43:
        return 8**8
    elif n == 44:
        return 8**8
    elif n == 45:
        return 8**8
    elif n == 46:
        return 8**8
    elif n == 47:
        return 8**8
    elif n == 48:
        return 8**8
    elif n == 49:
        return 8**8
    elif n == 50:
        return 8**8
    elif n == 51:
        return 8**8
    elif n == 52:
        return 8**8
    elif n == 53:
        return 8**8
    elif n == 54:
        return 8**8
    elif n == 55:
        return 8**8
    elif n == 56:
        return 8**8
    elif n == 57:
        return 8**8
    elif n == 58:
        return 8**8
    elif n == 59:
        return 8**8
    elif n == 60:
        return 8**8
    elif n == 61:
        return 8**8
    elif n == 62:
        return 8**8
    elif n == 63:
        return 8**8
    elif n == 64:
        return 8**8
    elif n == 65:
        return 8**8
    elif n == 66:
        return 8**8
    elif n == 67:
        return 8**8
    elif n == 68:
        return 8**8
    elif n == 69:
        return 8**8
    elif n == 70:
        return 8**8
    elif n == 71:
        return 8**8
    elif n == 72:
        return 8**8
    elif n == 73:
        return 8**8
    elif n == 74:
        return 8**8
    elif n == 75:
        return 8**8
    elif n == 76:
        return 8**8
    elif n == 77:
        return 8**8
    elif n == 78:
        return 8**8
    elif n == 79:
        return 8**8
    elif n == 80:
        return 8**8
    elif n == 81:
        return 8**8
    elif n == 82:
        return 8**8
    elif n == 83:
        return 8**8
    elif n == 84:
        return 8**8
    elif n == 85:
        return 8**8
    elif n == 86:
        return 8**8
    elif n == 87:
        return 8**8
    elif n == 88:
        return 8**8
    elif n == 89:
        return 8**8
    elif n == 90:
        return 8**8
    elif n == 91:
        return 8**8
    elif n == 92:
        return 8**8
    elif n == 93:
        return 8**8
    elif n == 94:
        return 8**8
    elif n == 95:
        return 8**8
    elif n == 96:
        return 8**8
    elif n == 97:
        return 8**8
    elif n == 98:
        return 8**8
    elif n == 99:
        return 8**8
    elif n == 100:
        return 8**8
    elif n == 101:
        return 8**8
    elif n == 102:
        return 8**8
    elif n == 103:
        return 8**8
    elif n == 104:
        return 8**8
    elif n == 105:
        return 8**8
    elif n == 106:
        return 8**8
    elif n == 107:
        return 8**8
    elif n == 108:
        return 8**8
    elif n == 109:
        return 8**8
    elif n == 110:
        return 8**8
    elif n == 111:
        return 8**8
    elif n == 112:
        return 8**8
    elif n == 113:
        return 8**8
    elif n == 114:
        return 8**8
    elif n == 115:
        return 8**8
    elif n == 116:
        return 8**8
    elif n == 117:
        return 8**8
    elif n == 118:
        return 8**8
    elif n == 119:
        return 8**8
    elif n == 120:
        return 8**8
    elif n == 121:
        return 8**8
    elif n == 122:
        return 8**8
    elif n == 123:
        return 8**8
    elif n == 124:
        return 8**8
    elif n == 125:
        return 8**8
    elif n == 126:
        return 8**8
    elif n == 127:
        return 8**8


print "Test of long lookup tables (128)"
print timeit.repeat("for n in dummyOpcodes128: lookupList128[n](8)", "from __main__ import lookupList128, dummyOpcodes128", number=100)
print timeit.repeat("for n in dummyOpcodes128: lookupTuple128[n](8)", "from __main__ import lookupTuple128, dummyOpcodes128", number=100)
print timeit.repeat("for n in dummyOpcodes128: testIf128(n)", "from __main__ import testIf128, dummyOpcodes128", number=100)
print timeit.repeat("for n in dummyOpcodes128: lookupNumArr128[n](8)", "from __main__ import lookupNumArr128, dummyOpcodes128", number=100)


dummyOpcodes256 = [n for n in range(256)]*100

lookupNumArr256 = numpy.array([(lambda x: x**8) for i in range(256)])
lookupList256 = [(lambda x: x**8) for i in range(256)]
lookupTuple256 = tuple((lambda x: x**8) for i in range(256))

def testIf256(n):
    if n == 0:
        return 8**8
    elif n == 1:
        return 8**8
    elif n == 2:
        return 8**8
    elif n == 3:
        return 8**8
    elif n == 4:
        return 8**8
    elif n == 5:
        return 8**8
    elif n == 6:
        return 8**8
    elif n == 7:
        return 8**8
    elif n == 8:
        return 8**8
    elif n == 9:
        return 8**8
    elif n == 10:
        return 8**8
    elif n == 11:
        return 8**8
    elif n == 12:
        return 8**8
    elif n == 13:
        return 8**8
    elif n == 14:
        return 8**8
    elif n == 15:
        return 8**8
    elif n == 16:
        return 8**8
    elif n == 17:
        return 8**8
    elif n == 18:
        return 8**8
    elif n == 19:
        return 8**8
    elif n == 20:
        return 8**8
    elif n == 21:
        return 8**8
    elif n == 22:
        return 8**8
    elif n == 23:
        return 8**8
    elif n == 24:
        return 8**8
    elif n == 25:
        return 8**8
    elif n == 26:
        return 8**8
    elif n == 27:
        return 8**8
    elif n == 28:
        return 8**8
    elif n == 29:
        return 8**8
    elif n == 30:
        return 8**8
    elif n == 31:
        return 8**8
    elif n == 32:
        return 8**8
    elif n == 33:
        return 8**8
    elif n == 34:
        return 8**8
    elif n == 35:
        return 8**8
    elif n == 36:
        return 8**8
    elif n == 37:
        return 8**8
    elif n == 38:
        return 8**8
    elif n == 39:
        return 8**8
    elif n == 40:
        return 8**8
    elif n == 41:
        return 8**8
    elif n == 42:
        return 8**8
    elif n == 43:
        return 8**8
    elif n == 44:
        return 8**8
    elif n == 45:
        return 8**8
    elif n == 46:
        return 8**8
    elif n == 47:
        return 8**8
    elif n == 48:
        return 8**8
    elif n == 49:
        return 8**8
    elif n == 50:
        return 8**8
    elif n == 51:
        return 8**8
    elif n == 52:
        return 8**8
    elif n == 53:
        return 8**8
    elif n == 54:
        return 8**8
    elif n == 55:
        return 8**8
    elif n == 56:
        return 8**8
    elif n == 57:
        return 8**8
    elif n == 58:
        return 8**8
    elif n == 59:
        return 8**8
    elif n == 60:
        return 8**8
    elif n == 61:
        return 8**8
    elif n == 62:
        return 8**8
    elif n == 63:
        return 8**8
    elif n == 64:
        return 8**8
    elif n == 65:
        return 8**8
    elif n == 66:
        return 8**8
    elif n == 67:
        return 8**8
    elif n == 68:
        return 8**8
    elif n == 69:
        return 8**8
    elif n == 70:
        return 8**8
    elif n == 71:
        return 8**8
    elif n == 72:
        return 8**8
    elif n == 73:
        return 8**8
    elif n == 74:
        return 8**8
    elif n == 75:
        return 8**8
    elif n == 76:
        return 8**8
    elif n == 77:
        return 8**8
    elif n == 78:
        return 8**8
    elif n == 79:
        return 8**8
    elif n == 80:
        return 8**8
    elif n == 81:
        return 8**8
    elif n == 82:
        return 8**8
    elif n == 83:
        return 8**8
    elif n == 84:
        return 8**8
    elif n == 85:
        return 8**8
    elif n == 86:
        return 8**8
    elif n == 87:
        return 8**8
    elif n == 88:
        return 8**8
    elif n == 89:
        return 8**8
    elif n == 90:
        return 8**8
    elif n == 91:
        return 8**8
    elif n == 92:
        return 8**8
    elif n == 93:
        return 8**8
    elif n == 94:
        return 8**8
    elif n == 95:
        return 8**8
    elif n == 96:
        return 8**8
    elif n == 97:
        return 8**8
    elif n == 98:
        return 8**8
    elif n == 99:
        return 8**8
    elif n == 100:
        return 8**8
    elif n == 101:
        return 8**8
    elif n == 102:
        return 8**8
    elif n == 103:
        return 8**8
    elif n == 104:
        return 8**8
    elif n == 105:
        return 8**8
    elif n == 106:
        return 8**8
    elif n == 107:
        return 8**8
    elif n == 108:
        return 8**8
    elif n == 109:
        return 8**8
    elif n == 110:
        return 8**8
    elif n == 111:
        return 8**8
    elif n == 112:
        return 8**8
    elif n == 113:
        return 8**8
    elif n == 114:
        return 8**8
    elif n == 115:
        return 8**8
    elif n == 116:
        return 8**8
    elif n == 117:
        return 8**8
    elif n == 118:
        return 8**8
    elif n == 119:
        return 8**8
    elif n == 120:
        return 8**8
    elif n == 121:
        return 8**8
    elif n == 122:
        return 8**8
    elif n == 123:
        return 8**8
    elif n == 124:
        return 8**8
    elif n == 125:
        return 8**8
    elif n == 126:
        return 8**8
    elif n == 127:
        return 8**8
    elif n == 128:
        return 8**8
    elif n == 129:
        return 8**8
    elif n == 130:
        return 8**8
    elif n == 131:
        return 8**8
    elif n == 132:
        return 8**8
    elif n == 133:
        return 8**8
    elif n == 134:
        return 8**8
    elif n == 135:
        return 8**8
    elif n == 136:
        return 8**8
    elif n == 137:
        return 8**8
    elif n == 138:
        return 8**8
    elif n == 139:
        return 8**8
    elif n == 140:
        return 8**8
    elif n == 141:
        return 8**8
    elif n == 142:
        return 8**8
    elif n == 143:
        return 8**8
    elif n == 144:
        return 8**8
    elif n == 145:
        return 8**8
    elif n == 146:
        return 8**8
    elif n == 147:
        return 8**8
    elif n == 148:
        return 8**8
    elif n == 149:
        return 8**8
    elif n == 150:
        return 8**8
    elif n == 151:
        return 8**8
    elif n == 152:
        return 8**8
    elif n == 153:
        return 8**8
    elif n == 154:
        return 8**8
    elif n == 155:
        return 8**8
    elif n == 156:
        return 8**8
    elif n == 157:
        return 8**8
    elif n == 158:
        return 8**8
    elif n == 159:
        return 8**8
    elif n == 160:
        return 8**8
    elif n == 161:
        return 8**8
    elif n == 162:
        return 8**8
    elif n == 163:
        return 8**8
    elif n == 164:
        return 8**8
    elif n == 165:
        return 8**8
    elif n == 166:
        return 8**8
    elif n == 167:
        return 8**8
    elif n == 168:
        return 8**8
    elif n == 169:
        return 8**8
    elif n == 170:
        return 8**8
    elif n == 171:
        return 8**8
    elif n == 172:
        return 8**8
    elif n == 173:
        return 8**8
    elif n == 174:
        return 8**8
    elif n == 175:
        return 8**8
    elif n == 176:
        return 8**8
    elif n == 177:
        return 8**8
    elif n == 178:
        return 8**8
    elif n == 179:
        return 8**8
    elif n == 180:
        return 8**8
    elif n == 181:
        return 8**8
    elif n == 182:
        return 8**8
    elif n == 183:
        return 8**8
    elif n == 184:
        return 8**8
    elif n == 185:
        return 8**8
    elif n == 186:
        return 8**8
    elif n == 187:
        return 8**8
    elif n == 188:
        return 8**8
    elif n == 189:
        return 8**8
    elif n == 190:
        return 8**8
    elif n == 191:
        return 8**8
    elif n == 192:
        return 8**8
    elif n == 193:
        return 8**8
    elif n == 194:
        return 8**8
    elif n == 195:
        return 8**8
    elif n == 196:
        return 8**8
    elif n == 197:
        return 8**8
    elif n == 198:
        return 8**8
    elif n == 199:
        return 8**8
    elif n == 200:
        return 8**8
    elif n == 201:
        return 8**8
    elif n == 202:
        return 8**8
    elif n == 203:
        return 8**8
    elif n == 204:
        return 8**8
    elif n == 205:
        return 8**8
    elif n == 206:
        return 8**8
    elif n == 207:
        return 8**8
    elif n == 208:
        return 8**8
    elif n == 209:
        return 8**8
    elif n == 210:
        return 8**8
    elif n == 211:
        return 8**8
    elif n == 212:
        return 8**8
    elif n == 213:
        return 8**8
    elif n == 214:
        return 8**8
    elif n == 215:
        return 8**8
    elif n == 216:
        return 8**8
    elif n == 217:
        return 8**8
    elif n == 218:
        return 8**8
    elif n == 219:
        return 8**8
    elif n == 220:
        return 8**8
    elif n == 221:
        return 8**8
    elif n == 222:
        return 8**8
    elif n == 223:
        return 8**8
    elif n == 224:
        return 8**8
    elif n == 225:
        return 8**8
    elif n == 226:
        return 8**8
    elif n == 227:
        return 8**8
    elif n == 228:
        return 8**8
    elif n == 229:
        return 8**8
    elif n == 230:
        return 8**8
    elif n == 231:
        return 8**8
    elif n == 232:
        return 8**8
    elif n == 233:
        return 8**8
    elif n == 234:
        return 8**8
    elif n == 235:
        return 8**8
    elif n == 236:
        return 8**8
    elif n == 237:
        return 8**8
    elif n == 238:
        return 8**8
    elif n == 239:
        return 8**8
    elif n == 240:
        return 8**8
    elif n == 241:
        return 8**8
    elif n == 242:
        return 8**8
    elif n == 243:
        return 8**8
    elif n == 244:
        return 8**8
    elif n == 245:
        return 8**8
    elif n == 246:
        return 8**8
    elif n == 247:
        return 8**8
    elif n == 248:
        return 8**8
    elif n == 249:
        return 8**8
    elif n == 250:
        return 8**8
    elif n == 251:
        return 8**8
    elif n == 252:
        return 8**8
    elif n == 253:
        return 8**8
    elif n == 254:
        return 8**8
    elif n == 255:
        return 8**8


print "Test of long lookup tables (256)"
print timeit.repeat("for n in dummyOpcodes256: lookupList256[n](8)", "from __main__ import lookupList256, dummyOpcodes256", number=100)
print timeit.repeat("for n in dummyOpcodes256: lookupTuple256[n](8)", "from __main__ import lookupTuple256, dummyOpcodes256", number=100)
print timeit.repeat("for n in dummyOpcodes256: testIf256(n)", "from __main__ import testIf256, dummyOpcodes256", number=100)
print timeit.repeat("for n in dummyOpcodes256: lookupNumArr256[n](8)", "from __main__ import lookupNumArr256, dummyOpcodes256", number=100)


dummyOpcodes512 = [n for n in range(512)]*100

lookupNumArr512 = numpy.array([(lambda x: x**8) for i in range(512)])
lookupList512 = [(lambda x: x**8) for i in range(512)]
lookupTuple512 = tuple((lambda x: x**8) for i in range(512))

def testIf512(n):
    if n == 0:
        return 8**8
    elif n == 1:
        return 8**8
    elif n == 2:
        return 8**8
    elif n == 3:
        return 8**8
    elif n == 4:
        return 8**8
    elif n == 5:
        return 8**8
    elif n == 6:
        return 8**8
    elif n == 7:
        return 8**8
    elif n == 8:
        return 8**8
    elif n == 9:
        return 8**8
    elif n == 10:
        return 8**8
    elif n == 11:
        return 8**8
    elif n == 12:
        return 8**8
    elif n == 13:
        return 8**8
    elif n == 14:
        return 8**8
    elif n == 15:
        return 8**8
    elif n == 16:
        return 8**8
    elif n == 17:
        return 8**8
    elif n == 18:
        return 8**8
    elif n == 19:
        return 8**8
    elif n == 20:
        return 8**8
    elif n == 21:
        return 8**8
    elif n == 22:
        return 8**8
    elif n == 23:
        return 8**8
    elif n == 24:
        return 8**8
    elif n == 25:
        return 8**8
    elif n == 26:
        return 8**8
    elif n == 27:
        return 8**8
    elif n == 28:
        return 8**8
    elif n == 29:
        return 8**8
    elif n == 30:
        return 8**8
    elif n == 31:
        return 8**8
    elif n == 32:
        return 8**8
    elif n == 33:
        return 8**8
    elif n == 34:
        return 8**8
    elif n == 35:
        return 8**8
    elif n == 36:
        return 8**8
    elif n == 37:
        return 8**8
    elif n == 38:
        return 8**8
    elif n == 39:
        return 8**8
    elif n == 40:
        return 8**8
    elif n == 41:
        return 8**8
    elif n == 42:
        return 8**8
    elif n == 43:
        return 8**8
    elif n == 44:
        return 8**8
    elif n == 45:
        return 8**8
    elif n == 46:
        return 8**8
    elif n == 47:
        return 8**8
    elif n == 48:
        return 8**8
    elif n == 49:
        return 8**8
    elif n == 50:
        return 8**8
    elif n == 51:
        return 8**8
    elif n == 52:
        return 8**8
    elif n == 53:
        return 8**8
    elif n == 54:
        return 8**8
    elif n == 55:
        return 8**8
    elif n == 56:
        return 8**8
    elif n == 57:
        return 8**8
    elif n == 58:
        return 8**8
    elif n == 59:
        return 8**8
    elif n == 60:
        return 8**8
    elif n == 61:
        return 8**8
    elif n == 62:
        return 8**8
    elif n == 63:
        return 8**8
    elif n == 64:
        return 8**8
    elif n == 65:
        return 8**8
    elif n == 66:
        return 8**8
    elif n == 67:
        return 8**8
    elif n == 68:
        return 8**8
    elif n == 69:
        return 8**8
    elif n == 70:
        return 8**8
    elif n == 71:
        return 8**8
    elif n == 72:
        return 8**8
    elif n == 73:
        return 8**8
    elif n == 74:
        return 8**8
    elif n == 75:
        return 8**8
    elif n == 76:
        return 8**8
    elif n == 77:
        return 8**8
    elif n == 78:
        return 8**8
    elif n == 79:
        return 8**8
    elif n == 80:
        return 8**8
    elif n == 81:
        return 8**8
    elif n == 82:
        return 8**8
    elif n == 83:
        return 8**8
    elif n == 84:
        return 8**8
    elif n == 85:
        return 8**8
    elif n == 86:
        return 8**8
    elif n == 87:
        return 8**8
    elif n == 88:
        return 8**8
    elif n == 89:
        return 8**8
    elif n == 90:
        return 8**8
    elif n == 91:
        return 8**8
    elif n == 92:
        return 8**8
    elif n == 93:
        return 8**8
    elif n == 94:
        return 8**8
    elif n == 95:
        return 8**8
    elif n == 96:
        return 8**8
    elif n == 97:
        return 8**8
    elif n == 98:
        return 8**8
    elif n == 99:
        return 8**8
    elif n == 100:
        return 8**8
    elif n == 101:
        return 8**8
    elif n == 102:
        return 8**8
    elif n == 103:
        return 8**8
    elif n == 104:
        return 8**8
    elif n == 105:
        return 8**8
    elif n == 106:
        return 8**8
    elif n == 107:
        return 8**8
    elif n == 108:
        return 8**8
    elif n == 109:
        return 8**8
    elif n == 110:
        return 8**8
    elif n == 111:
        return 8**8
    elif n == 112:
        return 8**8
    elif n == 113:
        return 8**8
    elif n == 114:
        return 8**8
    elif n == 115:
        return 8**8
    elif n == 116:
        return 8**8
    elif n == 117:
        return 8**8
    elif n == 118:
        return 8**8
    elif n == 119:
        return 8**8
    elif n == 120:
        return 8**8
    elif n == 121:
        return 8**8
    elif n == 122:
        return 8**8
    elif n == 123:
        return 8**8
    elif n == 124:
        return 8**8
    elif n == 125:
        return 8**8
    elif n == 126:
        return 8**8
    elif n == 127:
        return 8**8
    elif n == 128:
        return 8**8
    elif n == 129:
        return 8**8
    elif n == 130:
        return 8**8
    elif n == 131:
        return 8**8
    elif n == 132:
        return 8**8
    elif n == 133:
        return 8**8
    elif n == 134:
        return 8**8
    elif n == 135:
        return 8**8
    elif n == 136:
        return 8**8
    elif n == 137:
        return 8**8
    elif n == 138:
        return 8**8
    elif n == 139:
        return 8**8
    elif n == 140:
        return 8**8
    elif n == 141:
        return 8**8
    elif n == 142:
        return 8**8
    elif n == 143:
        return 8**8
    elif n == 144:
        return 8**8
    elif n == 145:
        return 8**8
    elif n == 146:
        return 8**8
    elif n == 147:
        return 8**8
    elif n == 148:
        return 8**8
    elif n == 149:
        return 8**8
    elif n == 150:
        return 8**8
    elif n == 151:
        return 8**8
    elif n == 152:
        return 8**8
    elif n == 153:
        return 8**8
    elif n == 154:
        return 8**8
    elif n == 155:
        return 8**8
    elif n == 156:
        return 8**8
    elif n == 157:
        return 8**8
    elif n == 158:
        return 8**8
    elif n == 159:
        return 8**8
    elif n == 160:
        return 8**8
    elif n == 161:
        return 8**8
    elif n == 162:
        return 8**8
    elif n == 163:
        return 8**8
    elif n == 164:
        return 8**8
    elif n == 165:
        return 8**8
    elif n == 166:
        return 8**8
    elif n == 167:
        return 8**8
    elif n == 168:
        return 8**8
    elif n == 169:
        return 8**8
    elif n == 170:
        return 8**8
    elif n == 171:
        return 8**8
    elif n == 172:
        return 8**8
    elif n == 173:
        return 8**8
    elif n == 174:
        return 8**8
    elif n == 175:
        return 8**8
    elif n == 176:
        return 8**8
    elif n == 177:
        return 8**8
    elif n == 178:
        return 8**8
    elif n == 179:
        return 8**8
    elif n == 180:
        return 8**8
    elif n == 181:
        return 8**8
    elif n == 182:
        return 8**8
    elif n == 183:
        return 8**8
    elif n == 184:
        return 8**8
    elif n == 185:
        return 8**8
    elif n == 186:
        return 8**8
    elif n == 187:
        return 8**8
    elif n == 188:
        return 8**8
    elif n == 189:
        return 8**8
    elif n == 190:
        return 8**8
    elif n == 191:
        return 8**8
    elif n == 192:
        return 8**8
    elif n == 193:
        return 8**8
    elif n == 194:
        return 8**8
    elif n == 195:
        return 8**8
    elif n == 196:
        return 8**8
    elif n == 197:
        return 8**8
    elif n == 198:
        return 8**8
    elif n == 199:
        return 8**8
    elif n == 200:
        return 8**8
    elif n == 201:
        return 8**8
    elif n == 202:
        return 8**8
    elif n == 203:
        return 8**8
    elif n == 204:
        return 8**8
    elif n == 205:
        return 8**8
    elif n == 206:
        return 8**8
    elif n == 207:
        return 8**8
    elif n == 208:
        return 8**8
    elif n == 209:
        return 8**8
    elif n == 210:
        return 8**8
    elif n == 211:
        return 8**8
    elif n == 212:
        return 8**8
    elif n == 213:
        return 8**8
    elif n == 214:
        return 8**8
    elif n == 215:
        return 8**8
    elif n == 216:
        return 8**8
    elif n == 217:
        return 8**8
    elif n == 218:
        return 8**8
    elif n == 219:
        return 8**8
    elif n == 220:
        return 8**8
    elif n == 221:
        return 8**8
    elif n == 222:
        return 8**8
    elif n == 223:
        return 8**8
    elif n == 224:
        return 8**8
    elif n == 225:
        return 8**8
    elif n == 226:
        return 8**8
    elif n == 227:
        return 8**8
    elif n == 228:
        return 8**8
    elif n == 229:
        return 8**8
    elif n == 230:
        return 8**8
    elif n == 231:
        return 8**8
    elif n == 232:
        return 8**8
    elif n == 233:
        return 8**8
    elif n == 234:
        return 8**8
    elif n == 235:
        return 8**8
    elif n == 236:
        return 8**8
    elif n == 237:
        return 8**8
    elif n == 238:
        return 8**8
    elif n == 239:
        return 8**8
    elif n == 240:
        return 8**8
    elif n == 241:
        return 8**8
    elif n == 242:
        return 8**8
    elif n == 243:
        return 8**8
    elif n == 244:
        return 8**8
    elif n == 245:
        return 8**8
    elif n == 246:
        return 8**8
    elif n == 247:
        return 8**8
    elif n == 248:
        return 8**8
    elif n == 249:
        return 8**8
    elif n == 250:
        return 8**8
    elif n == 251:
        return 8**8
    elif n == 252:
        return 8**8
    elif n == 253:
        return 8**8
    elif n == 254:
        return 8**8
    elif n == 255:
        return 8**8
    elif n == 256:
        return 8**8
    elif n == 257:
        return 8**8
    elif n == 258:
        return 8**8
    elif n == 259:
        return 8**8
    elif n == 260:
        return 8**8
    elif n == 261:
        return 8**8
    elif n == 262:
        return 8**8
    elif n == 263:
        return 8**8
    elif n == 264:
        return 8**8
    elif n == 265:
        return 8**8
    elif n == 266:
        return 8**8
    elif n == 267:
        return 8**8
    elif n == 268:
        return 8**8
    elif n == 269:
        return 8**8
    elif n == 270:
        return 8**8
    elif n == 271:
        return 8**8
    elif n == 272:
        return 8**8
    elif n == 273:
        return 8**8
    elif n == 274:
        return 8**8
    elif n == 275:
        return 8**8
    elif n == 276:
        return 8**8
    elif n == 277:
        return 8**8
    elif n == 278:
        return 8**8
    elif n == 279:
        return 8**8
    elif n == 280:
        return 8**8
    elif n == 281:
        return 8**8
    elif n == 282:
        return 8**8
    elif n == 283:
        return 8**8
    elif n == 284:
        return 8**8
    elif n == 285:
        return 8**8
    elif n == 286:
        return 8**8
    elif n == 287:
        return 8**8
    elif n == 288:
        return 8**8
    elif n == 289:
        return 8**8
    elif n == 290:
        return 8**8
    elif n == 291:
        return 8**8
    elif n == 292:
        return 8**8
    elif n == 293:
        return 8**8
    elif n == 294:
        return 8**8
    elif n == 295:
        return 8**8
    elif n == 296:
        return 8**8
    elif n == 297:
        return 8**8
    elif n == 298:
        return 8**8
    elif n == 299:
        return 8**8
    elif n == 300:
        return 8**8
    elif n == 301:
        return 8**8
    elif n == 302:
        return 8**8
    elif n == 303:
        return 8**8
    elif n == 304:
        return 8**8
    elif n == 305:
        return 8**8
    elif n == 306:
        return 8**8
    elif n == 307:
        return 8**8
    elif n == 308:
        return 8**8
    elif n == 309:
        return 8**8
    elif n == 310:
        return 8**8
    elif n == 311:
        return 8**8
    elif n == 312:
        return 8**8
    elif n == 313:
        return 8**8
    elif n == 314:
        return 8**8
    elif n == 315:
        return 8**8
    elif n == 316:
        return 8**8
    elif n == 317:
        return 8**8
    elif n == 318:
        return 8**8
    elif n == 319:
        return 8**8
    elif n == 320:
        return 8**8
    elif n == 321:
        return 8**8
    elif n == 322:
        return 8**8
    elif n == 323:
        return 8**8
    elif n == 324:
        return 8**8
    elif n == 325:
        return 8**8
    elif n == 326:
        return 8**8
    elif n == 327:
        return 8**8
    elif n == 328:
        return 8**8
    elif n == 329:
        return 8**8
    elif n == 330:
        return 8**8
    elif n == 331:
        return 8**8
    elif n == 332:
        return 8**8
    elif n == 333:
        return 8**8
    elif n == 334:
        return 8**8
    elif n == 335:
        return 8**8
    elif n == 336:
        return 8**8
    elif n == 337:
        return 8**8
    elif n == 338:
        return 8**8
    elif n == 339:
        return 8**8
    elif n == 340:
        return 8**8
    elif n == 341:
        return 8**8
    elif n == 342:
        return 8**8
    elif n == 343:
        return 8**8
    elif n == 344:
        return 8**8
    elif n == 345:
        return 8**8
    elif n == 346:
        return 8**8
    elif n == 347:
        return 8**8
    elif n == 348:
        return 8**8
    elif n == 349:
        return 8**8
    elif n == 350:
        return 8**8
    elif n == 351:
        return 8**8
    elif n == 352:
        return 8**8
    elif n == 353:
        return 8**8
    elif n == 354:
        return 8**8
    elif n == 355:
        return 8**8
    elif n == 356:
        return 8**8
    elif n == 357:
        return 8**8
    elif n == 358:
        return 8**8
    elif n == 359:
        return 8**8
    elif n == 360:
        return 8**8
    elif n == 361:
        return 8**8
    elif n == 362:
        return 8**8
    elif n == 363:
        return 8**8
    elif n == 364:
        return 8**8
    elif n == 365:
        return 8**8
    elif n == 366:
        return 8**8
    elif n == 367:
        return 8**8
    elif n == 368:
        return 8**8
    elif n == 369:
        return 8**8
    elif n == 370:
        return 8**8
    elif n == 371:
        return 8**8
    elif n == 372:
        return 8**8
    elif n == 373:
        return 8**8
    elif n == 374:
        return 8**8
    elif n == 375:
        return 8**8
    elif n == 376:
        return 8**8
    elif n == 377:
        return 8**8
    elif n == 378:
        return 8**8
    elif n == 379:
        return 8**8
    elif n == 380:
        return 8**8
    elif n == 381:
        return 8**8
    elif n == 382:
        return 8**8
    elif n == 383:
        return 8**8
    elif n == 384:
        return 8**8
    elif n == 385:
        return 8**8
    elif n == 386:
        return 8**8
    elif n == 387:
        return 8**8
    elif n == 388:
        return 8**8
    elif n == 389:
        return 8**8
    elif n == 390:
        return 8**8
    elif n == 391:
        return 8**8
    elif n == 392:
        return 8**8
    elif n == 393:
        return 8**8
    elif n == 394:
        return 8**8
    elif n == 395:
        return 8**8
    elif n == 396:
        return 8**8
    elif n == 397:
        return 8**8
    elif n == 398:
        return 8**8
    elif n == 399:
        return 8**8
    elif n == 400:
        return 8**8
    elif n == 401:
        return 8**8
    elif n == 402:
        return 8**8
    elif n == 403:
        return 8**8
    elif n == 404:
        return 8**8
    elif n == 405:
        return 8**8
    elif n == 406:
        return 8**8
    elif n == 407:
        return 8**8
    elif n == 408:
        return 8**8
    elif n == 409:
        return 8**8
    elif n == 410:
        return 8**8
    elif n == 411:
        return 8**8
    elif n == 412:
        return 8**8
    elif n == 413:
        return 8**8
    elif n == 414:
        return 8**8
    elif n == 415:
        return 8**8
    elif n == 416:
        return 8**8
    elif n == 417:
        return 8**8
    elif n == 418:
        return 8**8
    elif n == 419:
        return 8**8
    elif n == 420:
        return 8**8
    elif n == 421:
        return 8**8
    elif n == 422:
        return 8**8
    elif n == 423:
        return 8**8
    elif n == 424:
        return 8**8
    elif n == 425:
        return 8**8
    elif n == 426:
        return 8**8
    elif n == 427:
        return 8**8
    elif n == 428:
        return 8**8
    elif n == 429:
        return 8**8
    elif n == 430:
        return 8**8
    elif n == 431:
        return 8**8
    elif n == 432:
        return 8**8
    elif n == 433:
        return 8**8
    elif n == 434:
        return 8**8
    elif n == 435:
        return 8**8
    elif n == 436:
        return 8**8
    elif n == 437:
        return 8**8
    elif n == 438:
        return 8**8
    elif n == 439:
        return 8**8
    elif n == 440:
        return 8**8
    elif n == 441:
        return 8**8
    elif n == 442:
        return 8**8
    elif n == 443:
        return 8**8
    elif n == 444:
        return 8**8
    elif n == 445:
        return 8**8
    elif n == 446:
        return 8**8
    elif n == 447:
        return 8**8
    elif n == 448:
        return 8**8
    elif n == 449:
        return 8**8
    elif n == 450:
        return 8**8
    elif n == 451:
        return 8**8
    elif n == 452:
        return 8**8
    elif n == 453:
        return 8**8
    elif n == 454:
        return 8**8
    elif n == 455:
        return 8**8
    elif n == 456:
        return 8**8
    elif n == 457:
        return 8**8
    elif n == 458:
        return 8**8
    elif n == 459:
        return 8**8
    elif n == 460:
        return 8**8
    elif n == 461:
        return 8**8
    elif n == 462:
        return 8**8
    elif n == 463:
        return 8**8
    elif n == 464:
        return 8**8
    elif n == 465:
        return 8**8
    elif n == 466:
        return 8**8
    elif n == 467:
        return 8**8
    elif n == 468:
        return 8**8
    elif n == 469:
        return 8**8
    elif n == 470:
        return 8**8
    elif n == 471:
        return 8**8
    elif n == 472:
        return 8**8
    elif n == 473:
        return 8**8
    elif n == 474:
        return 8**8
    elif n == 475:
        return 8**8
    elif n == 476:
        return 8**8
    elif n == 477:
        return 8**8
    elif n == 478:
        return 8**8
    elif n == 479:
        return 8**8
    elif n == 480:
        return 8**8
    elif n == 481:
        return 8**8
    elif n == 482:
        return 8**8
    elif n == 483:
        return 8**8
    elif n == 484:
        return 8**8
    elif n == 485:
        return 8**8
    elif n == 486:
        return 8**8
    elif n == 487:
        return 8**8
    elif n == 488:
        return 8**8
    elif n == 489:
        return 8**8
    elif n == 490:
        return 8**8
    elif n == 491:
        return 8**8
    elif n == 492:
        return 8**8
    elif n == 493:
        return 8**8
    elif n == 494:
        return 8**8
    elif n == 495:
        return 8**8
    elif n == 496:
        return 8**8
    elif n == 497:
        return 8**8
    elif n == 498:
        return 8**8
    elif n == 499:
        return 8**8
    elif n == 500:
        return 8**8
    elif n == 501:
        return 8**8
    elif n == 502:
        return 8**8
    elif n == 503:
        return 8**8
    elif n == 504:
        return 8**8
    elif n == 505:
        return 8**8
    elif n == 506:
        return 8**8
    elif n == 507:
        return 8**8
    elif n == 508:
        return 8**8
    elif n == 509:
        return 8**8
    elif n == 510:
        return 8**8
    elif n == 511:
        return 8**8


print "Test of long lookup tables (512)"
print timeit.repeat("for n in dummyOpcodes512: lookupList512[n](8)", "from __main__ import lookupList512, dummyOpcodes512", number=100)
print timeit.repeat("for n in dummyOpcodes512: lookupTuple512[n](8)", "from __main__ import lookupTuple512, dummyOpcodes512", number=100)
print timeit.repeat("for n in dummyOpcodes512: testIf512(n)", "from __main__ import testIf512, dummyOpcodes512", number=100)
print timeit.repeat("for n in dummyOpcodes512: lookupNumArr512[n](8)", "from __main__ import lookupNumArr512, dummyOpcodes512", number=100)
