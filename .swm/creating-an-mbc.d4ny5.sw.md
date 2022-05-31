---
id: d4ny5
name: Creating an MBC
file_version: 1.0.2
app_version: 0.8.7-0
file_blobs:
  pyboy/core/cartridge/mbc1.py: 27ed14c74bb4791b71b2cadbd424de039fdbee20
  pyboy/core/cartridge/__init__.py: 42ba1a244d84a660fa77c596e4730bb17f388b32
  pyboy/core/cartridge/cartridge.py: 0190842a013eacb9c0e49c2efcd5da95cb9e0e3a
  pyboy/core/cartridge/base_mbc.pxd: f249b04be5e64564596bb8871eaeba9fb13ff907
  pyboy/core/cartridge/mbc3.pxd: ce2a781ad4fae978311c8ccacb12a768b5fbc9a7
  pyboy/core/cartridge/mbc3.py: ede561d39e771c927a411c0a055077c04866453a
  pyboy/core/cartridge/mbc5.pxd: a58f041f488ce96bc62d35cf05aa50f3e65180c9
  pyboy/core/cartridge/mbc5.py: 68d07601d0dd1c5c4c09bd59b537df70829c3c06
---

Understanding MBCs, how they work, and how to add new ones, is important - and this document will describe just that.

An MBC is MBC

