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
# ----------------------------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------------------------
# Test routines for reading/instantiating TimeSeries instance from VOTable
#   * TimeSeries is currently supported as a class which interprets a Cube instance as Time Series
# ----------------------------------------------------------------------------------------------------
import pytest

from astropy import units as u
from unittest import mock

import numpy as np
from numpy.testing import assert_array_equal

from rama import read

from rama.tools.timeseries import TimeSeries
from rama.adapters.cube import CubePoint
from rama.models.cube import NDPoint
from rama.models.measurements import Time, GenericMeasure


class TimeAxisStub:
    def __init__(self):
        self.dependent = False
        coord = np.array([1, 2, 3]) * u.Unit('d')
        coord.name = "foo"
        self.measure = mock.MagicMock(Time, coord=coord)


class FluxAxisStub:
    def __init__(self):
        self.dependent = True
        cval = np.array([10, 20, 30]) * u.Unit('mag')
        cval.name = 'flux'
        coord = mock.MagicMock(cval=cval)
        self.measure = mock.MagicMock(GenericMeasure, coord=coord)


class NdPointStub:
    observable = None
    def __init__(self, axes=None):
        if axes is None:
            self.observable = [TimeAxisStub(), FluxAxisStub()]
        else:
            self.observable = axes
        
@pytest.fixture
def ts_file(make_data_path):
    return read(make_data_path('time-series.vot.xml'))

def test_time_series_unit():
    """
    Time Series Unit Tests
      * Focus testing of Cube->TimeSeries conversion using Mock data
    """
    # Create mock time series instance
    cube_point  = CubePoint(NdPointStub())
    time_series = TimeSeries(cube_point)

    # Test access to TimeSeries axes by either ts.<axis>  or ts['<axis>'] syntax
    #  o TimeAxis named 'foo' recognized/identified as TimeSeries.time
    assert_array_equal(time_series.time.measure, np.array([1, 2, 3]) * u.Unit('d'))
    assert_array_equal(time_series['time'].measure, np.array([1, 2, 3]) * u.Unit('d'))
    assert_array_equal(time_series.dependent[0].measure, np.array([10, 20, 30]) * u.Unit('mag'))
    assert_array_equal(time_series['flux'].measure, np.array([10, 20, 30]) * u.Unit('mag'))

    # Test - no independent axis
    time_axis = TimeAxisStub()
    flux_axis = FluxAxisStub()
    time_axis.dependent = True
    cube_point = CubePoint(NdPointStub([time_axis,flux_axis]))
    try:
        time_series = TimeSeries(cube_point)
        assert time_series is None # FAIL if no error
    except AttributeError as ex:
        assert "there is no independent axis for Time" in str(ex)
        pass

    # Test - independent axis not TimeAxis (eg: Spectrum)
    time_axis.dependent = True
    flux_axis.dependent = False
    cube_point = CubePoint(NdPointStub([time_axis,flux_axis]))
    try:
        time_series = TimeSeries(cube_point)
        assert time_series is None # FAIL if no error
    except AttributeError as ex:
        assert "found independent axis other than Time" in str(ex)
        pass

    # Test - mulitple independent axes, incl. TimeAxis
    #  (Event list may be all dependent or all independent??  not sure.)
    time_axis.dependent = False
    flux_axis.dependent = False
    cube_point = CubePoint(NdPointStub([time_axis,flux_axis]))
    try:
        time_series = TimeSeries(cube_point)
        assert time_series is None # FAIL if no error
    except AttributeError as ex:
        assert "found independent axis other than Time" in str(ex)
        pass

    # Test - mulitple independent Time axes
    time_axis.measure.coord.name = "hjd"
    time_axis.dependent = False
    cube_point = CubePoint(NdPointStub([time_axis,TimeAxisStub()]))
    assert len(cube_point.axes) == 2
    try:
        time_series = TimeSeries(cube_point)
        assert time_series is None # FAIL if no error
    except AttributeError as ex:
        assert "found multiple independent Time axes" in str(ex)
        pass

    
def test_time_series_file(ts_file, recwarn):
    """
    Time Series Test - Full thread
      o Time: Position, Flux, Mag
    """
    cube_point  = ts_file.find_instances(NDPoint)[0]
    time_series = TimeSeries(cube_point)

    assert_array_equal(time_series.time, cube_point['time'])
    assert_array_equal(time_series['time'], cube_point['time'])
    assert_array_equal(time_series.dependent[1], cube_point['flux'])
    assert_array_equal(time_series['flux'], cube_point['flux'])

    assert len(recwarn) == 0
