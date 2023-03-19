import time
import board
import digitalio

led = digitalio.DigitalInOut(board.G0)
led.direction = digitalio.Direction.OUTPUT
btn = digitalio.DigitalInOut(board.G1)
btn.direction = digitalio.Direction.INPUT

led.value = False

print("ready")
while True:
	time.sleep(0.05)
	if btn.value == True:
		led.value = True
	else:
		led.value = False
