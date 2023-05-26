import os
import threading
import signal
import curses
import time
import pygame
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
HOTKEY_TOGGLE_DEBUG = "d" # toggle debug mode (only on "curses mode")
HIGH_VOL = 0.30 # normal volume to play sound files
LOW_VOL = 0.06 # low volume when to fade down to on button press
FADE_DURATION = 0.8
FADE_STEPS = 128 # should be reasonable hight to avoid clips and bips
DEBUG = False # can be toggled via HOTKEY_TOGGLE_DEBUG anyway now
# Config END

this_dir = os.path.dirname(__file__) + os.path.sep

overlay_sound = pygame.mixer.Sound(this_dir + AUDIO_OVERLAY)
overlay_length = overlay_sound.get_length()
overlay_playing = False

pygame.mixer.music.load(this_dir +  AUDIO_BACK)
pygame.mixer.music.set_volume(HIGH_VOL)
pygame.mixer.music.play(-1) # -1: loopy loop all the way

# setup mcp2221 gpio
# led = digitalio.DigitalInOut(board.G0)
# led.direction = digitalio.Direction.OUTPUT
btn = digitalio.DigitalInOut(board.G3)
btn.direction = digitalio.Direction.INPUT

def main_loop():
	global DEBUG, overlay_playing
	if btn.value == True:
		play_overlay()
	# curses hotkeys
	if CURSES == True:
		c = stdscr.getch()
		if c == ord(HOTKEY_QUIT):
			quit_app()
		elif c == ord(HOTKEY_BUTTON):
			play_overlay()
		elif c == ord(HOTKEY_TOGGLE_DEBUG):
			DEBUG = not DEBUG
			print("\rDebug mode {}\r".format(DEBUG))
		elif c == ord(HOTKEY_INFO):
			print("\rMusic: {}\r\nOverlay: {}\r\nOverlay length: {}\r\nCurrent mixer volume: {}\r\nButton state: {}\r".format(
				AUDIO_BACK, AUDIO_OVERLAY, overlay_length, pygame.mixer.music.get_volume(), btn.value))


def play_overlay():
	global overlay_playing
	if overlay_playing == False:
		overlay_playing = True

		# TODO: maybe use endevent etc for better handling? https://www.pygame.org/docs/ref/mixer.html#pygame.mixer.Channel.set_endevent ... then also throw away threading?

		debug("fade down")
		fade_vol_down_thread = threading.Thread(target=fade, args=(HIGH_VOL, LOW_VOL, pygame.mixer.music.set_volume))
		fade_vol_down_thread.start()
		time.sleep(FADE_DURATION)

		debug("play that overlay sound (length: {}) ...".format(overlay_length))
		overlay_sound.play()
		time.sleep(overlay_length)

		debug("fade up")
		fade_vol_up_thread = threading.Thread(target=fade, args=(LOW_VOL, HIGH_VOL, pygame.mixer.music.set_volume))
		fade_vol_up_thread.start()
		time.sleep(FADE_DURATION)

		overlay_playing = False


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

# --

# Listen for interrupt signal
signal.signal(signal.SIGINT, quit_app)

while True:
	try:
		time.sleep(0.02) # do some minimum relaxing
		main_loop()
	except Exception as e:
		quit_app(exception=e)
