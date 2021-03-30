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
import pytest
from astropy.table import MaskedColumn
from astropy import units as u
from numpy.testing import assert_array_equal

from rama import is_template, count, unroll
from rama.models.test.filter import PhotometryFilter
from rama.models.test.sample import SkyCoordinateFrame, Source, SkyCoordinate, LuminosityMeasurement
from rama.reader import Reader
from rama.reader.votable import Votable

import sys

@pytest.fixture
def context_test5(make_data_path):
    return Reader(Votable(make_data_path("test5.vot.xml")))


def test_coordinate_frame(context_test5):
    frames = context_test5.find_instances(SkyCoordinateFrame)

    assert len(frames) == 1
    assert frames[0].name == "ICRS"


def test_filters(context_test5):
    filters = context_test5.find_instances(PhotometryFilter)

    assert len(filters) == 5
    assert filters[0].name == "2mass:H"
    assert filters[1].name == "2mass:J"
    assert filters[2].name == "2mass:K"
    assert filters[3].name == "sdss:g"
    assert filters[4].name == "sdss:r"


def test_source(context_test5, recwarn):
    sources = context_test5.find_instances(Source)

    assert len(sources) == 1
    source = sources[0]
    # assert_array_equal(source.id, [b'08120809-0206132', b'08115683-0205428', b'08115826-0205336'])
    # assert_array_equal(source.name, [b'08120809-0206132', b'08115683-0205428', b'08115826-0205336'])
    assert_array_equal(source.position.longitude, MaskedColumn([123.033734, 122.986794, 122.992773],
                                                               dtype='float32', unit='deg'))
    assert_array_equal(source.position.latitude, MaskedColumn([-2.103671, -2.095231, -2.092676],
                                                              dtype='float32', unit='deg'))

    frame = context_test5.find_instances(SkyCoordinateFrame)[0]
    filters = context_test5.find_instances(PhotometryFilter)
    h_filter = filters[0]
    j_filter = filters[1]
    k_filter = filters[2]
    g_filter = filters[3]

    assert source.position.frame is frame

    assert len(source.luminosity) == 5

    h_mag = source.luminosity[0]
    assert h_mag.type == 'magnitude'
    assert h_mag.filter is h_filter
    assert_array_equal(h_mag.value, MaskedColumn([13.681, 15.103, 15.718],
                                                 dtype='float32', unit='mag'))
    assert_array_equal(h_mag.error, MaskedColumn([0.027, 0.077, 0.112],
                                                 dtype='float32', unit='mag'))
    j_mag = source.luminosity[1]
    assert j_mag.type == 'magnitude'
    assert j_mag.filter is j_filter
    assert_array_equal(j_mag.value, MaskedColumn([14.161, 15.86, 16.273],
                                                 dtype='float32', unit='mag'))
    assert_array_equal(j_mag.error, MaskedColumn([0.025, 0.06, 0.096],
                                                 dtype='float32', unit='mag'))

    k_mag = source.luminosity[2]
    assert k_mag.type == 'magnitude'
    assert k_mag.filter is k_filter
    assert_array_equal(k_mag.value, MaskedColumn([13.675, 14.847, 15.46],
                                                 dtype='float32', unit='mag'))
    assert_array_equal(k_mag.error, MaskedColumn([0.048, 0.127, 0.212],
                                                 dtype='float32', unit='mag'))

    #Gmag is coming from external instances.. expect a List (one per source)
    assert len(source.luminosity[3]) == 3 

    g_mag = source.luminosity[3][0]
    assert g_mag.type == 'magnitude'
    #assert g_mag.filter is g_filter  ### TODO!!!
    assert len(g_mag.value.data) == 1 
    assert_array_equal(g_mag.value, MaskedColumn([23.2], dtype='float32', unit='mag'))
    assert_array_equal(g_mag.error, MaskedColumn([0.04], dtype='float32', unit='mag'))

    g_mag = source.luminosity[3][1]
    assert g_mag is None  # No external magnitude for this source id.

    g_mag = source.luminosity[3][2]
    assert g_mag.type == 'magnitude'
    #assert g_mag.filter is g_filter  ### TODO!!!
    assert len(g_mag.value.data) == 1 
    assert_array_equal(g_mag.value, MaskedColumn([20.0], dtype='float32', unit='mag'))
    assert_array_equal(g_mag.error, MaskedColumn([0.05], dtype='float32', unit='mag'))


    #one Source_id has 2 matches in MAGS table, 
    assert len(source.luminosity[4]) == 3 

    g_mag = source.luminosity[4][0]
    assert g_mag is None
    g_mag = source.luminosity[4][1]
    assert g_mag is None
    g_mag = source.luminosity[4][2]
    assert g_mag.type == 'magnitude'
    #assert g_mag.filter is g_filter  ### TODO!!!
    assert len(g_mag.value.data) == 1 
    assert_array_equal(g_mag.value, MaskedColumn([20.1], dtype='float32', unit='mag'))
    assert_array_equal(g_mag.error, MaskedColumn([0.05], dtype='float32', unit='mag'))

    
    assert len(recwarn) == 0
    
    #assert "W20" in str(recwarn[0].message)
    #assert "W41" in str(recwarn[1].message)
    #for i in range(2, 12):
    #    assert "W10" in str(recwarn[i].message)

    # TODO MISSING multi-table relationship


