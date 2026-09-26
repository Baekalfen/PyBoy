from pathlib import Path


DOCUMENTATION_IMAGES = (
    "Kirby1.png",
    "Kirby2.png",
    "PokemonGen1-1.png",
    "PokemonGen1-2.png",
    "PokemonGen1-3.png",
    "PandorasBlocks.png",
    "SuperMarioBrosDeluxe.png",
    "SuperMarioLand1.png",
    "SuperMarioLand2.png",
    "Tetris1.png",
    "Tetris2.png",
)

TEST_ARTIFACTS = (
    "frame.png",
    "state_file.state",
    "tile_1.png",
)


def pytest_sessionfinish(session, exitstatus):
    if exitstatus != 0 or hasattr(session.config, "workerinput"):
        return

    assets = Path(__file__).parent / "docs/wiki/assets"
    for filename in DOCUMENTATION_IMAGES:
        source = Path.cwd() / filename
        if source.is_file():
            source.replace(assets / filename)

    for filename in TEST_ARTIFACTS:
        (Path.cwd() / filename).unlink(missing_ok=True)
