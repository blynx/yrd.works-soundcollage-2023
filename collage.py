import os
import threading
import signal
import curses
import time
import pygame
import board
import digitalio

# Using curses extension for simple terminal keyboard handling
# https://docs.python.org/3/howto/curses.html
# Revert this when exiting ... otherwise console is shit
# No terminal for systemd auto start -> no curses
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

# Config START
WAV_BACK = "audio-back.mp3"
WAV_OVERLAY = "audio-overlay.mp3"
HOTKEY_BUTTON = "p"
HOTKEY_QUIT = "q"
HOTKEY_INFO = "i"
HOTKEY_TOGGLE_DEBUG = "d"
HIGH_VOL = 0.30
LOW_VOL = 0.06
FADE_DURATION = 0.8
FADE_STEPS = 128
DEBUG = False
# Config END

this_dir = os.path.dirname(__file__) + os.path.sep

overlay_sound = pygame.mixer.Sound(this_dir + WAV_OVERLAY)
overlay_length = overlay_sound.get_length()
overlay_playing = False

pygame.mixer.music.load(this_dir +  WAV_BACK)
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
				WAV_BACK, WAV_OVERLAY, overlay_length, pygame.mixer.music.get_volume(), btn.value))


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
		print(exception) # what about strack trace?
	quit()

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
