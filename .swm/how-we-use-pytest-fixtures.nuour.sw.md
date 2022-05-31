---
id: nuour
name: How We Use Pytest Fixtures
file_version: 1.0.2
app_version: 0.8.7-0
file_blobs:
  tests/test_openai_gym.py: 33d543b122e3f89a3caab8479f6dabae4b1aa59a
---

In this document we'll explain what Pytest Fixtures are and show some examples from our code.

<br/>

## Intro - what are fixtures?
Fixtures are a way to set up everything you need for a test to run.  In pytest, they are functions you define that serve this purpose.

From [the official documentation](https://docs.pytest.org/en/latest/explanation/fixtures.html):
> In testing, a fixture provides a defined, reliable and consistent context for the tests. This could include environment (for example a database configured with known parameters) or content (such as a dataset).

All the things (state, services etc.) set up by fixtures are accessed by the test functions through arguments.


<br/>

### How to define a fixture?

<br/>

We use the decorator `@pytest.fixture` to tell pytest that a specific function is a fixture. You can see an example here:
<!-- NOTE-swimm-snippet: the lines below link your snippet to Swimm -->
### 📄 tests/test_openai_gym.py
```python
⬜ 17     is_pypy = platform.python_implementation() == "PyPy"
⬜ 18     
⬜ 19     
🟩 20     @pytest.fixture
🟩 21     def pyboy():
⬜ 22         pyboy = PyBoy(tetris_rom, window_type="headless", disable_input=True, game_wrapper=True)
⬜ 23         pyboy.set_emulation_speed(0)
⬜ 24         return pyboy
```

<br/>

### How to Use a Fixture?
Test functions **request** fixtures they require by declaring them as arguments. In pytest terms, it is called **requesting** a fixture.

From [the official documentation](https://docs.pytest.org/en/latest/explanation/fixtures.html):
> When pytest goes to run a test, it looks at the parameters in that test function’s signature, and then searches for fixtures that have the same names as those parameters. Once pytest finds them, it runs those fixtures, captures what they returned (if anything), and passes those objects into the test function as arguments.

<br/>

Here is an example of how `pyboy`[<sup id="Z1moPaJ">↓</sup>](#f-Z1moPaJ) is used in a test function, as it is being passed to it as an argument:
<!-- NOTE-swimm-snippet: the lines below link your snippet to Swimm -->
### 📄 tests/test_openai_gym.py
```python
⬜ 45         reason="This requires gym, which doesn't work on this platform"
⬜ 46     )
⬜ 47     class TestOpenAIGym:
🟩 48         def test_raw(self, pyboy):
🟩 49             env = pyboy.openai_gym(observation_type="raw", action_type="press")
⬜ 50             observation = env.reset()
⬜ 51             assert observation.shape == (ROWS, COLS, 3)
⬜ 52             assert observation.dtype == np.uint8
⬜ 53     
⬜ 54             observation, _, _, _ = env.step(0)
⬜ 55             assert observation.shape == (ROWS, COLS, 3)
⬜ 56             assert observation.dtype == np.uint8
⬜ 57     
⬜ 58         def test_tiles(self, pyboy, tiles_id, id0_block, id1_block):
⬜ 59             env = pyboy.openai_gym(observation_type="tiles")
```

<br/>

Notice that fixtures can also request other fixtures.

<br/>

### Fixture scopes - sharing fixtures
Fixtures are *created* when first **requested** by a test, and are *destroyed* based on their scope:

* `function`: the default scope, the fixture is destroyed at the end of the test.
* `class`: the fixture is destroyed during teardown of the last test in the class.
* `module`: the fixture is destroyed during teardown of the last test in the module.
* `package`: the fixture is destroyed during teardown of the last test in the package.
* `session`: the fixture is destroyed at the end of the test session. Every time you run pytest, it’s considered to be one session.

As `function` is the default scope, when a fixture doesn't explicitly define a scope - it will be destroyed when the test function ends.

A fixture is only available for tests to request if they are in the scope that fixture is defined in. If a fixture is defined inside a class, it can only be requested by tests inside that class. But if a fixture is defined inside the global scope of the module, then every test in that module, even if it’s defined inside a class, can request it.

<br/>

## Learn More About Fixtures
Read [the official documentation](https://docs.pytest.org/en/latest/how-to/fixtures.html#how-to-fixtures).

<br/>

## Our Fixtures
These fixtures are important to know as we use them quite often:

<br/>

### `pyboy`[<sup id="Z1moPaJ">↓</sup>](#f-Z1moPaJ)

In some cases, we use `pyboy`[<sup id="Z1moPaJ">↓</sup>](#f-Z1moPaJ) in order to create a game instance.

<br/>

You can see its implementation here:
<!-- NOTE-swimm-snippet: the lines below link your snippet to Swimm -->
### 📄 tests/test_openai_gym.py
```python
⬜ 17     is_pypy = platform.python_implementation() == "PyPy"
⬜ 18     
⬜ 19     
🟩 20     @pytest.fixture
🟩 21     def pyboy():
🟩 22         pyboy = PyBoy(tetris_rom, window_type="headless", disable_input=True, game_wrapper=True)
🟩 23         pyboy.set_emulation_speed(0)
🟩 24         return pyboy
⬜ 25     
⬜ 26     
⬜ 27     @pytest.fixture
```

<br/>

Here is an example of how it's called:
<!-- NOTE-swimm-snippet: the lines below link your snippet to Swimm -->
### 📄 tests/test_openai_gym.py
```python
⬜ 45         reason="This requires gym, which doesn't work on this platform"
⬜ 46     )
⬜ 47     class TestOpenAIGym:
🟩 48         def test_raw(self, pyboy):
🟩 49             env = pyboy.openai_gym(observation_type="raw", action_type="press")
⬜ 50             observation = env.reset()
⬜ 51             assert observation.shape == (ROWS, COLS, 3)
⬜ 52             assert observation.dtype == np.uint8
⬜ 53     
⬜ 54             observation, _, _, _ = env.step(0)
⬜ 55             assert observation.shape == (ROWS, COLS, 3)
⬜ 56             assert observation.dtype == np.uint8
⬜ 57     
⬜ 58         def test_tiles(self, pyboy, tiles_id, id0_block, id1_block):
⬜ 59             env = pyboy.openai_gym(observation_type="tiles")
```

<br/>

### `id0_block`[<sup id="btAtV">↓</sup>](#f-btAtV)

Quite often, we call `id0_block`[<sup id="btAtV">↓</sup>](#f-btAtV) for simple mocks.

<br/>

You can see its implementation here:
<!-- NOTE-swimm-snippet: the lines below link your snippet to Swimm -->
### 📄 tests/test_openai_gym.py
```python
⬜ 24         return pyboy
⬜ 25     
⬜ 26     
🟩 27     @pytest.fixture
🟩 28     def id0_block():
🟩 29         return np.array((1, 1, 2, 2))
⬜ 30     
⬜ 31     
⬜ 32     @pytest.fixture
```

<br/>

Here is an example of how it's called:
<!-- NOTE-swimm-snippet: the lines below link your snippet to Swimm -->
### 📄 tests/test_openai_gym.py
```python
⬜ 55             assert observation.shape == (ROWS, COLS, 3)
⬜ 56             assert observation.dtype == np.uint8
⬜ 57     
🟩 58         def test_tiles(self, pyboy, tiles_id, id0_block, id1_block):
⬜ 59             env = pyboy.openai_gym(observation_type="tiles")
⬜ 60             tetris = pyboy.game_wrapper()
⬜ 61             tetris.set_tetromino("Z")
⬜ 62             observation = env.reset()
⬜ 63     
⬜ 64             # Build the expected first observation
⬜ 65             game_area_shape = pyboy.game_wrapper().shape[::-1]
⬜ 66             expected_observation = tiles_id["BLANK"] * np.ones(game_area_shape, dtype=np.uint16)
🟩 67             expected_observation[id0_block, id1_block] = tiles_id["Z"]
⬜ 68             print(observation, expected_observation)
⬜ 69             assert np.all(observation == expected_observation)
⬜ 70     
🟩 71             expected_observation[id0_block, id1_block] = tiles_id["BLANK"]
⬜ 72     
⬜ 73             action = 2 # DOWN
⬜ 74             observation, _, _, _ = env.step(action) # Press DOWN
⬜ 75             observation, _, _, _ = env.step(action) # Press DOWN
⬜ 76     
⬜ 77             # Build the expected second observation
🟩 78             expected_observation[id0_block + 1, id1_block] = tiles_id["Z"]
⬜ 79             print(observation, expected_observation)
⬜ 80             assert np.all(observation == expected_observation)
⬜ 81     
⬜ 82         def test_compressed(self, pyboy, tiles_id, id0_block, id1_block):
⬜ 83             env = pyboy.openai_gym(observation_type="compressed")
```

<br/>

### `id1_block`[<sup id="Zegdb1">↓</sup>](#f-Zegdb1)

Sometimes, our test functions use `id1_block`[<sup id="Zegdb1">↓</sup>](#f-Zegdb1) as it is useful when another mock test.

<br/>

You can see its implementation here:
<!-- NOTE-swimm-snippet: the lines below link your snippet to Swimm -->
### 📄 tests/test_openai_gym.py
```python
⬜ 29         return np.array((1, 1, 2, 2))
⬜ 30     
⬜ 31     
🟩 32     @pytest.fixture
🟩 33     def id1_block():
🟩 34         return np.array((3, 4, 4, 5))
⬜ 35     
⬜ 36     
⬜ 37     @pytest.fixture
```

<br/>

Here is an example of how it's called:
<!-- NOTE-swimm-snippet: the lines below link your snippet to Swimm -->
### 📄 tests/test_openai_gym.py
```python
⬜ 55             assert observation.shape == (ROWS, COLS, 3)
⬜ 56             assert observation.dtype == np.uint8
⬜ 57     
🟩 58         def test_tiles(self, pyboy, tiles_id, id0_block, id1_block):
⬜ 59             env = pyboy.openai_gym(observation_type="tiles")
⬜ 60             tetris = pyboy.game_wrapper()
⬜ 61             tetris.set_tetromino("Z")
⬜ 62             observation = env.reset()
⬜ 63     
⬜ 64             # Build the expected first observation
⬜ 65             game_area_shape = pyboy.game_wrapper().shape[::-1]
⬜ 66             expected_observation = tiles_id["BLANK"] * np.ones(game_area_shape, dtype=np.uint16)
🟩 67             expected_observation[id0_block, id1_block] = tiles_id["Z"]
⬜ 68             print(observation, expected_observation)
⬜ 69             assert np.all(observation == expected_observation)
⬜ 70     
🟩 71             expected_observation[id0_block, id1_block] = tiles_id["BLANK"]
⬜ 72     
⬜ 73             action = 2 # DOWN
⬜ 74             observation, _, _, _ = env.step(action) # Press DOWN
⬜ 75             observation, _, _, _ = env.step(action) # Press DOWN
⬜ 76     
⬜ 77             # Build the expected second observation
🟩 78             expected_observation[id0_block + 1, id1_block] = tiles_id["Z"]
⬜ 79             print(observation, expected_observation)
⬜ 80             assert np.all(observation == expected_observation)
⬜ 81     
⬜ 82         def test_compressed(self, pyboy, tiles_id, id0_block, id1_block):
⬜ 83             env = pyboy.openai_gym(observation_type="compressed")
```

<br/>

### `tiles_id`[<sup id="1TmoyL">↓</sup>](#f-1TmoyL)

Quite often, we call `tiles_id`[<sup id="1TmoyL">↓</sup>](#f-1TmoyL) for test tiles.

<br/>

You can see its implementation here:
<!-- NOTE-swimm-snippet: the lines below link your snippet to Swimm -->
### 📄 tests/test_openai_gym.py
```python
⬜ 34         return np.array((3, 4, 4, 5))
⬜ 35     
⬜ 36     
🟩 37     @pytest.fixture
🟩 38     def tiles_id():
🟩 39         return {"BLANK": 47, "Z": 130, "DEADBLOCK": 135}
⬜ 40     
⬜ 41     
⬜ 42     @pytest.mark.skipif(
```

<br/>

Here is an example of how it's called:
<!-- NOTE-swimm-snippet: the lines below link your snippet to Swimm -->
### 📄 tests/test_openai_gym.py
```python
⬜ 55             assert observation.shape == (ROWS, COLS, 3)
⬜ 56             assert observation.dtype == np.uint8
⬜ 57     
🟩 58         def test_tiles(self, pyboy, tiles_id, id0_block, id1_block):
⬜ 59             env = pyboy.openai_gym(observation_type="tiles")
⬜ 60             tetris = pyboy.game_wrapper()
⬜ 61             tetris.set_tetromino("Z")
⬜ 62             observation = env.reset()
⬜ 63     
⬜ 64             # Build the expected first observation
⬜ 65             game_area_shape = pyboy.game_wrapper().shape[::-1]
🟩 66             expected_observation = tiles_id["BLANK"] * np.ones(game_area_shape, dtype=np.uint16)
🟩 67             expected_observation[id0_block, id1_block] = tiles_id["Z"]
⬜ 68             print(observation, expected_observation)
⬜ 69             assert np.all(observation == expected_observation)
⬜ 70     
🟩 71             expected_observation[id0_block, id1_block] = tiles_id["BLANK"]
⬜ 72     
⬜ 73             action = 2 # DOWN
⬜ 74             observation, _, _, _ = env.step(action) # Press DOWN
⬜ 75             observation, _, _, _ = env.step(action) # Press DOWN
⬜ 76     
⬜ 77             # Build the expected second observation
🟩 78             expected_observation[id0_block + 1, id1_block] = tiles_id["Z"]
⬜ 79             print(observation, expected_observation)
⬜ 80             assert np.all(observation == expected_observation)
⬜ 81     
⬜ 82         def test_compressed(self, pyboy, tiles_id, id0_block, id1_block):
⬜ 83             env = pyboy.openai_gym(observation_type="compressed")
```

<br/>

<!-- THIS IS AN AUTOGENERATED SECTION. DO NOT EDIT THIS SECTION DIRECTLY -->
### Swimm Note

<span id="f-btAtV">id0_block</span>[^](#btAtV) - "tests/test_openai_gym.py" L27
```python
@pytest.fixture
```

<span id="f-Zegdb1">id1_block</span>[^](#Zegdb1) - "tests/test_openai_gym.py" L32
```python
@pytest.fixture
```

<span id="f-Z1moPaJ">pyboy</span>[^](#Z1moPaJ) - "tests/test_openai_gym.py" L20
```python
@pytest.fixture
```

<span id="f-1TmoyL">tiles_id</span>[^](#1TmoyL) - "tests/test_openai_gym.py" L37
```python
@pytest.fixture
```

<br/>

This file was generated by Swimm. [Click here to view it in the app](https://swimm-web-app.web.app/repos/Z2l0aHViJTNBJTNBUHlCb3klM0ElM0FnaWxhZG5hdm90/docs/nuour).