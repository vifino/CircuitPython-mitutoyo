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

- You need the 'data' and 'clock' pins configured as inputs with pullup.
  They are pin 2 and 3 on a Digimatic 10-pin cable.

- Connect the 'req' pin to a NPN with a 10kΩ resistor and the open collector output to '!req'.
  On a Digimatic 10-pin cable, '!req' is pin 5.

- Optionally, you can connect 'ready' as an input with a pullup to know when to read.
  On a Digimatic 10-pin cable, 'ready' is pin 4.

**Software:**

- CircuitPython 5.0 tested, older versions should work.
  MicroPython should also work, thanks to Adafruit Blinka.

"""

# TODO: vifino: acquire more Mitutoyo gear, it is beautiful.

__repo__ = "https://github.com/vifino/CircuitPython-mitutoyo"
__version__ = "1.0.0"


import digitalio


class Digimatic:
    """Mitutoyo Digimatic SPC implementation for CircuitPython.
    Provide either 'req' or 'nreq'. 'req' takes precedence.

    :param ~microcontroller.Pin data: data pin
    :param ~microcontroller.Pin clock: clock pin
    :param ~microcontroller.Pin req: non-inverted data request pin, alternative to 'nreq'
    :param ~microcontroller.Pin nreq: inverted data request pin, alternative to 'req'
    """

    UNITS = {0: "mm", 1: "in"}

    def __init__(self, **args):
        if "data" not in args:
            raise "Missing `data` pin in arguments!"
        if "clock" not in args:
            raise "Missing `clock` pin in arguments!"
        if "req" not in args and "nreq" not in args:
            raise "Missing `req` or `nreq` in arguments!"

        pins = {}
        for name, pin in args.items():
            if type(pin).__name__ == "Pin":  # board pin
                dio = digitalio.DigitalInOut(pin)
                if name in ["req", "nreq"]:
                    dio.direction = digitalio.Direction.OUTPUT
                else:
                    dio.direction = digitalio.Direction.INPUT
                    dio.pull = digitalio.Pull.UP
                pins[name] = dio
            else:
                pins[name] = pin

        self.pins = pins

        # preallocate buffers
        self.bits = bytearray(52)
        self.nibbles = bytearray(13)

    def _req(self, val):
        if "req" in self.pins:
            self.pins["req"].value = val
        else:
            self.pins["nreq"].value = not val

    def read(self):
        """Attempt to read a value from the connected instrument.

        :return: A reading or none if data is unparsable
        :rtype: :class:`mitutoyo.Digimatic.Reading`
        """

        clock = self.pins["clock"]
        data = self.pins["data"]

        # read bitstream
        self._req(True)
        for i in range(52):
            # wait for clock to go low
            while clock.value:
                continue

            self.bits[i] = data.value

            if i == 0:  # deassert req after first bit read, so we only get one response
                self._req(False)

            # wait for clock to go up again
            while not clock.value:
                continue

        # assemble nibbles
        for n in range(13):  # iterate over each nibble
            idx = n * 4
            self.nibbles[n] = (
                (self.bits[idx + 0] << 0)
                + (self.bits[idx + 1] << 1)
                + (self.bits[idx + 2] << 2)
                + (self.bits[idx + 3] << 3)
            )

        # parse preamble
        # TODO: check if this contains useful data.
        for n in range(4):
            if self.nibbles[n] != 15:
                return None  # invalid data

        # sign
        if self.nibbles[4] != 0 and self.nibbles[4] != 8:
            return None  # invalid data
        sign_pos = self.nibbles[4] == 0

        # convert bcd sequence to integer
        number = 0
        bcd = self.nibbles[5:11]
        for i in range(6):
            number += bcd[i] * (10 ** (5 - i))

        # decimal point
        number = number / 10 ** self.nibbles[11]

        # unit
        unit = self.UNITS.get(self.nibbles[12])

        value = number if sign_pos else -number
        if number == 0:
            value = 0.0  # don't like negative zeros.

        return self.Reading(value, unit)

    class Reading:
        """A Reading from a Mitutoyo Digimatic instrument."""

        def __init__(self, value, unit):
            self.value = value
            """The value returned by the instrument. (`float`)"""
            self.unit = unit
            """The unit the reading's value is in. (`str`)"""

        def __str__(self):
            return "%s%s" % (self.value, self.unit)

    def read_cm(self):
        """Attempt to read from a connected instrument, but always return the value in centimeters.

        :return: centimeters
        :rtype: float
        """

        reading = self.read()
        if not reading:
            return None

        if reading.unit == "mm":
            return reading.value * 10
        if reading.unit == "in":
            return reading.value * 2.54

        # Unlikely, but future proof.
        raise "Reading has unknown unit: %s" % reading.unit
