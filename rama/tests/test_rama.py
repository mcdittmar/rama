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
# Test routines for high level rama methods
# ----------------------------------------------------------------------------------------------------

import pytest

from rama import read, is_template, count, unroll
from rama.models.test.sample import Source, SkyCoordinate, CircleError
from astropy.units import Quantity


@pytest.fixture
def sample_file(make_data_path):
    return read(make_data_path('sample.vot.xml'))

def test_read_bad_format(recwarn):
    """
    Tests read() with unsupported format
    """
    try:
        read('sample.vot.xml', 'fits')
    except AttributeError as ex:
        assert "No such format" in str(ex)
        pass

    assert len(recwarn) == 0

def test_read_file_dne(recwarn):
    """
    Tests read() with non-existing file
    """
    try:
        read('sample.vot.xml', 'votable')
    except OSError as ex:
        assert "Error reading file" in str(ex)
        pass

    assert len(recwarn) == 0

def test_is_template( sample_file, recwarn):
    """
    Tests parser.py::is_template()
    """
    gavo = sample_file

    sources = gavo.find_instances(Source)
    assert len(sources) == 2

    # Check instance types -- method output depends on type
    #   Only VO-Objects can be tagged as templates
    assert isinstance( sources[0], Source )                       # VO Instance
    assert isinstance( sources[0].position, SkyCoordinate )       # VO Instance
    assert isinstance( sources[0].position_error, CircleError )   # VO Instance
    assert isinstance( sources[0].position.longitude, Quantity )  # Astropy Quantity
    assert isinstance( sources[0].position.latitude,  Quantity )  # Astropy Quantity

    # GLOBAL position
    assert not is_template(sources[0].position)
    assert not is_template(sources[0].position_error)
    assert not is_template(sources[0].position.longitude)
    assert not is_template(sources[0].position.latitude)
    assert not is_template(sources[0].position.latitude)
    assert not is_template(sources[0].position_error.radius)

    # TEMPLATE position
    assert is_template(sources[1].position)
    assert is_template(sources[1].position_error)
    assert not is_template(sources[1].position.longitude)
    assert not is_template(sources[1].position.latitude)
    assert not is_template(sources[1].position.latitude)
    assert not is_template(sources[1].position_error.radius)
    
    # Something totally not in Models: Reader class
    assert not is_template(gavo)

    assert len(recwarn) == 0


def test_count( sample_file, recwarn):
    """
    Tests parser.py::count()
    """
    gavo = sample_file

    sources = gavo.find_instances(Source)
    assert len(sources) == 2

    # Uses same instances as test_is_template() test

    # Acting on GLOBAL instance
    assert count(sources[0].position) == 0
    assert count(sources[0].position_error) == 0
    
    # Acting on TEMPLATE instance (table has 3 rows)
    assert count(sources[1].position) == 3

    # Acting on non-VO Object
    try:
        assert count(gavo) == 0
    except ValueError as ex:
        assert "Instance is not an adapter or a data model type" in str(ex)
        pass
        
    assert len(recwarn) == 0


def test_unroll( sample_file, recwarn):
    """
    Tests parser.py::unroll()
    """
    gavo = sample_file

    sources = gavo.find_instances(Source)
    assert len(sources) == 2

    # Uses same instances as test_is_template() test

    # Acting on GLOBAL instance
    assert unroll(sources[0].position) == []
    assert unroll(sources[0].position_error) == []
    
    # Acting on TEMPLATE instance (table has 3 rows)
    #  * method unpacks it into array of separate instances
    assert isinstance(sources[1].position, SkyCoordinate)
    positions = unroll(sources[1].position)
    assert len(positions) == 3
    assert isinstance(positions[0], SkyCoordinate)
    assert isinstance(positions[1], SkyCoordinate)
    assert isinstance(positions[2], SkyCoordinate)
    
    # Acting on non-VO Object
    try:
        assert unroll(gavo) == 0
    except ValueError as ex:
        assert "Instance is not an adapter or a data model type" in str(ex)
        pass
        
    assert len(recwarn) == 0
    
