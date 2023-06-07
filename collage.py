import os
import threading
import signal
import curses
import time
import pygame

start_with_button = os.environ.get('BLINKA_MCP2221') == "1"
if start_with_button:
	print("\rStarting with Adafruit MCP2221 button")
	import board
	import digitalio

# Using curses extension for simple terminal keyboard handling
# Curses? "The curses library supplies a terminal-independent screen-painting and keyboard-handling facility for text-based terminals"
# https://docs.python.org/3/howto/curses.html
# Revert this when exiting ... otherwise console is shit
# No terminal when starting this script via systemd auto start -> no curses
CURSES = True
try:
	stdscr = curses.initscr()
	curses.cbreak()
	curses.noecho()
	stdscr.keypad(True)
	stdscr.nodelay(True)
	print("\rStarting with curses.")
except:
	CURSES = False
	print("Starting WITHOUT curses.")

# Using pygame for music and sound playback
#   Music https://www.pygame.org/docs/ref/music.html
#   Mixer https://www.pygame.org/docs/ref/mixer.html
#         https://coderslegacy.com/python/pygame-mixer/
#   Sound https://www.pygame.org/docs/ref/mixer.html#pygame.mixer.Sound
#   Channel https://www.pygame.org/docs/ref/mixer.html#pygame.mixer.Channel
pygame.init()
pygame.mixer.init()

# Configure environment variables in "audio_config.env" file (copy & edit audio_config.env.example)
AUDIO_BACK = os.environ.get('AUDIO_BACK_FILE') or "audio-back-default.mp3"
AUDIO_OVERLAY = os.environ.get('AUDIO_OVERLAY_FILE') or "audio-overlay-default.mp3"

# Config START
HOTKEY_BUTTON = "p" # THE BUTTON (only on "curses mode")
HOTKEY_QUIT = "q" # quit (only on "curses mode")
HOTKEY_INFO = "i" # show some info (only on "curses mode")
HOTKEY_STOP = "s" # stop overlay
HOTKEY_TOGGLE_DEBUG = "d" # toggle debug mode (only on "curses mode")
HOTKEY_STOP_TIME = 3000
HIGH_VOL = 0.30 # normal volume to play sound files
LOW_VOL = 0.06 # low volume when to fade down to on button press
FADE_DURATION = 0.8
FADE_STEPS = 128 # should be reasonable hight to avoid clips and bips
DEBUG = False # can be toggled via HOTKEY_TOGGLE_DEBUG anyway now
# Config END

this_dir = os.path.dirname(__file__) + os.path.sep

overlay_sound = pygame.mixer.Sound(this_dir + AUDIO_OVERLAY)
global_overlay_session = 0
overlay_length = overlay_sound.get_length()
hotkey_pressed_time = None

pygame.mixer.music.load(this_dir +  AUDIO_BACK)
pygame.mixer.music.set_volume(HIGH_VOL)
pygame.mixer.music.play(-1) # -1: loopy loop all the way

# setup mcp2221 gpio
# led = digitalio.DigitalInOut(board.G0)
# led.direction = digitalio.Direction.OUTPUT
btn = None
if start_with_button:
	btn = digitalio.DigitalInOut(board.G3)
	btn.direction = digitalio.Direction.INPUT

def main_loop():
	global DEBUG, hotkey_pressed_time
	if start_with_button and btn.value == True:
		if hotkey_pressed_time == None:
			play_overlay()
			hotkey_pressed_time = now()
		elif now() + HOTKEY_STOP_TIME > hotkey_pressed_time:
			stop_overlay()
	else:
		hotkey_pressed_time = None
	# curses hotkeys
	if CURSES == True:
		c = stdscr.getch()
		if c == ord(HOTKEY_QUIT):
			quit_app()
		elif c == ord(HOTKEY_BUTTON):
			play_overlay()
		elif c == ord(HOTKEY_STOP):
			stop_overlay()
		elif c == ord(HOTKEY_TOGGLE_DEBUG):
			DEBUG = not DEBUG
			print("\rDebug mode {}\r".format(DEBUG))
		elif c == ord(HOTKEY_INFO):
			print("\rMusic: {}\r\nOverlay: {}\r\nOverlay length: {}\r\nOverlay channels: {}\r\nCurrent mixer volume: {}r".format(
				AUDIO_BACK, AUDIO_OVERLAY, overlay_sound.get_num_channels(), overlay_length, pygame.mixer.music.get_volume()))


def play_overlay():
	global global_overlay_session
	if overlay_sound.get_num_channels() == 0:
		debug("fade down")
		fade_vol_down_thread = threading.Thread(target=fade, args=(HIGH_VOL, LOW_VOL, pygame.mixer.music.set_volume))
		fade_vol_down_thread.start()
		time.sleep(FADE_DURATION)
		global_overlay_session = global_overlay_session + 1
		actually_play_overlay_thread = threading.Thread(target=actually_play_overlay, args=(overlay_sound, global_overlay_session))
		actually_play_overlay_thread.start()


def stop_overlay():
	if overlay_sound.get_num_channels() > 0:
		debug("fade up")
		fade_vol_up_thread = threading.Thread(target=fade, args=(LOW_VOL, HIGH_VOL, pygame.mixer.music.set_volume))
		fade_vol_up_thread.start()
		time.sleep(FADE_DURATION)
		overlay_sound.fadeout(int(FADE_DURATION * 1000))


def actually_play_overlay(overlay_sound, this_overlay_session):
	global global_overlay_session
	debug("play that overlay sound (length: {}) ...".format(overlay_length))
	overlay_sound.play()
	time.sleep(overlay_length)
	if global_overlay_session == this_overlay_session:
		debug("fade up")
		fade_vol_up_thread = threading.Thread(target=fade, args=(LOW_VOL, HIGH_VOL, pygame.mixer.music.set_volume))
		fade_vol_up_thread.start()
		time.sleep(FADE_DURATION)


def fade(start, end, cb, duration=FADE_DURATION, steps=FADE_STEPS):
	step = (end - start) / steps
	wait = duration / steps
	current_vol = start
	for s in range(steps):
		time.sleep(wait)
		next_vol = current_vol + step
		debug("fade step: {}, from {} to {}".format(s, current_vol, next_vol))
		cb(next_vol)
		current_vol = next_vol


# handle quitting via exception and "SIGINT", all arguments handle both cases
def quit_app(sig=None, frame=None, exception=None):
	if CURSES == True:
		# Undo curses settings
		curses.nocbreak()
		curses.echo()
		stdscr.keypad(False)
		stdscr.nodelay(False)
		curses.endwin()
	if exception != None:
		print("\nOh no!")
		print(exception) # what about stack trace?
	quit()

# print to curses screen, prepend carriage return
def debug(msg):
	if DEBUG == True:
		print("\r{}".format(msg))

def now():
	return round(time.time() * 1000)

# --

# Listen for interrupt signal
signal.signal(signal.SIGINT, quit_app)

while True:
	try:
		time.sleep(0.02) # do some minimum relaxing
		main_loop()
	except Exception as e:
		quit_app(exception=e)
