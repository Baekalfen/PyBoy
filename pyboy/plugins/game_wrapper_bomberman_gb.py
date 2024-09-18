from datetime import datetime

import numpy as np
from numpy.typing import NDArray

import pyboy

from .base_plugin import PyBoyGameWrapper

logger = pyboy.logging.get_logger(__name__)


class GameWrapperBombermanGB(PyBoyGameWrapper):
    """This class wraps Bomberman GB, and provides basic access for AIs.

    If you call `print` on an instance of this object, it will show an overview of
    everything this object provides.
    """

    cartridge_title = 'BOMBER MAN GB'

    def __init__(self, *args, **kwargs):
        # Readonly Vars
        self._GAME_AREA_SHAPE = (2, 2, 18, 14)
        self._ENEMY = ['ENEMY_1', 'ENEMY_2', 'ENEMY_3']

        self.AGENT_DEAD = 51233  # 0xc821
        self.AGENT_STATS_BOMB_PLACED = 49462  # 0xc136
        self.AGENT_STATS_BOMB_MAX = 49461  # 0xc135
        self.AGENT_STATS_BOMB_RANGE = 49463  # 0xc137

        self._COORD_MEM_ADDR = {
            'AGENT': (51202, 51206),
            'ENEMY_1': (51458, 51462),
            'ENEMY_2': (51714, 51718),
            'ENEMY_3': (51970, 51974),
        }

        self._ENEMY_DEAD_MEM_ADDR = {
            'ENEMY_1': 51489,
            'ENEMY_2': 51745,
            'ENEMY_3': 52001,
        }

        self.BOMBINFO_START = 50721  # 0xc621
        self.BOMBINGO_END = 50945  # 0xc701

        # Game Vars
        self._ENEMY_ALIVE = []

        self._agent_dead = self.pyboy.memory[self.AGENT_DEAD]
        self._agent_bombs_available = 1
        self._agent_bomb_max = 1
        self._agent_bomb_range = 1
        self._agent_bombs = []

        self._score_agent_kill = 0
        self._agent_suicide = 0

        self._score_agent_placed_bomb = 0
        self._bomb_block_hits = 0

        self._min_global_distance = 999
        self._score_min_global_dist = 0
        self._last_min_enemy_distance = 999
        self._score_last_dist = 0
        self._agent_in_bomb_range = 0

        super().__init__(*args, game_area_section=self._GAME_AREA_SHAPE, **kwargs)
        super().game_area_mapping(self._minimal_mapping(), 0)

    def start_game(self, timer_div=None, enemies=None, win=1, time=1) -> None:
        """This method starts the game into the play state and creates a save state.

        Args:
            timer_div (int, optional): "RandomSeed" of PyBoy. Defaults to None.
            enemies (int, optional): Amount of enemies. If default random
                                        amount 1-3. Defaults to None.
            win (int, optional): Amounts of wins needed. Defaults to 1.
            time (int, optional): Max duration of Game (Episode). Defaults to 1.
        """
        if not enemies:
            enemies = np.random.default_rng().integers(1, 4)
        
        logger.info('STARTING GAME')
        logger.info(f'Enemies: {enemies}, Wins: {win}, Time: {time}')

        PyBoyGameWrapper.start_game(self, timer_div)

        self._navigate_to_password_screen()

        # Enter Password for Arena Mode
        self._handle_password_screen()

        # Confirme Player One
        self.pyboy.button('start')
        self.pyboy.tick(100, render=False)

        # The point to reset is before enemy selection
        logger.info('SAVE STATE CREATED')
        self.saved_state.seek(0)
        self.pyboy.save_state(self.saved_state)

        # Add Enemies.
        self._set_enemies(enemies, shuffle=True)

        # Set rules
        self._handle_rules_screen(win=win, time=time)

        # Select Stage
        self._select_stage_screen()
        self._reset_settings()
        logger.info('STARTED GAME')

    def reset_game(self, timer_div=None, enemies=None, win=1, time=1) -> None:
        """After calling `start_game`, use this method to reset to save state.

        Kwargs:
            timer_div (int, optional): Replace timer's DIV register with this value.
                                       Use `None` to randomize. Defaults to None.
            enemies (int, optional): Amount of enemies. If default random
                                        amount 1-3. Defaults to 0.
            win (int, optional): _description_. Defaults to 1.
            time (int, optional): _description_. Defaults to 1.
        """
        if not enemies:
            enemies = np.random.default_rng().integers(1, 4)

        logger.info('RESETING GAME')
        logger.info(f'Enemies: {enemies}, Wins: {win}, Time: {time}')

        PyBoyGameWrapper.reset_game(self, timer_div=timer_div)

        # Add Enemies.
        self._set_enemies(enemies, shuffle=True)

        # Set rules
        self._handle_rules_screen(win=win, time=time)

        # Select Stage
        self._select_stage_screen()
        self._reset_settings()
        logger.info('RESET GAME')

    def game_over(self) -> bool:
        """This function checks if the game is over.

        The game is over, when agent won by last player alive or
        lost when agent dead.

        Returns:
            bool: True if game over.
        """
        logger.info('CHECKING GAME OVER')

        map_changed = self.pyboy.game_area()[2, 2] != 12
        win = (len(self._ENEMY_ALIVE) == 0) and not self._agent_dead

        end = self._agent_dead or map_changed or win  # or time_up

        logger.info(
            f'\nGAME END: {end}\nDEAD: {self._agent_dead}\n \
            MAP:{map_changed}\nWIN:{win}',
        )

        return end

    def _reset_settings(self) -> None:
        """This function resets the players stats."""
        logger.info('RESETING STATS')
        self._ENEMY_ALIVE = []

        self._agent_bombs_available = 1
        self._agent_bomb_max = 1
        self._agent_bomb_range = 1
        self._agent_bombs = []

        self._score_agent_kill = 0
        self._agent_suicide = 0

        self._score_agent_placed_bomb = 0
        self._bomb_block_hits = 0

        self._min_global_distance = 999
        self._score_min_global_dist = 0
        self._last_min_enemy_distance = 999
        self._score_last_dist = 0
        self._agent_in_bomb_range = 0

        logger.info('STATS RESETED')

    def post_tick(self) -> None:
        """This function is called after `.tick()`."""
        # From BaseClass
        self._tile_cache_invalid = True
        self._sprite_cache_invalid = True

        # Check if dead and if suicide.
        self._agent_dead = self.pyboy.memory[self.AGENT_DEAD]

        if self._agent_dead:
            logger.info('AGENT DEAD')
            self._agent_suicide = self._suicide()

        # This has some timing issues going on
        # Update enemy cache
        self._update_enemy_alive_cache()

        # Update placed agent placed bombs and coordinate of it
        self._update_agent_bomb_info()
        self._distance_checks()

    def score(self) -> tuple[int]:
        """Returns if condition for score was reached.

        For better abstraction this function returns only if a certain condition was
        reached. The amount of reward/points for the condition can be specified
        in the `GymWrapper`.

        Returns:
            tuple[int]: _description_
        """
        step_penalty = 1

        max_bomb_up = self._agent_bomb_max_increased()
        range_bomb_up = self._agent_bomb_range_increased()

        if self._score_agent_placed_bomb:
            placed_bomb = 1
            self._score_agent_placed_bomb = 0
        else:
            placed_bomb = 0

        if self._score_agent_kill:
            kill = 1
            self._score_agent_kill = 0
        else:
            kill = 0

        win = 1 if (len(self._ENEMY_ALIVE) == 0) and not self._agent_dead else 0
        lose = 1 if self._agent_dead else 0

        if self._agent_suicide:
            suicide = 1
            self._agent_suicide = 0
        else:
            suicide = 0

        if self._bomb_block_hits:
            block_hits = self._bomb_block_hits
            self._bomb_block_hits = 0
        else:
            block_hits = 0

        if self._score_min_global_dist:
            min_dist = 1
            self._score_min_global_dist = 0
        else:
            min_dist = 0

        if self._score_last_dist > 0:
            dist_score = 1
            self._score_last_dist = 0
        elif self._score_last_dist < 0:
            dist_score = -1
            self._score_last_dist = 0
        else:
            dist_score = 0

        if self._agent_in_bomb_range:
            in_bomb_range = 1
            self._agent_in_bomb_range = 0
        else:
            in_bomb_range = 0

        # logger.info("HELLO")

        return (
            step_penalty * 1,
            max_bomb_up * 1,
            range_bomb_up * 1,
            placed_bomb * 1,
            kill * 1,
            win * 1,
            lose * 1,
            suicide * 1,
            block_hits * 1,
            min_dist * 1,
            dist_score * 1,
            in_bomb_range * 1,
        )

    def _suicide(self) -> int:
        """Checks if Pieets killed himself.

        Returns:
            int: True if death by own bomb.
        """
        bomb_map = np.empty((7, 9), dtype=np.uint8)
        bomb_map = self._get_explosion_map()

        x_coord, y_coord = self._player_game_area_coordinate('AGENT')

        if bomb_map[y_coord // 2, x_coord // 2] in self._agent_bombs:
            logger.info('SUICIDE')
            return 1

        return 0

    def _get_explosion_map(self) -> NDArray[uint8]:  # noqa: F821
        """This Function returns a "map" with bombs on it.

        Returns:
            np.ndarray: "Map"
        """
        bombs = self.pyboy.memory[
            self.BOMBINFO_START : self.BOMBINGO_END
        ]  # See PlayerInfo

        # Reshape and deselect VRAM
        return np.reshape(np.array(bombs, dtype=np.uint8), (7, -1))[:7, :9]

    def _player_game_area_coordinate(self, player: str) -> tuple[int, int]:
        """This function returns the coordinates of player.

        Only the upperleft 8x8 square coordinates of 16x16 square player.

        Args:
            player (str): Name of player to search for

        Returns:
            tuple[int, int]: upperleft square coordinates
        """
        x_pixle_coordinate = self.pyboy.memory[self._COORD_MEM_ADDR[player][0]]
        y_pixle_coordinate = self.pyboy.memory[self._COORD_MEM_ADDR[player][1]]

        # See global var GAME_AREA_SHAPE
        x_coordinate = (
            x_pixle_coordinate // 8
        ) - 3  # //8 for Pixelsize -2 game_area offset.
        y_coordinate = (y_pixle_coordinate // 8) - 3

        # To much logging.
        # logger.info(f"UPPERLEFT COORDINATES {player}:")
        # logger.info(f"X: {x_coordinate}, Y: {y_coordinate}")

        return (x_coordinate, y_coordinate)  # Coordinate of the upperleft quarter.

    def _update_enemy_alive_cache(self) -> None:
        """This function creates or updates the enemy cache.

        If a enemy is removed from cache its checked if the player
        got the kill.
        """
        if self._ENEMY_ALIVE:
            for enemy in self._ENEMY_ALIVE:
                if self.pyboy.memory[self._ENEMY_DEAD_MEM_ADDR[enemy]]:
                    self._check_agent_kill(enemy)
                    self._ENEMY_ALIVE.remove(enemy)
                    logger.info(f'REMOVE {enemy}')
        else:
            logger.info('CREATING NEW ENEMY CACHE')
            for enemy in self._ENEMY:
                if not self.pyboy.memory[self._ENEMY_DEAD_MEM_ADDR[enemy]]:
                    self._ENEMY_ALIVE.append(enemy)

    def _check_agent_kill(self, enemy) -> None:
        bomb_map = np.empty((7, 9), dtype=np.uint8)
        bomb_map = self._get_explosion_map()
        x_coord, y_coord = self._player_game_area_coordinate(enemy)

        if bomb_map[y_coord // 2, x_coord // 2] in self._agent_bombs:
            self._score_agent_kill = 1
            logger.info('PIEETS IS UNSTOPPABLE')

    def _update_agent_bomb_info(self) -> None:
        """Updated Pieets bomb information.

        If a bomb placed it gets added to `self._agent_bombs`.
        If a bomb exploded it gets removed from `self._agent_bombs`.

        """
        diff_allowed = self._agent_placed_bomb()
        # logger.info(f"DIFF: {diff_allowed}")

        if diff_allowed <= 0:
            # logger.info(f"BOMB EXPLODE")
            # logger.info(f"PIEETS BOMBS BEFORE: {self._agent_bombs}")

            # Bombs are displayed longer in memory then in Pieets bombstats
            # so we check every time for removed bombs.

            bomb_map = np.empty((7, 9), dtype=np.uint8)
            bomb_map = self._get_explosion_map()

            for bomb in self._agent_bombs:
                if not np.any(np.isin(bomb_map, bomb, assume_unique=True)):
                    self._agent_bombs.remove(bomb)

            # logger.info(f"PIEETS BOMBS AFTER: {self._agent_bombs}")

        if diff_allowed > 0:
            bomb_map = np.empty((7, 9), dtype=np.uint8)
            bomb_map = self._get_explosion_map()

            x_coord, y_coord = self._player_game_area_coordinate('AGENT')
            agent_bomb_number = bomb_map[y_coord // 2, x_coord // 2]

            # logger.info(f"BOMB PLACED")
            # logger.info(f"PIEETS BOMBS BEFORE: {self._agent_bombs}")

            self._agent_bombs.append(agent_bomb_number)
            self._check_bomb_hits(x_coord, y_coord)

            self._score_agent_placed_bomb = 1

            # logger.info(f"PIEETS BOMBS AFTER: {self._agent_bombs}")

    def _agent_placed_bomb(self) -> int:
        """This function checks if Pieets placed a bomb.

        1 (True) if bomb placed.
        0 (False) if nothing happened
        -1 (False) if bomb exploded.

        Returns:
            int: See above.
        """
        bomb_amount_current = (
            self.pyboy.memory[self.AGENT_STATS_BOMB_MAX]
            - self.pyboy.memory[self.AGENT_STATS_BOMB_PLACED]
        )

        bomb_amount_last = self._agent_bombs_available

        diff_allowed = bomb_amount_last - bomb_amount_current

        self._agent_bombs_available = bomb_amount_current

        return diff_allowed

    def _check_bomb_hits(self, x_coord, y_coord) -> None:
        area_cache = self.pyboy.game_area()

        right_check = [
            x_coord + 2 + i if x_coord <= 15 + self._agent_bomb_range else 17
            for i in range(1, self._agent_bomb_range + 1)
        ]
        left_check = [
            x_coord - 2 - i if x_coord >= 2 - self._agent_bomb_range else 0
            for i in range(1, self._agent_bomb_range + 1)
        ]
        up_check = [
            y_coord - 2 - i if y_coord >= 2 + self._agent_bomb_range else 0
            for i in range(1, self._agent_bomb_range + 1)
        ]
        down_check = [
            y_coord + 2 + i if y_coord <= 11 - self._agent_bomb_range else 13
            for i in range(1, self._agent_bomb_range + 1)
        ]

        right_hit = self._check_bomb_x_hits(right_check, y_coord, area_cache)
        left_hit = self._check_bomb_x_hits(left_check, y_coord, area_cache)
        up_hit = self._check_bomb_y_hits(up_check, x_coord, area_cache)
        down_hit = self._check_bomb_y_hits(down_check, x_coord, area_cache)

        self._bomb_block_hits = right_hit + left_hit + up_hit + down_hit

    def _check_bomb_x_hits(self, coord_to_check, y_coord, area) -> int:
        for coord in coord_to_check:
            if coord <= 0 or coord >= 17:
                x_block_destroy = 0
                break
            x_destroy = area[y_coord, coord]

            if x_destroy == 10:
                x_block_destroy = 1
                break

            if x_destroy == 12:
                x_block_destroy = 0
                break
        return x_block_destroy

    def _check_bomb_y_hits(self, coord_to_check, x_coord, area) -> int:
        for coord in coord_to_check:
            if coord <= 0 or coord >= 13:
                y_block_destroy = 0
                break

            y_destroy = area[coord, x_coord]

            if y_destroy == 10:
                y_block_destroy = 1
                break

            if y_destroy == 12:
                y_block_destroy = 0
                break
        return y_block_destroy

    def _distance_checks(self) -> None:
        x_agent, y_agent = self._player_game_area_coordinate('AGENT')

        min_enemy_dist = 99
        enemy_dist_diff = 0  # Because of all enemies dead no assignment

        for enemy in self._ENEMY_ALIVE:
            x_enemy, y_enemy = self._player_game_area_coordinate(enemy)
            dist = np.abs(x_enemy - x_agent) + np.abs(y_enemy - y_agent)

            # logger.info(f"DISTANCE TO {enemy}: {dist}")

            if min_enemy_dist >= dist:
                # logger.info(f"LOWEST DIST TO ENEMY {enemy}")
                min_enemy_dist = dist
                enemy_dist_diff = self._last_min_enemy_distance - dist

        # logger.info(f"DIST DIFF {enemy_dist_diff}")

        if enemy_dist_diff >= 0:
            # logger.info("CLOSER THEN LAST STEP")
            self._score_last_dist = 1
            if min_enemy_dist < self._min_global_distance:  # MAYBE NOT EQUAL
                logger.info('GLOBAL LOWEST DIFF')
                self._min_global_distance = min_enemy_dist
                self._score_min_global_dist = 1
        if enemy_dist_diff < 0:
            # logger.info("FARTHER THEN LAST STEP")
            self._score_last_dist = -1

        self._last_min_enemy_distance = min_enemy_dist

        bomb_map = np.empty((7, 9), dtype=np.uint8)
        bomb_map = self._get_explosion_map()

        if bomb_map[y_agent // 2, x_agent // 2] != 0:
            self._agent_in_bomb_range = 1

    def _agent_bomb_max_increased(self) -> int:
        current_bomb_max = self._agent_bomb_max
        new_bomb_max = self.pyboy.memory[self.AGENT_STATS_BOMB_MAX]

        if current_bomb_max != new_bomb_max:
            # print(current_bomb_max, new_bomb_max)
            self._agent_bomb_max = new_bomb_max
            return 1

        return 0

    def _agent_bomb_range_increased(self) -> int:
        current_bomb_range = self._agent_bomb_range
        new_bomb_range = self.pyboy.memory[self.AGENT_STATS_BOMB_RANGE]

        if current_bomb_range != new_bomb_range:
            # print(current_bomb_range, new_bomb_range)
            self._agent_bomb_range = new_bomb_range
            return 1

        return 0

    # ----------------------------------------------------------------------------
    # Dunder methods

    def __repr__(self):
        # yapf: disable

        return (
            f"BOMBERMAN GB\nPyboyInstance: {self.pyboy}\n"
            f"AGENT (x/y): {self._full_player_coordinate('AGENT')}\n"
            f"AGENT (PACKAGE NR): {self._agent_bombs}\n"
            f"AGENT (INVENTAR): {self._agent_bombs_available}\n"
            f"AGENT (MAX): {self._agent_bomb_max}\n"
            f"AGENT (RANGE): {self._agent_bomb_range}\n"
            f"AGENT (KILL): {self._score_agent_kill}\n"
            f"Enemies Alive: {len(self._ENEMY_ALIVE)}\n"
            f"ENEMY1 (x/y): {self._full_player_coordinate('ENEMY_1')}\n"
            f"ENEMY2 (x/y): {self._full_player_coordinate('ENEMY_2')}\n"
            f"ENEMY3 (x/y): {self._full_player_coordinate('ENEMY_3')}\n" +
            super().__repr__()
        )
        # yapf: enable

    # ----------------------------------------------------------------------------
    # Not so important methods

    def _minimal_mapping(self) -> NDArray[uint8]:  # noqa: F821
        """This function returns the minimal mapping for BombermanGB.

        Returns:
            NDArray[uint8]: Mapping of the 384 tiles to a group
        """
        created_mapping = [
            1,
            1,
            1,
            1,
            1,
            1,
            1,
            1,
            1,
            1,
            1,
            1,
            1,
            1,
            1,
            1,
            1,
            1,
            1,
            1,
            1,
            1,
            1,
            1,
            1,
            1,
            1,
            1,
            1,
            1,
            1,
            1,
            4,
            4,
            4,
            4,
            4,
            4,
            4,
            4,
            4,
            4,
            4,
            4,
            4,
            4,
            4,
            4,
            4,
            4,
            4,
            4,
            4,
            4,
            4,
            4,
            4,
            4,
            4,
            4,
            4,
            4,
            4,
            4,
            4,
            4,
            4,
            4,
            4,
            4,
            4,
            4,
            4,
            4,
            4,
            4,
            4,
            4,
            4,
            4,
            4,
            4,
            4,
            4,
            4,
            4,
            4,
            4,
            4,
            4,
            4,
            4,
            4,
            4,
            4,
            4,
            4,
            4,
            4,
            4,
            4,
            4,
            4,
            4,
            4,
            4,
            4,
            4,
            4,
            4,
            4,
            4,
            4,
            4,
            4,
            4,
            4,
            4,
            4,
            4,
            4,
            4,
            4,
            4,
            4,
            4,
            4,
            4,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            5,
            5,
            5,
            5,
            6,
            6,
            6,
            6,
            7,
            7,
            7,
            7,
            8,
            8,
            8,
            8,
            9,
            9,
            9,
            9,
            9,
            9,
            9,
            9,
            9,
            9,
            9,
            9,
            9,
            9,
            9,
            9,
            9,
            9,
            9,
            9,
            9,
            9,
            9,
            9,
            9,
            9,
            9,
            9,
            9,
            9,
            9,
            9,
            9,
            9,
            9,
            9,
            9,
            9,
            9,
            9,
            9,
            9,
            9,
            9,
            9,
            9,
            9,
            9,
            9,
            9,
            9,
            9,
            9,
            9,
            9,
            9,
            9,
            9,
            9,
            9,
            9,
            9,
            9,
            9,
            9,
            9,
            9,
            9,
            9,
            9,
            9,
            9,
            9,
            9,
            9,
            9,
            9,
            9,
            9,
            9,
            9,
            9,
            9,
            9,
            9,
            9,
            9,
            9,
            9,
            9,
            9,
            9,
            9,
            9,
            9,
            9,
            0,
            0,
            0,
            0,
            10,
            10,
            10,
            10,
            10,
            10,
            10,
            10,
            10,
            10,
            10,
            10,
            10,
            10,
            10,
            10,
            10,
            10,
            10,
            10,
            0,
            0,
            0,
            0,
            12,
            12,
            12,
            12,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            11,
            11,
            11,
            11,
            11,
            11,
            11,
            11,
            11,
            11,
            11,
            11,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
        ]

        return np.array(created_mapping, dtype=np.uint8)

    def _save_picture(self, name=None):  # Maybe remove since other calls can be used.
        datestring = datetime.now(tz=datetime.timezone.utc).strftime(
            '%Y_%m_%d_%H_%M_%S_',
        )

        name = datestring + 'screenshot' if not name else datestring + name

        image = self.pyboy.screen.image
        image.save(f'./reports/vis/helper_func/{name}.png')

    def _full_player_coordinate(
        self,
        player: str,
    ) -> tuple[tuple[int, int], tuple[int, int]]:
        """This function returns the coordinates the "whole" player is standing.

        This is necessary, since _player_game_area_coordinate only returns the upperleft
        quarter of the full player.

        Args:
            player (str): Player to return coordinates for

        Returns:
            tuple[tuple[int, int], tuple[int, int]]: All coordinates.
        """
        x_upperleft_coordinate, y_upperleft_coordinate = (
            self._player_game_area_coordinate(player)
        )
        x_coord = [x_upperleft_coordinate, x_upperleft_coordinate + 1]
        y_coord = [y_upperleft_coordinate, y_upperleft_coordinate + 1]

        return x_coord, y_coord

    # -----------------------------------------------------------------------------
    # Functions handling navigation and game settings and not providing any more
    # use.

    def _navigate_to_password_screen(self) -> None:
        # logger.info("START: NAVIGATE TO PASSWORD SCREEN")
        # Skip to main menu
        self.pyboy.tick(200, render=False)
        self.pyboy.button('start')
        self.pyboy.tick(69, render=False)

        # Select password in main menu
        for _ in range(3):
            self.pyboy.button('down')
            self.pyboy.tick(10, render=False)
        self.pyboy.button('a')
        self.pyboy.tick(99, render=False)

        # logger.info("END:  NAVIGATE TO PASSWORD SCREEN")

    def _handle_password_screen(self) -> None:
        # logger.info("START: HANDLE PASSWORD SCREEN")
        for _ in range(5):
            self.pyboy.button('up')
            self.pyboy.tick(10, render=False)

        self.pyboy.button('right')
        self.pyboy.tick(10, render=False)

        for _ in range(6):
            self.pyboy.button('up')
            self.pyboy.tick(10, render=False)

        self.pyboy.button('right')
        self.pyboy.tick(10, render=False)

        for _ in range(5):
            self.pyboy.button('up')
            self.pyboy.tick(10, render=False)

        self.pyboy.button('right')
        self.pyboy.tick(10, render=False)

        for _ in range(6):
            self.pyboy.button('up')
            self.pyboy.tick(10, render=False)

        self.pyboy.button('start')
        self.pyboy.tick(100, render=False)
        # logger.info("END:  HANDLE PASSWORD SCREEN")

    def _set_enemies(self, n_enemy=0, shuffle=False) -> None:
        """Selects n enemies.

        Always selects the furthest enemy from player. Agent used to wait for
        enemies to free him.

        Args:
            n_enemy (int): Number of enemies
            shuffle (bool, optional): Shuffle enemy selection. Defaults to None.
        """
        enemy_list = np.arange(2, -1, -1)  # Reverse so at 1v1 most away enemy

        logger.info(f'START: SET ENEMIES {n_enemy}')

        if shuffle:
            logger.info(f'SHUFFLE: SET ENEMIES {n_enemy}')
            np.random.default_rng().shuffle(enemy_list)

        selected_enemies = enemy_list[:n_enemy]
        logger.info(f'SELECTED: ENEMIES {selected_enemies+2}')

        def select_enemie(enemy):
            if enemy != 0:
                for _ in range(enemy):
                    self.pyboy.button('right')
                    self.pyboy.tick(2, render=False)

            self.pyboy.button('down')
            self.pyboy.tick(2, render=False)

            if enemy != 0:
                for _ in range(enemy):
                    self.pyboy.button('left')
                    self.pyboy.tick(2, render=False)

        for player in selected_enemies:
            select_enemie(player)

        self.pyboy.button('start')
        self.pyboy.tick(69, render=False)
        logger.info(f'END:SET ENMIES {n_enemy}')

    def _handle_rules_screen(self, win=1, time=1) -> None:
        # logger.info(f"START: SETTING RULES Win:{win}, Time:{time}")

        time_diff = 3 - time
        win_diff = 4 - win

        if time_diff == 0 and win_diff == 0:
            self.pyboy.button('start')
            self.pyboy.tick(46, render=False)

        if time_diff < 0:
            for _ in range(time - 3):
                self.pyboy.button('right')
                self.pyboy.tick(5, render=False)
        if time_diff > 0:
            for _ in range(3 - time):
                self.pyboy.button('left')
                self.pyboy.tick(5, render=False)

        self.pyboy.button('down')
        self.pyboy.tick(5, render=False)

        if win_diff < 0:
            for _ in range(win - 4):
                self.pyboy.button('right')
                self.pyboy.tick(5, render=False)
        if win_diff > 0:
            for _ in range(4 - win):
                self.pyboy.button('left')
                self.pyboy.tick(5, render=False)

        self.pyboy.button('start')
        self.pyboy.tick(69, render=False)
        # logger.info(f"END:   SETTING RULES Win:{win}, Time:{time}")

    def _select_stage_screen(self, stage=1):
        # logger.info(f"START: SELECT STAGE")
        self.pyboy.button('start')
        self.pyboy.tick(46, render=True)
        # logger.info(f"END:   SELECT STAGE")
