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
#  Test code for the interpretation of Coords model
#    o special testing for manual overrides of default classes
#
# ----------------------------------------------------------------------
import numpy
import pytest

from numpy.testing import assert_array_equal

from astropy import units as u
from astropy.coordinates import SkyCoord, FK5, ICRS
from astropy.time import Time

from rama.models.measurements import StdPosition, StdTimeMeasure
from rama.models.coordinates import Point, JD, MJD, ISOTime
from rama import read

@pytest.fixture
def positions_file(make_data_path):
    return read(make_data_path('simple-position.vot.xml'))

@pytest.fixture
def times_file(make_data_path):
    return read(make_data_path('time.vot.xml'))

def test_skycoord_adapter(positions_file):
    """
    Test Adapters to AstroPy classes.
       o coords:Point types -> SkyCoord
       o Incompatible Points remain as Point

    Check in context of GLOBALS/scalar and TEMPLATES/column
    """
    sky_positions = positions_file.find_instances(StdPosition)
    assert len(sky_positions) == 5

    # globals instances:
    #   case: missing reference frame - can not convert
    pos = sky_positions[0]
    assert isinstance(pos.coord, Point)
    assert pos.coord.axis1 == 0.0 * u.Unit('deg')
    assert pos.coord.axis2 == 180.0 * u.Unit('deg')
    assert pos.coord.coord_sys.frame.ref_position.position == "TOPOCENTER"
    
    #   case: spherical coord in FK5
    pos = sky_positions[1]
    assert isinstance(pos.coord, SkyCoord)
    assert pos.coord.ra == 10.342 * u.Unit('deg')
    assert pos.coord.dec == 41.132 * u.Unit('deg')
    assert isinstance(pos.coord.frame, FK5)
    assert pos.coord.equinox == Time("J1975")

    #   case: cartesian coord in ICRS
    pos = sky_positions[2]
    assert isinstance(pos.coord, SkyCoord)
    assert pos.coord.x == 2.9 * u.Unit('lyr')
    assert pos.coord.y == -3.0 * u.Unit('lyr')
    assert pos.coord.z == -0.1 * u.Unit('lyr')
    assert isinstance(pos.coord.frame, ICRS)
    assert pos.coord.equinox is None

    #   case: chip coordinates - 2D cartesian 
    pos = sky_positions[3]
    assert isinstance(pos.coord, Point)
    assert pos.coord.axis1 == 300.50 * u.Unit('pixel')
    assert pos.coord.axis2 == 500.00 * u.Unit('pixel')
    assert pos.coord.axis3 is None
    assert pos.coord.coord_sys.frame.ref_position.position == "TOPOCENTER"

    # template instsances:
    pos = sky_positions[4]
    assert isinstance(pos.coord, SkyCoord)
    assert pos.coord.ra[0]  == 10.0 * u.Unit('deg')
    assert pos.coord.dec[0] == 11.0 * u.Unit('deg')
    assert pos.coord.ra[1]  == 20.0 * u.Unit('deg')
    assert pos.coord.dec[1] == 21.0 * u.Unit('deg')
    assert isinstance(pos.coord.frame, FK5)
    assert pos.coord.equinox == Time("J1975")


def test_time_adapter_ISO(times_file, recwarn):
    """
    Test Adapters to AstroPy classes.
       o coords:TimeInstant types -> Time

    Check in context of GLOBALS/scalar and TEMPLATES/column
    """
    # ISOTime instances
    times = times_file.find_instances(ISOTime)
    assert len(times) == 2

    #  - GLOBAL/scalar
    time = times[0]
    assert isinstance(time, Time)
    assert time.scale == "tt"
    assert time == "2000-09-02T01:10:14"

    #  - TEMPLATE/array
    time = times[1]
    assert isinstance(time, Time)
    expected_time = Time(["2000-09-02T08:15:00", "9999-12-31T23:59:59"], format='fits', scale='tt')
    assert_array_equal(time, expected_time)
    
    assert len(recwarn) == 1
    assert "_col_H_TIME" in str(recwarn[0].message ) # masked Quantity not supported

def test_time_adapter_MJD(times_file, recwarn):
    """
    Test Adapters to AstroPy classes.
       o coords:TimeInstant types -> Time

    Check in context of GLOBALS/scalar and TEMPLATES/column
    """
    # Verify all MJD instances have been converted
    times = times_file.find_instances(MJD)
    assert len(times) == 2

    #  - GLOBAL/scalar
    time = times[0]
    assert isinstance(time, Time)
    assert time.scale == "tt"
    assert time.mjd == 50814.02
    
    #  - TEMPLATE/array
    time = times[1]
    assert isinstance(time, Time)
    expected_time = Time([53486.5, 0.0], format='mjd', scale='tt')
    assert_array_equal(time, expected_time)
    
    assert len(recwarn) == 1
    assert "_col_H_TIME" in str(recwarn[0].message ) # masked Quantity not supported

def test_time_adapter_JD(times_file, recwarn):
    """
    Test Adapters to AstroPy classes.
       o coords:TimeInstant types -> Time

    Check in context of GLOBALS/scalar and TEMPLATES/column
    """
    # Verify all JD instances have been converted
    times = times_file.find_instances(JD)
    assert len(times) == 2

    #  - GLOBAL/scalar
    time = times[0]
    assert isinstance(time, Time)
    assert time == Time(2453456.5, format='jd', scale='tt')

    #  - TEMPLATE/array
    time = times[1]
    assert isinstance(time, Time)
    expected_time = Time([2453486.5, 0.0] * u.Unit('d'), format='jd', scale='tt')
    assert_array_equal(time, expected_time)
    
    assert len(recwarn) == 1
    assert "_col_H_TIME" in str(recwarn[0].message ) # masked Quantity not supported

