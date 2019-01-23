#   Copyright 2013 Dagda Ltd.
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
"""
This module provides classes for interfacing with an MCP48XX devices.
"""
from myDevices.devices.spi import SPI
from myDevices.devices.analog import DAC
from myDevices.plugins.analog import AnalogOutput


class MCP48XX(SPI, DAC):
    """Base class for interacting with MCP48XX devices."""

    def __init__(self, chip, channel_count, resolution):
        SPI.__init__(self, int(chip), 0, 8, 10000000)
        DAC.__init__(self, channel_count, resolution, 2.048)
        self.buffered=False
        self.gain=False
        self.shutdown=True
        self.values = [0 for i in range(channel_count)]

    def __str__(self):
        """Returns friendly name."""
        return "%s(chip=%d)" % (self.__class__.__name__, self.chip)

    def __analogRead__(self, channel, diff=False):
        """Read the analog input. Overrides ADC.__analogRead__.

        channel: Channel on the device
        diff: True if using differential input
        """
        return self.values[channel]

    def __analogWrite__(self, channel, value):
        """Writes the value to the specified channel. Overrides DAC.__analogWrite__."""
        self.shutdown=False
        d = [0x00, 0x00]
        d[0] |= (channel & 0x01) << 7                     # bit 15 = channel
        d[0] |= (self.buffered & 0x01) << 6               # bit 14 = ignored
        d[0] |= (not self.gain & 0x01) << 5               # bit 13 = gain
        d[0] |= (not self.shutdown & 0x01) << 4           # bit 12 = shutdown
        d[0] |= value >> (self._analogResolution - 4)     # bits 8-11 = msb data
        d[1] |= ((value << (12-self._analogResolution)) & 0xFF) # bits 4 - 7 = lsb data (4802) bits 2-7 (4812) bits 0-7 (4822)                              # bits 0 - 3 = ignored                       
        
        self.writeBytes(d)
        self.values[channel] = value

       
class MCP4802(MCP48XX):
    """Class for interacting with an MCP4802 device."""

    def __init__(self, chip=0):
        """Initializes MCP4921 device.

        Arguments:
        chip: The chip select
        """        
        MCP48XX.__init__(self, chip, 2, 8)


class MCP4812(MCP48XX):
    """Class for interacting with an MCP4812 device."""

    def __init__(self, chip=0):
        """Initializes MCP4812 device.

        Arguments:
        chip: The chip select
        """ 
        MCP48XX.__init__(self, chip, 2, 10)


class MCP4822(MCP48XX):
    """Class for interacting with an MCP4822 device."""

    def __init__(self, chip=0):
        """Initializes MCP4822 device.

        Arguments:
        chip: The chip select
        """ 
        MCP48XX.__init__(self, chip, 2, 12)


class MCP4822Test(MCP4822):
    """Class for simulating an MCP4822 device."""

    def __init__(self):
        """Initializes the test class."""
        self.bytes = None
        MCP4822.__init__(self)

    def writeBytes(self, data):
        """Write data bytes."""
        self.bytes = data
