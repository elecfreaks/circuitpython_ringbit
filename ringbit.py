# SPDX-FileCopyrightText: Copyright ELECFREAKS
# SPDX-License-Identifier: MIT

"""
`ringbit`
====================================================

CircuitPython driver for the Ring:bit car.

"""

import time
import digitalio
import analogio
import microcontroller
import pwmio
import pulseio
from adafruit_motor import servo


class Unit():
    """Distance unit"""
    cm = 1
    inch = 2


class Ringbit():
    """Supports the Pico:ed ring:bit by ELECFREAKS"""

    def __init__(self, left_pin: microcontroller.Pin,
                 right_pin: microcontroller.Pin):
        """Init Ring:bit"""
        self._left_pin = pwmio.PWMOut(left_pin, frequency=50, duty_cycle=0)
        self._right_pin = pwmio.PWMOut(right_pin, frequency=50, duty_cycle=0)
        self._left_servo = servo.ContinuousServo(self._left_pin)
        self._right_pin = servo.ContinuousServo(self._right_pin)

    def set_speed(self, left_speed: int, right_speed: int):
        """Set the Ring:bit Car speed"""
        if left_speed > 100 or left_speed < -100 or \
                right_speed > 100 or right_speed < -100:
            raise ValueError('speed error, -100~100')
        self._left_servo.throttle = left_speed / 100
        self._right_pin.throttle = - right_speed / 100

    def get_distance(self, pin: microcontroller.Pin, unit: Unit):
        """Gets the distance detected by ultrasound"""
        _ultrasonic_pin = digitalio.DigitalInOut(pin)
        _ultrasonic_pin.direction = digitalio.Direction.OUTPUT
        _ultrasonic_pin.value = True
        time.sleep(0.00001)
        _ultrasonic_pin.value = False
        _ultrasonic_pin.deinit()
        pulses = pulseio.PulseIn(pin)
        while len(pulses) == 0:
            pass
        pulses.pause()
        distance = pulses.popleft() * 34 / 2 / 1000 + 7
        pulses.clear()
        pulses.deinit()
        if unit == Unit.cm:
            return distance
        elif unit == Unit.inch:
            return distance / 2.54
        else:
            raise ValueError('unit error,please select Unit.cm or Unit.inch')

    def get_tracking(self, pin: microcontroller.Pin):
        """Gets the status of the patrol sensor"""
        _tracking_pin = analogio.AnalogIn(pin)
        _tracking_value = _tracking_pin.value
        _tracking_pin.deinit()
        if _tracking_value < 9600:
            return 11
        elif 9600 < _tracking_value < 15040:
            return 10
        elif 15040 < _tracking_value < 19200:
            return 1
        elif 19200 < _tracking_value < 38400:
            return 0
