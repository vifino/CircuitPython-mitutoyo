# This is a quick example how to read values from Mitutoyo Calipers.
# Assuming a Serpente board, with `req`, `clock`, `data` and `ready` connected to
# D0, D1, D2 and D3, respectively.

import board
import digitalio
import mitutoyo

pin_req = digitalio.DigitalInOut(board.D0)
pin_req.direction = digitalio.Direction.OUTPUT

pin_clock = digitalio.DigitalInOut(board.D1)
pin_clock.direction = digitalio.Direction.INPUT
pin_clock.pull = digitalio.Pull.UP
pin_data = digitalio.DigitalInOut(board.D2)
pin_data.direction = digitalio.Direction.INPUT
pin_data.pull = digitalio.Pull.UP
pin_ready = digitalio.DigitalInOut(board.D3)
pin_ready.direction = digitalio.Direction.INPUT
pin_ready.pull = digitalio.Pull.UP

print("Hello! Press the read button on the Calipers to print the value!")

meter = mitutoyo.Digimatic(clock=pin_clock, data=pin_data, req=pin_req)

while True:
    # wait until ready goes low
    while pin_ready.value:
        continue

    print(meter.read())

    # wait until ready goes up again to just get a single reading per press
    while not pin_ready.value:
        continue
