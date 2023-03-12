import threading
import signal
import curses
import time
import pygame

# Using curses extension for simple terminal keyboard handling
# https://docs.python.org/3/howto/curses.html
# Revert this when exiting ... otherwise console is shit
stdscr = curses.initscr()
curses.cbreak()
stdscr.keypad(True)
curses.noecho()

# Using pygame for music and sound playback
#   Music https://www.pygame.org/docs/ref/music.html
#   Mixer https://www.pygame.org/docs/ref/mixer.html
#         https://coderslegacy.com/python/pygame-mixer/
#   Sound https://www.pygame.org/docs/ref/mixer.html#pygame.mixer.Sound
#   Channel https://www.pygame.org/docs/ref/mixer.html#pygame.mixer.Channel
pygame.init()

# Config START
# WAV_BACK = "schrammel.wav"
WAV_BACK = "Sealed_Book_45-xx-xx_ep07_The_Accusing_Corpse.wav"
WAV_OVERLAY = "flup.wav"
HOTKEY_BUTTON = "p"
HOTKEY_QUIT = "q"
HOTKEY_INFO = "i"
HOTKEY_TOGGLE_DEBUG = "d"
HIGH_VOL = 0.72
LOW_VOL = 0.06
FADE_DURATION = 0.8
FADE_STEPS = 128
DEBUG = False
# Config END

overlay_sound = pygame.mixer.Sound(WAV_OVERLAY)
overlay_length = overlay_sound.get_length()
overlay_playing = False # TODO: ARGH!!! # maybe use endevent? https://www.pygame.org/docs/ref/mixer.html#pygame.mixer.Channel.set_endevent ... then also throw away threading?

pygame.mixer.music.load(WAV_BACK)
pygame.mixer.music.set_volume(HIGH_VOL)
pygame.mixer.music.play(-1) # -1: loopy loop all the way

def main_loop():
	global DEBUG, overlay_playing
	c = stdscr.getch()
	if c == ord(HOTKEY_QUIT):
		quit_app()
	elif c == ord(HOTKEY_BUTTON):
		# TODO: why does overlay_playing thing not work?
		if overlay_playing == False:
			overlay_playing = True
			play_overlay()
	elif c == ord(HOTKEY_TOGGLE_DEBUG):
		DEBUG = not DEBUG
		print("\rDebug mode {}\r".format(DEBUG))
	elif c == ord(HOTKEY_INFO):
		print("\rMusic: {}\r\nOverlay: {}\r\nOverlay length: {}\r\nCurrent mixer volume: {}\r".format(
			WAV_BACK, WAV_OVERLAY, overlay_length, pygame.mixer.music.get_volume()))


def play_overlay():
	global overlay_playing
	debug("play that overlay sound (length: {}) ...".format(overlay_length))

	fade_vol_down_thread = threading.Thread(target=fade, args=(HIGH_VOL, LOW_VOL, pygame.mixer.music.set_volume))
	fade_vol_down_thread.start()

	debug(" ~~ OVERLAY PLAY' ~~")
	time.sleep(FADE_DURATION) # TODO: tweak overlay start !?
	overlay_sound.play()
	time.sleep(overlay_length + FADE_DURATION)
	overlay_playing = False

	fade_vol_up_thread = threading.Thread(target=fade, args=(LOW_VOL, HIGH_VOL, pygame.mixer.music.set_volume))
	fade_vol_up_thread.start()


# TODO: tweak fade function ... maybe even easing instead of linear?
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
	# Undo curses settings
	curses.nocbreak()
	stdscr.keypad(False)
	curses.echo()
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
		time.sleep(0.01) # do some minimum relaxing
		main_loop()
	except Exception as e: 
		quit_app(exception=e)