To create a new MBC, we create a class that inherits from `BaseMBC`[<sup id="J7FTe">↓</sup>](#f-J7FTe).

Some examples of `BaseMBC`[<sup id="J7FTe">↓</sup>](#f-J7FTe)s are `MBC3`[<sup id="ZEICwf">↓</sup>](#f-ZEICwf), `MBC3`[<sup id="Z1EieLL">↓</sup>](#f-Z1EieLL), `MBC5`[<sup id="ZkJYRT">↓</sup>](#f-ZkJYRT), and `MBC5`[<sup id="ZOBXkJ">↓</sup>](#f-ZOBXkJ).

<br/>

## TL;DR - How to Add a `BaseMBC`[<sup id="J7FTe">↓</sup>](#f-J7FTe)

1. Create a new class inheriting from `BaseMBC`[<sup id="J7FTe">↓</sup>](#f-J7FTe)&nbsp;
   - Place the file under [[sym:./pyboy/core/cartridge({"type":"path","text":"pyboy/core/cartridge","path":"pyboy/core/cartridge"})]],
     e.g. `MBC1`[<sup id="Z2tXvdN">↓</sup>](#f-Z2tXvdN) is defined in [[sym:./pyboy/core/cartridge/mbc1.py({"type":"path","text":"pyboy/core/cartridge/mbc1.py","path":"pyboy/core/cartridge/mbc1.py"})]].
2. Implement `setitem`[<sup id="7WWcG">↓</sup>](#f-7WWcG).
3. Update [[sym:./pyboy/core/cartridge/__init__.py({"type":"path","text":"pyboy/core/cartridge/__init__.py","path":"pyboy/core/cartridge/__init__.py"})]].
3. Update [[sym:./pyboy/core/cartridge/cartridge.py({"type":"path","text":"pyboy/core/cartridge/cartridge.py","path":"pyboy/core/cartridge/cartridge.py"})]].
4. **Profit** 💰

<br/>

## Example Walkthrough - `MBC1`[<sup id="Z2tXvdN">↓</sup>](#f-Z2tXvdN)
We'll follow the implementation of `MBC1`[<sup id="Z2tXvdN">↓</sup>](#f-Z2tXvdN) for this example.

A `MBC1`[<sup id="Z2tXvdN">↓</sup>](#f-Z2tXvdN) is {Explain what MBC1 is and how it works with the MBC interface}

<br/>

## Steps to Adding a new `BaseMBC`[<sup id="J7FTe">↓</sup>](#f-J7FTe)

<br/>

### 1\. Inherit from `BaseMBC`[<sup id="J7FTe">↓</sup>](#f-J7FTe).
All `BaseMBC`[<sup id="J7FTe">↓</sup>](#f-J7FTe)s are defined in files under [[sym:./pyboy/core/cartridge({"type":"path","text":"pyboy/core/cartridge","path":"pyboy/core/cartridge"})]].

<br/>

We first need to define our class in the relevant file, and inherit from `BaseMBC`[<sup id="J7FTe">↓</sup>](#f-J7FTe):
<!-- NOTE-swimm-snippet: the lines below link your snippet to Swimm -->
### 📄 pyboy/core/cartridge/mbc1.py
```python
⬜ 10     logger = logging.getLogger(__name__)
⬜ 11     
⬜ 12     
🟩 13     class MBC1(BaseMBC):
⬜ 14         def __init__(self, *args, **kwargs):
⬜ 15             super().__init__(*args, **kwargs)
⬜ 16             self.bank_select_register1 = 1
```

<br/>

### 2\. Implement `setitem`[<sup id="7WWcG">↓</sup>](#f-7WWcG)

<br/>

The goal of `setitem`[<sup id="7WWcG">↓</sup>](#f-7WWcG) is to {Explain setitem's role}.

<br/>

This is how we implemented it for `MBC1`[<sup id="Z2tXvdN">↓</sup>](#f-Z2tXvdN) {Explain what's happening in this implementation}
<!-- NOTE-swimm-snippet: the lines below link your snippet to Swimm -->
### 📄 pyboy/core/cartridge/mbc1.py
```python
⬜ 16             self.bank_select_register1 = 1
⬜ 17             self.bank_select_register2 = 0
⬜ 18     
🟩 19         def setitem(self, address, value):
🟩 20             if 0x0000 <= address < 0x2000:
🟩 21                 self.rambank_enabled = (value & 0b00001111) == 0b1010
🟩 22             elif 0x2000 <= address < 0x4000:
🟩 23                 value &= 0b00011111
🟩 24                 # The register cannot contain zero (0b00000) and will be initialized as 0b00001
🟩 25                 # Attempting to write 0b00000 will write 0b00001 instead.
🟩 26                 if value == 0:
🟩 27                     value = 1
🟩 28                 self.bank_select_register1 = value
🟩 29             elif 0x4000 <= address < 0x6000:
🟩 30                 self.bank_select_register2 = value & 0b11
🟩 31             elif 0x6000 <= address < 0x8000:
🟩 32                 self.memorymodel = value & 0b1
🟩 33             elif 0xA000 <= address < 0xC000:
🟩 34                 if self.rambanks is None:
🟩 35                     logger.warning(
🟩 36                         "Game tries to set value 0x%0.2x at RAM address 0x%0.4x, but RAM "
🟩 37                         "banks are not initialized. Initializing %d RAM banks as "
🟩 38                         "precaution" % (value, address, self.external_ram_count)
🟩 39                     )
🟩 40                     self.init_rambanks(self.external_ram_count)
🟩 41     
🟩 42                 if self.rambank_enabled:
🟩 43                     self.rambank_selected = self.bank_select_register2 if self.memorymodel == 1 else 0
🟩 44                     self.rambanks[self.rambank_selected % self.external_ram_count][address - 0xA000] = value
🟩 45             else:
🟩 46                 logger.error("Invalid writing address: %s" % hex(address))
⬜ 47     
⬜ 48         def getitem(self, address):
⬜ 49             if 0x0000 <= address < 0x4000:
```

<br/>

## Update additional files with the new class
Every time we add a new `BaseMBC`[<sup id="J7FTe">↓</sup>](#f-J7FTe), we reference it in a few locations.
We will still look at `MBC1`[<sup id="Z2tXvdN">↓</sup>](#f-Z2tXvdN) as our example.

<br/>

3\. Add the new class to [[sym:./pyboy/core/cartridge/__init__.py({"type":"path","text":"pyboy/core/cartridge/__init__.py","path":"pyboy/core/cartridge/__init__.py"})]], like so:
<!-- NOTE-swimm-snippet: the lines below link your snippet to Swimm -->
### 📄 pyboy/core/cartridge/__init__.py
```python
⬜ 6      # from .base_mbc import BaseMBC, ROMOnly
⬜ 7      from .cartridge import load_cartridge
⬜ 8      
🟩 9      # from .mbc1 import MBC1
⬜ 10     # from .mbc2 import MBC2
⬜ 11     # from .mbc3 import MBC3
⬜ 12     # from .mbc5 import MBC5
```

<br/>

4\. We modify  [[sym:./pyboy/core/cartridge/cartridge.py({"type":"path","text":"pyboy/core/cartridge/cartridge.py","path":"pyboy/core/cartridge/cartridge.py"})]], as we do with `MBC1`[<sup id="Z2tXvdN">↓</sup>](#f-Z2tXvdN) here:
<!-- NOTE-swimm-snippet: the lines below link your snippet to Swimm -->
### 📄 pyboy/core/cartridge/cartridge.py
```python
⬜ 77     CARTRIDGE_TABLE = {
⬜ 78         #      MBC     , SRAM  , Battery , RTC
⬜ 79         0x00: (ROMOnly , False , False   , False) , # ROM
🟩 80         0x01: (MBC1    , False , False   , False) , # MBC1
🟩 81         0x02: (MBC1    , True  , False   , False) , # MBC1+RAM
🟩 82         0x03: (MBC1    , True  , True    , False) , # MBC1+RAM+BATT
⬜ 83         0x05: (MBC2    , False , False   , False) , # MBC2
⬜ 84         0x06: (MBC2    , False , True    , False) , # MBC2+BATTERY
⬜ 85         0x08: (ROMOnly , True  , False   , False) , # ROM+RAM
```

<br/>

<!-- THIS IS AN AUTOGENERATED SECTION. DO NOT EDIT THIS SECTION DIRECTLY -->
### Swimm Note

<span id="f-J7FTe">BaseMBC</span>[^](#J7FTe) - "pyboy/core/cartridge/base_mbc.pxd" L10
```cython
cdef class BaseMBC:
```

<span id="f-Z2tXvdN">MBC1</span>[^](#Z2tXvdN) - "pyboy/core/cartridge/mbc1.py" L13
```python
class MBC1(BaseMBC):
```

<span id="f-Z1EieLL">MBC3</span>[^](#Z1EieLL) - "pyboy/core/cartridge/mbc3.py" L13
```python
class MBC3(BaseMBC):
```

<span id="f-ZEICwf">MBC3</span>[^](#ZEICwf) - "pyboy/core/cartridge/mbc3.pxd" L10
```cython
cdef class MBC3(BaseMBC):
```

<span id="f-ZOBXkJ">MBC5</span>[^](#ZOBXkJ) - "pyboy/core/cartridge/mbc5.py" L13
```python
class MBC5(BaseMBC):
```

<span id="f-ZkJYRT">MBC5</span>[^](#ZkJYRT) - "pyboy/core/cartridge/mbc5.pxd" L10
```cython
cdef class MBC5(BaseMBC):
```

<span id="f-7WWcG">setitem</span>[^](#7WWcG) - "pyboy/core/cartridge/mbc1.py" L19
```python
    def setitem(self, address, value):
```

<br/>

This file was generated by Swimm. [Click here to view it in the app](https://swimm-web-app.web.app/repos/Z2l0aHViJTNBJTNBUHlCb3klM0ElM0FnaWxhZG5hdm90/docs/d4ny5).