def test_source_unroll(context_test5, recwarn):

    # Frame instance
    # - is a GLOBALS instance, only have 1 spec'd
    #   - is singular, cardinality = 0
    frame = context_test5.find_instances(SkyCoordinateFrame)[0]
    t = frame.unroll()
    assert len(t) == 0   # <== t = []

    # PhotometryFilters
    # - is a GLOBALS instance, have 3 spec'd
    # - find returns [filter,filter,filter]
    #   - each filter is singular, cardinality = 0
    filters = context_test5.find_instances(PhotometryFilter)
    h_filter = filters[0]
    j_filter = filters[1]
    k_filter = filters[2]

    t = h_filter.unroll()
    assert len(t) == 0   # <== t = []

    # SkyCoordinate
    # - is a TEMPLATE instance, have 1 spec'd with 3 rows in table.
    pos = context_test5.find_instances(SkyCoordinate)
    assert len(pos) == 1
    assert len(pos[0].longitude) == 3

    t = pos[0].unroll()  # <== t = [SkyCoordinate, SkyCoordinate, SkyCoordinate]
    assert len(t) == 3
    for n in range(len(t)):
        assert t[n].longitude == pos[0].longitude[n]
        assert t[n].latitude == pos[0].latitude[n]
        assert t[n].frame is frame
    
    # LuminosityMeasurement
    # - This just gets ALL LuminosityMeasurement instances
    # - is a TEMPLATE instance, have 3 spec'd with 3 rows each
    #                           PLUS some from EXTINSTANCES (second table)
    # - end up with 4 instances, Quantity with 3 rows in first 3
    #                            MaskedColumn with 6 rows in 4th (no units)
    lum = context_test5.find_instances(LuminosityMeasurement)
    assert len(lum) == 4
    assert len(lum[0].value) == 3
    assert len(lum[1].value) == 3
    assert len(lum[2].value) == 3
    assert len(lum[3].value) == 6

    for ii in range(len(lum)):
        t = lum[ii].unroll()
        assert len(t) == 3 if ii < 2 else 6
        for n in range(len(t)):
            assert t[n].type  == lum[ii].type      # singular.. not type[n]
            assert t[n].value == lum[ii].value[n]  # Quantity w/ n values
            assert t[n].error == lum[ii].error[n]  # Quantity w/ n values
            if ii < 3:
                assert t[n].filter is filters[ii]  # ref to filter is still reference
            else:
                assert t[n].filter is None

    # ================================================================================
    # So the atomic level seems to be OK.
    # Next unroll Source: fully within TEMPLATES, contains the above
    template_source = context_test5.find_instances(Source)[0]
    assert is_template(template_source)
    assert template_source.cardinality == 3  #<== check the no. of instances from TEMPLATE

    # unroll it
    #sources = unroll(template_source)
    sources = template_source.unroll()

    assert len(sources) == 3
    assert len(sources[0].luminosity) == 5  # 3 local + 2 external instances

    for n in range(len(sources)):
        #assert sources[n].name == '08120809-0206132'
        assert sources[n].name == template_source.name[n]
        assert sources[n].position.longitude == template_source.position.longitude[n]
        assert sources[n].position.latitude == template_source.position.latitude[n]
        assert sources[n].position.frame is frame
        h_mag = sources[n].luminosity[0]
        assert h_mag.type == 'magnitude'
        assert h_mag.filter is h_filter
        assert h_mag.value == template_source.luminosity[0].value[n]
        assert h_mag.error == template_source.luminosity[0].error[n]
        #
        j_mag = sources[n].luminosity[1]
        assert j_mag.type == 'magnitude'
        assert j_mag.filter is j_filter
        assert j_mag.value == template_source.luminosity[1].value[n]
        assert j_mag.error == template_source.luminosity[1].error[n]
        #
        k_mag = sources[n].luminosity[2]
        assert k_mag.type == 'magnitude'
        assert k_mag.filter is k_filter
        assert k_mag.value == template_source.luminosity[2].value[n]
        assert k_mag.error == template_source.luminosity[2].error[n]

        # external instances, may be None; organized differently in packed representation
        g_mag = sources[n].luminosity[3]
        if n == 1:
            assert g_mag is None
            assert g_mag == template_source.luminosity[3][n]
        else:
            assert g_mag.type == 'magnitude'
            assert g_mag.filter is None
            assert g_mag.value == template_source.luminosity[3][n].value
            assert g_mag.error == template_source.luminosity[3][n].error

        g_mag = sources[n].luminosity[4]
        if n != 2:
            assert g_mag is None
            assert g_mag == template_source.luminosity[4][n]
        else:
            assert g_mag.type == 'magnitude'
            assert g_mag.filter is None
            assert g_mag.value == template_source.luminosity[4][n].value
            assert g_mag.error == template_source.luminosity[4][n].error
            
        
#    assert sources is None
    
