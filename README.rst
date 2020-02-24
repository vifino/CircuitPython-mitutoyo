`mitutoyo`: A library for the Mitutoyo Digimatic (SPC) protocol.
================================================================

.. image:: https://readthedocs.org/projects/circuitpython-mitutoyo/badge/?version=latest
    :target: https://circuitpython-mitutoyo.readthedocs.io/
    :alt: Documentation Status

.. image:: https://github.com/vifino/CircuitPython-mitutoyo/workflows/Build%20CI/badge.svg
    :target: https://github.com/vifino/CircuitPython-mitutoyo/actions
    :alt: Build Status

CircuitPython implementation of the Mitutoyo Digimatic SPC interface.


Dependencies
============
This driver depends on:

* `Adafruit CircuitPython <https://github.com/adafruit/circuitpython>`_

Please ensure all dependencies are available on the CircuitPython filesystem.
This is easily achieved by downloading
`the Adafruit library and driver bundle <https://circuitpython.org/libraries>`_.

Installing from PyPI
====================
.. note:: This library is not available on PyPI yet. Install documentation is included
   as a standard element. Stay tuned for PyPI availability!

On supported GNU/Linux systems like the Raspberry Pi, you can install the driver locally `from
PyPI <https://pypi.org/project/adafruit-circuitpython-mitutoyo/>`_. To install for current user:

.. code-block:: shell

    pip3 install circuitpython-mitutoyo

To install system-wide (this may be required in some cases):

.. code-block:: shell

    sudo pip3 install circuitpython-mitutoyo

To install in a virtual environment in your current project:

.. code-block:: shell

    mkdir project-name && cd project-name
    python3 -m venv .env
    source .env/bin/activate
    pip3 install circuitpython-mitutoyo

Usage Example
=============

.. code-block:: python

    import board
    import mitutoyo

    instrument = mitutoyo.Digimatic(req=board.D0, clock=board.D1, data=board.D2)

    reading = instrument.read()
    print(reading)  # human formatted
    print("Reading in %s: %f" %(reading.unit, reading.value))


Contributing
============

Contributions are welcome! Please read our `Code of Conduct
<https://github.com/vifino/CircuitPython-mitutoyo/blob/master/CODE_OF_CONDUCT.md>`_
before contributing to help this project stay welcoming.
