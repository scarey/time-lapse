# MIT License (MIT)
# Copyright (c) 2023 Stephen Carey
# https://opensource.org/licenses/MIT

# Micropython code for taking time-lapse photos with your SLR.

from machine import Pin, SoftI2C
import ssd1306

import time
import os

from encoder_menu import set_data, get_integer, wrap_menu, selection, wizard, run_menu, get_values, set_oled, display


def display_at_random_row(text):
    display(text, '', row_start=int.from_bytes(os.urandom(1), 'big') % 52)


shutter_pin = Pin(25, Pin.OUT)

pics_taken = 0

i2c = SoftI2C(scl=Pin(22), sda=Pin(21))

oled = ssd1306.SSD1306_I2C(128, 64, i2c, addr=0x3d)
set_oled(oled)

set_data('finished', 'No')
set_data('num_pics', 20)
set_data('exposure', 30)
set_data('exposure_ms', 0)
set_data('delay', 1)
set_num_pics = get_integer(low_v=10, high_v=1000, increment=10, caption='Num Pictures', field='num_pics')
set_exposure_secs = get_integer(0, 90, 1, 'Exposure Secs', 'exposure')
set_exposure_ms = get_integer(0, 990, 10, 'Exposure Ms', 'exposure_ms')
set_delay = get_integer(1, 60, 1, 'Pic Delay', 'delay')
start_choices = selection('finished', ['Yes', 'No'])

settings_wizard = wizard(
    [("Number Pictures", set_num_pics), ("Exposure Seconds", set_exposure_secs), ("Exposure millis", set_exposure_ms),
     ("Delay Btw Pictures", set_delay)])
start_wizard = wizard([("Start", start_choices)])

root_menu = wrap_menu([('> Change Settings', settings_wizard), ('> Start', start_wizard)])

root_menu()  # Set up the initial root menu by calling its function
run_menu()  # Start the main loop running

config = get_values()
print("Done with menu: {}".format(config))

num_pics = config['num_pics'] * 10
exposure_time = config['exposure']
exposure_ms = config['exposure_ms'] * 10.0 / 1000.0
between_pics = config['delay']
display('{} at {}s'.format(num_pics, (exposure_time + exposure_ms)), 'Delay: {}'.format(between_pics))

print("Exposure time: {}".format(exposure_ms + exposure_time))
while pics_taken < num_pics:
    pics_taken = pics_taken + 1
    print("Taking pic {}...".format(pics_taken))
    shutter_pin.on()
    time.sleep(exposure_time + exposure_ms)
    shutter_pin.off()
    status = '{}/{} {}mins'.format(str(pics_taken), str(num_pics),
                                   str(round((num_pics - pics_taken) * (
                                           exposure_time + exposure_ms + between_pics) / 60)))
    display_at_random_row(status)
    if pics_taken != num_pics:
        time.sleep(between_pics)
print("Done!")
while True:
    display_at_random_row('Done!')
    time.sleep(10)
