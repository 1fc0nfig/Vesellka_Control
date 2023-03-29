# Program for UMPRUM Controller running on Raspberry Pico
# Created by Marek Vavrinek & Matyas Cerny
# Vesellka works 2023

import time
import board
import digitalio
import analogio
import busio
import usb_midi
import neopixel
import supervisor

import adafruit_midi
from adafruit_midi.note_off import NoteOff
from adafruit_midi.note_on import NoteOn
from adafruit_midi.control_change import ControlChange

def led_init_sequence(led_strips, num_pixels=2, delay=0.05):
    """Animate the LED strips during the startup."""
    # Turn on each LED strip one by one
    for strip in led_strips:
        for i in range(num_pixels):
            strip[i] = (10, 10, 10, 255)
            strip.write()
            time.sleep(delay)

    # Turn off each LED strip one by one
    for strip in led_strips:
        for i in range(num_pixels):
            strip[i] = (0, 0, 0, 0)
            strip.write()
            time.sleep(delay)

def indicate_print_error(led_strip, led_strip_pixel_num, error_color=(255, 0, 0, 255), delay=0.1):
    # LIGHT UP THE LIGHTSTRIP
    for i in range(3):
        # TURN RED
        time.sleep(delay)
        for i in range(light_strip_pixel_num):
            if i > 23:
                light_strip[i] = (255, 0, 0, 0)
                light_strip.write()
        # TURN OFF
        time.sleep(delay)
        for i in range(light_strip_pixel_num):
            if i > 23:
                light_strip[i] = (0, 0, 0, 0)
                light_strip.write()
    
    time.sleep(delay)
    # TURN WHITE
    for i in range(light_strip_pixel_num):
            if i > 23:
                light_strip[i] = (0, 0, 0, 255)
                light_strip.write()
            

midi = adafruit_midi.MIDI(midi_out=usb_midi.ports[1], out_channel=0)

# Faders
faders = []
fader_1 = analogio.AnalogIn(board.A0)
fader_2 = analogio.AnalogIn(board.A1)
fader_3 = analogio.AnalogIn(board.A2)
faders.extend([fader_1, fader_2, fader_3])
fader_last_value = [0, 0, 0]

# LED strips
num_pixels = 2
led_pins = [board.GP10, board.GP11, board.GP12, board.GP13, board.GP14, board.GP15, board.GP16, board.GP17, board.GP18]
led_strips = [neopixel.NeoPixel(pin, num_pixels, bpp=4) for pin in led_pins]
brightness = 1

light_strip_pixel_num = 40
light_pin = board.GP19
light_strip = neopixel.NeoPixel(light_pin, light_strip_pixel_num, bpp=4)
light_strip.brightness = brightness


# Lightstrip brightness
for strip in led_strips:
    strip.brightness = brightness


# Add a new variable to store the index of the last pressed button
last_pressed = None

# Buttons and MIDI
track_pins = [board.GP0, board.GP1, board.GP2, board.GP3, board.GP4, board.GP5, board.GP6, board.GP7, board.GP8, board.GP9]
buttons = []

for pin in track_pins:
    tmp_pin = digitalio.DigitalInOut(pin)
    tmp_pin.direction = digitalio.Direction.INPUT
    tmp_pin.pull = digitalio.Pull.DOWN
    buttons.append(tmp_pin)

pressed = [False] * len(track_pins)

# Onboard LED
led = digitalio.DigitalInOut(board.LED)
led.direction = digitalio.Direction.OUTPUT

# Moving average filter and threshold for faders
moving_average_size = 50
fader_threshold = 500
fader_raw_values = [[], [], []]
fader_raw_average_values = [0, 0, 0]

# Blink the onboard LED to indicate a startup
for i in range(3):
    led.value = True
    time.sleep(0.1)
    led.value = False
    time.sleep(0.1)

