# Copyright 2018 Smithsonian Astrophysical Observatory
#
# Redistribution and use in source and binary forms, with or without modification, are permitted provided that the
# following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice, this list of conditions and the following
# disclaimer.
#
# 2. Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following
# disclaimer in the documentation and/or other materials provided with the distribution.
#
# 3. Neither the name of the copyright holder nor the names of its contributors may be used to endorse or promote
# products derived from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES,
# INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
# WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
# --------------------------------------------------------------------------------------------------------------
from astropy import units as u
from dateutil import parser

from rama.utils.registry import VO

# ----------------------------------------------------------------------
# Manually generated classes covering the primitive base types
# ----------------------------------------------------------------------
@VO("ivoa:string")
class StringQuantity:
    def __new__(cls, value, _):
        return str(value)

@VO("ivoa:Unit")
class VOUnit:
    """
      Handled by AstroPy Units.
    """
    def __new__(cls, value, _):
        return u.Unit(value)

@VO("ivoa:anyURI")
class anyURI(StringQuantity):
    pass

@VO("ivoa:boolean")
class VOBool:
    def __new__(cls, value, _):
        return value.lower() == 'true'

@VO("ivoa:integer")
class VOInteger:
    def __new__(cls, value, _):
        return int(value)

@VO("ivoa:nonnegativeInteger")
class VONonNegativeInteger:
    def __new__(cls, value, _):
        value = int(value)
        if value < 0:
            raise ValueError(f"Value must be positive: {value}")
        return value
    
@VO("ivoa:real")
class VOReal:
    def __new__(cls, value, _):
        return float(value)

@VO("ivoa:datetime")
class VODateTime:
    """
    Handled as a Python datetime instance.
    """
    def __new__(cls, value, _):
        return parser.parse(value)

@VO("ivoa:IntegerQuantity")
class IntegerQuantity:
    """
      Handled by AstroPy Quantity.
      NOTE: The value is converted to floating point..
    """
    def __new__(cls, value, unit):
        value = int(value)
        try:
            quantity = value * u.Unit(unit)
        except (ValueError, TypeError):
            quantity = value * u.dimensionless_unscaled
        return quantity

@VO("ivoa:RealQuantity")
class RealQuantity:
    """
      Handled by AstroPy Quantity.
    """
    def __new__(cls, value, unit):
        value = float(value)
        try:
            quantity = value * u.Unit(unit)
        except (ValueError, TypeError):
            quantity = value * u.dimensionless_unscaled
        return quantity
