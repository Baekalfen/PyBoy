from pyboy.utils import WindowEvent
import pyboy as pyboy
import io

'''
This shows the basic functions you can use if you want to write a bot using only the game image as a human would see it.
Uses Super Mario Land 1 as an example.
'''

path_to_rom = '../SuperMarioLand1.gb'


def save_state_to_file(boy, path):
	boy.save_state(open(path, "wb"))


def load_state_from_file(boy, path, reset_keys=False):
	boy.load_state(open(path, "rb"))
	if reset_keys:
		for key in range(WindowEvent.RELEASE_ARROW_UP, WindowEvent.RELEASE_BUTTON_START + 1):
			boy.send_input(key)


def save_state(boy):
	file_like_object = io.BytesIO()
	file_like_object.seek(0)
	boy.save_state(file_like_object)
	return file_like_object


def load_state(boy, file_like_object, reset_keys=False):
	file_like_object.seek(0)
	boy.load_state(file_like_object)
	if reset_keys:
		for key in range(WindowEvent.RELEASE_ARROW_UP, WindowEvent.RELEASE_BUTTON_START + 1):
			boy.send_input(key)


def show_screen(screen):
	img = screen.screen_image()
	img.show()


def save_screen(screen, path):
	img = screen.screen_image()
	img.save(path)


def get_ndarray_from_screen(screen):
	return screen.screen_ndarray()


def invert_ndarray(array):
	return array.transpose(1, 0, *list(range(len(array.shape)))[2:])


def to_grayscale(source):
	import cv2
	return cv2.cvtColor(source, cv2.COLOR_RGB2GRAY)


# Use headless, so emulation is not displayed
boy = pyboy.PyBoy(path_to_rom, window_type="headless")
# Emulation speed of `0` means fastest possible execution.
boy.set_emulation_speed(0)

# Progress to start of the game
for i in range(75):
	boy.tick()
boy.send_input(WindowEvent.PRESS_BUTTON_START)
boy.tick()
boy.send_input(WindowEvent.RELEASE_BUTTON_START)
for i in range(17):
	boy.tick()

# load/save state with file
save_state_to_file(boy, 'sml1_start.state')
load_state_from_file(boy, 'sml1_start.state')

# save state in memory
state = save_state(boy)

# Send input and progress game by one tick
boy.send_input(WindowEvent.PRESS_ARROW_RIGHT)
boy.tick()
boy.send_input(WindowEvent.RELEASE_ARROW_RIGHT)

# load state to return to beginning
load_state(boy, state)

# Get the screen, this is the output you would see as a human
game_screen = boy.botsupport_manager().screen()
show_screen(game_screen)
save_screen(game_screen, 'sml1_start.png')

# Get screen info as ndarray. The format is (height, width, RGB), use invert_ndarray if you want (width, height, RGB)
screen_array = get_ndarray_from_screen(game_screen)
print(screen_array.shape)  # (144, 160, 3)
screen_array = invert_ndarray(screen_array)
print(screen_array.shape)  # (160, 144, 3)

# Convert from RGB to grayscale (0 - 255) (uses CV2)
# grayscale_screen_array = to_grayscale(screen_array)
# print(grayscale_screen_array.shape)  # (160, 144)