print("INITIALIZING...")
# # INIT SEQUENCE
# led_init_sequence(led_strips, delay=0)
# # LIGHT UP THE LIGHTSTRIP
# for i in range(light_strip_pixel_num):
#     light_strip[i] = (0, 0, 0, 255)
#     light_strip.write()
#     time.sleep(0.1)

# # indicate_print_error(light_strip, light_strip_pixel_num)

print("READY!")

# Main loop
while True:
    # Faders
    for fad_index, fade in enumerate(faders):

        fader_raw_values[fad_index].append(fade.value)
        if len(fader_raw_values[fad_index]) > moving_average_size:
            fader_raw_values[fad_index].pop(0)
            
        average_value = sum(fader_raw_values[fad_index]) / len(fader_raw_values[fad_index])
        value_difference = abs(average_value - fader_raw_average_values[fad_index])
        led.value = False

        if value_difference > fader_threshold:
            fader_raw_average_values[fad_index] = average_value
            mapped_value = int(127 * average_value / 65535)

            # print("Fader " + str(fad_index + 1) + ": " + str(mapped_value))

            if mapped_value != fader_last_value[fad_index]:
                fader_last_value[fad_index] = mapped_value
                led.value = True
                midi.send(ControlChange(14 + fad_index, mapped_value))

    # Buttons and LEDs
    for button_index, but in enumerate(buttons):
        # True of button is pressed
        if but.value:
            if not pressed[9]:
                if not pressed[button_index]:
                    # Midi buttons
                    # track buttons
                    if button_index >= 0 and button_index <= 4:
                        print("TRACK: Sending note " + str(36 + button_index))
                        # Turn off the LED strip of the last pressed button if it's not None
                        if last_pressed is not None:
                            led_strips[last_pressed][0] = (0, 0, 0, 0)
                            led_strips[last_pressed][1] = (0, 0, 0, 0)

                        pressed[button_index] = True
                        led.value = True
                        midi.send(NoteOn(36 + button_index, 127))
                        
                        # Turn on the corresponding LED strip
                        for i in range(num_pixels):
                            led_strips[button_index][i] = (100, 100, 100, 255)
                        
                        # Update last_pressed
                        last_pressed = button_index
                    
                    # Print button
                    if button_index == 8:
                        print("print")
                        pressed[button_index] = True
                        led.value = True

                        # Turn on the corresponding LED strip
                        for i in range(num_pixels):
                            led_strips[button_index][i] = (100, 100, 100, 255)
                        
                        # Update last_pressed
                        last_pressed = button_index
                    
                    # OPTION button
                    if button_index == 9:
                        print("option")
                        pressed[button_index] = True
                        led.value = True

                # FX buttons
                if button_index >= 5 and button_index <= 7 and not pressed[button_index]:
                    print("FX: Sending note " + str(36 + button_index))

                    pressed[button_index] = True
                    led.value = True
                    midi.send(NoteOn(36 + button_index, 127))
                    
                    # Turn on the corresponding LED strip
                    for i in range(num_pixels):
                        led_strips[button_index][i] = (100, 100, 100, 255)

            # OPTION key combinations
            else:
                if not pressed[button_index]:
                    if button_index == 0:
                        print("option + track 1")
                        led.value = True
                        pressed[button_index] = True

                        # Perform reload
                        supervisor.reload()
        
        # Release handler
        else:
            # Send midi off signal for the track and fx buttons
            if pressed[button_index] and button_index < 8:
                pressed[button_index] = False
                led.value = False
                midi.send(NoteOff(36 + button_index, 0))

            # Do not send midi off signal for the print and option button
            elif pressed[button_index] and button_index >= 8 and button_index <= 9:
                pressed[button_index] = False
                led.value = False

            else:
                # Turn off the "FX" button LEDs when the button is released
                if button_index >= 5 and button_index <= 7:
                    for i in range(num_pixels):
                        led_strips[button_index][i] = (0, 0, 0, 0)
            