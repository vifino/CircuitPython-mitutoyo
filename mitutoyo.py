"""
`mitutoyo`: A library for the Mitutoyo Digimatic (SPC) protocol.
================================================================

This library is an implementation of the Mitutoyo Digimatic
protocol used to read data from gauges and scales.

It was written as a first project with CircuitPython.
Data used to implement this were Mitutoyo datasheets.

* Author(s): Adrian "vifino" Pistol

Implementation Notes
--------------------
**Hardware:**
* You need the `data` and `clock` pins - which are pin 2 and 3 on a Digimatic 10-pin cable - configured as inputs with pullup.
* You need to connect the `req` pin to a NPN with a 10kΩ resistor, with the open collector output to `!req`.
* Optionally, you can connect `ready` - pin 4 on a Digimatic 10-pin cable - as an input with a pullup to know when to read.

**Software:**
* CircuitPython 5.0 tested, older versions and MicroPython might work.

"""

# TODO: vifino: acquire more Mitutoyo gear, it is beautiful.

__repo__ = "https://github.com/vifino/circuitpython-mitutoyo"
__version__ = "1.0.0"

class Digimatic():
    def __init__(self, **args):
        if not "data" in args:
            raise "Missing `data` pin in arguments!"
        if not "clock" in args:
            raise "Missing `clock` pin in arguments!"
        if not "req" in args and not "nreq" in args:
            raise "Missing `req` or `nreq` in arguments!"

        self.pins = args

    def _req(self, val):
        if "req" in self.pins:
            self.pins["req"].value = val
        else:
            self.pins["nreq"].value = not val

    def read(self):
        clock = self.pins["clock"]
        data = self.pins["data"]

        # read bitstream
        self._req(True)
        bits = bytearray(52)
        for i in range(52):
            # wait for clock to go low
            while clock.value:
                continue

            bits[i] = data.value

            if i == 0: # deassert req after first bit read, so we know we have a response, but don't get more.
                self._req(False)

            # wait for clock to go up again
            while not clock.value:
                continue

        # assemble nibbles
        nibbles = bytearray(52/4)
        for n in range(52/4): # iterate over each nibble
            idx = n * 4
            nibbles[n] = (
                (bits[idx + 0] << 0) +
                (bits[idx + 1] << 1) +
                (bits[idx + 2] << 2) +
                (bits[idx + 3] << 3))

        # parse preamble
        # TODO: check if this contains useful data.
        for n in range(4):
            if nibbles[n] != 15:
                return None # invalid data

        # sign
        if nibbles[4] != 0 and nibbles[4] != 8:
            return None # invalid data
        sign_pos = nibbles[4] == 0

        # parse bcd the lazy way
        bcd = nibbles[5:11]
        number = int("".join([chr(0x30 + digit) for digit in bcd]))

        # decimal point
        number = number / 10**nibbles[11]

        # unit
        unit = nibbles[12] and "in" or "mm"

        value = sign_pos and number or -number
        if number == 0:
            value = 0 # don't like negative zeros.

        return self.Reading(value, unit)

    class Reading():
        def __init__(self, value, unit):
            self.value = value
            self.unit = unit

        def __str__(self):
            return "%s%s" % (self.value, self.unit)
