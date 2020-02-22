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
* You need the `data` and `clock` pins configured as inputs with pullup.
  They are pin 2 and 3 on a Digimatic 10-pin cable.
* Connect the `req` pin to a NPN with a 10kΩ resistor and the open collector output to `!req`.
  On a Digimatic 10-pin cable, `!req` is pin 5.
* Optionally, you can connect `ready` as an input with a pullup to know when to read.
  On a Digimatic 10-pin cable, `ready` is pin 4.

**Software:**
* CircuitPython 5.0 tested, older versions and MicroPython might work, but I doubt it.

"""

# TODO: vifino: acquire more Mitutoyo gear, it is beautiful.

__repo__ = "https://github.com/vifino/CircuitPython-mitutoyo"
__version__ = "1.0.0"

class Digimatic():
    """
    Mitutoyo Digimatic SPC implementation for CircuitPython.

    Parameters:
    data (pin): data pin
    clock (pin): clock pin
    req (pin) or nreq (pin): normal or inverted data request pin
    """

    def __init__(self, **args):
        if"data" not in args:
            raise "Missing `data` pin in arguments!"
        if "clock" not in args:
            raise "Missing `clock` pin in arguments!"
        if "req" not in args and "nreq" not in args:
            raise "Missing `req` or `nreq` in arguments!"

        self.pins = args

    def _req(self, val):
        if "req" in self.pins:
            self.pins["req"].value = val
        else:
            self.pins["nreq"].value = not val

    def read(self):
        """Read a value from the connected instrument."""
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

            if i == 0: # deassert req after first bit read, so we only get one response
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
        unit = "in" if nibbles[12] else "mm"

        value = number if sign_pos else -number
        if number == 0:
            value = 0 # don't like negative zeros.

        return self.Reading(value, unit)

    class Reading():
        """A Reading from a Mitutoyo Digimatic instrument."""
        def __init__(self, value, unit):
            self.value = value
            self.unit = unit

        def __str__(self):
            return "%s%s" % (self.value, self.unit)
