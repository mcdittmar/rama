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
# ----------------------------------------------------------------------
#
#  Test code for the interpretation of Measurements model
#    o special testing for manual overrides of default classes
#
# ----------------------------------------------------------------------
import numpy
import pytest

from astropy import units as u
from astropy.coordinates import SkyCoord, FK5
from astropy.time import Time

from rama.models.measurements import StdPosition
from rama import read


@pytest.fixture
def simple_position_file(make_data_path):
    return read(make_data_path('simple-position.vot.xml'))

# ----------------------------------------------------------------------
def test_parsing_coordinates(simple_position_file):
    """
    Test Adapters to AstroPy classes.
       o coords:SpaceCoord types  -> SkyCoord
       o coords:TimeInstant types -> Time

    Check in context of GLOBALS/scalar and TEMPLATES/column
    """
    sky_positions = simple_position_file.find_instances(StdPosition)
    assert len(sky_positions) == 2

    # scalar case
    pos = sky_positions[0]
    assert isinstance(pos.coord, SkyCoord)
    assert pos.coord.ra == 10.34209135 * u.Unit('deg')
    assert pos.coord.dec == 41.13232112 * u.Unit('deg')
    assert isinstance(pos.coord.frame, FK5)
    assert pos.coord.equinox == Time("J1975")
    # FIXME How to set the reference position in astropy?
    # assert "TOPOCENTER" == pos.coord.frame.ref_position.position

    # column case
    pos = sky_positions[1]
    assert isinstance(pos.coord, SkyCoord)
    assert pos.coord.ra[0]  == 10.0 * u.Unit('deg')
    assert pos.coord.dec[0] == 11.0 * u.Unit('deg')
    assert pos.coord.ra[1]  == 20.0 * u.Unit('deg')
    assert pos.coord.dec[1] == 21.0 * u.Unit('deg')
    assert isinstance(pos.coord.frame, FK5)
    assert pos.coord.equinox == Time("J1975")
    # FIXME How to set the reference position in astropy?
    # assert "TOPOCENTER" == pos.coord.frame.ref_position.position
