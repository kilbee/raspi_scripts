#!/usr/bin/python3

"""
Simple script for controlling stepper motor: 28byj-48 uln2003
by step count, or by specified angle
(gear ratio variable used for different gear setups - change turn_ratio to adapt for different gear ratio)
clockwise (values greater than 0) or counter-clockwise (values below 0)

turn_sequence([30,-40,45,-30,45,10,-40,20,-60,40]) 		# example how to use sequence small turns in one go
turn_motor(steps = 10)																# example how to use function, but using step value
turn_motor(angle = -60)																# example how to use function, but using angle value
"""


import sys
import time
import RPi.GPIO as GPIO




GPIO.setmode(GPIO.BCM) 			# BCM GPIO references instead of physical pin numbers
step_pins = [24,25,7,8] 		# GPIO signals to use
for pin in step_pins:
	GPIO.setup(pin,GPIO.OUT)
	GPIO.output(pin, False)		# Set all pins as output


def all_pins_low():
	"""
	keep pins low to power motor controller only when used
	"""
	global step_pins
	for pin in range(0, 4):
		xpin = step_pins[pin]
		GPIO.output(xpin, False)


def turn_motor(steps = None, angle = None, speed = 1):
	"""
	Turns motor by specified steps or angle

	Parameters
	----------
	steps : int, optional
		number of steps to turn motor (2048 is full turn; negative for counter-clockwise)
	angle : int, optional
		angle to turn motor (negative for counter-clockwise)
	speed : float, optional
		speed divider - higher values mean lower speed
	"""
	turn_ratio = 6.693 						# angle turn multiplier - used to recalculate full turn with different gear ratios
	print("turnig:", angle)
	if steps is None and angle is None:
		return
	if speed < 1:
		speed = 1
	step_direction = 2 						# Set to 1 or 2 for clockwise; Set to -1 or -2 for anti-clockwise
	if steps is not None and steps < 0:
		steps = -steps
		step_direction = -2
	step_wait = 0.002
	# Define advanced sequence as shown in manufacturers datasheet (signals for stepper motor controller)
	step_seq = [	[1,0,0,1],
					[1,0,0,0],
					[1,1,0,0],
					[0,1,0,0],
					[0,1,1,0],
					[0,0,1,0],
					[0,0,1,1],
					[0,0,0,1]
				  ]
	step_count = len(step_seq)
	step_counter = 0
	if steps is not None:
		final_steps = steps
	if angle is not None:
		angle = int(angle * turn_ratio)
		final_steps, step_direction = map_angle_to_step(angle)
	for step in range(0, final_steps):
		#print(step_counter, step_seq[step_counter])
		for pin in range(0, 4):
			xpin = step_pins[pin]
			if step_seq[step_counter][pin]!=0:
				GPIO.output(xpin, True)
			else:
				GPIO.output(xpin, False)
		step_counter += step_direction

		# reset if we reach the end of the sequence
		if (step_counter >= step_count):
			step_counter = 0
		if (step_counter < 0):
			step_counter = step_count + step_direction

		# wait before moving on time.sleep(step_wait) to let motor keep up with script - empirical value balancing speed vs reliability
		time.sleep(step_wait * speed)
	all_pins_low()


def map_angle_to_step(angle):
	step_direction = 2
	if angle < 0:
		angle = angle * -1
		step_direction = -2
	angle_range = (360 - 0)
	step_range = (2048 - 0)
	step_count = ((angle * step_range) / angle_range)
	return int(step_count), step_direction


def turn_sequence(angles):
	for angle in angles:
		turn_motor(angle = angle)



if __name__ == "__main__":
	turn_motor(angle = -60)
