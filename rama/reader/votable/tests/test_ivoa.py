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
#  Test code for the interpretation of IVOA model
# ----------------------------------------------------------------------
import numpy
import pytest

from astropy import units as u

from rama.models.test.sample import BaseTypeElements
from rama import read


@pytest.fixture
def example_file(make_data_path):
    return read(make_data_path('ivoa.vot.xml'))

# ----------------------------------------------------------------------

def test_ivoa_literals( example_file ):
    """
     Test parsing of LITERAL elements using
      - test object added to Sample model containing
        * ATTRIBUTE in each IVOA Base type, expressed as a LITERAL
    """

    # Find instance of test element
    objs = example_file.find_instances( BaseTypeElements )
    assert len(objs) == 2

    item = objs[0]  # Instance annotated as LITERALs
    assert item.sval == "blah"                               # ivoa:string
    assert item.unit == u.Unit("km/s")                       # ivoa:Unit
    assert item.link == "https://www.ivoa.net/bogus.html"    # ivoa:anyURI
    assert item.qval == True                                 # ivoa:boolean
    assert item.tval.isoformat() == '2020-01-02T12:34:56'    # ivoa:datetime
    assert item.ival == -1234                                # ivoa:integer
    assert item.wval == 1234                                 # ivoa:nonnegativeInteger
    assert item.rval == 3.14                                 # ivoa:real
    assert item.iqty.value == 72                             # ivoa:IntegerQuantity
    assert item.iqty.unit  == "C"
    assert item.rqty.value == 15.3                           # ivoa:RealQuantity
    assert item.rqty.unit == "kg"

def test_ivoa_constants( example_file ):
    """
     Test parsing of CONSTANT elements using
      - test object added to Sample model containing
        * ATTRIBUTE in each IVOA Base type, expressed as a CONSTANT
    """

    # Find instance of test element
    objs = example_file.find_instances( BaseTypeElements )
    assert len(objs) == 2

    item = objs[1]  # Instance annotated as CONSTANTs
    assert item.sval == "blah"                               # ivoa:string
    assert item.unit == u.Unit("km/s")                       # ivoa:Unit
    assert item.link == "https://www.ivoa.net/bogus.html"    # ivoa:anyURI
    assert item.qval == True                                 # ivoa:boolean
    assert item.tval.isoformat() == '2020-01-02T12:34:56'    # ivoa:datetime
    assert item.ival == -1234                                # ivoa:integer
    assert item.wval == 1234                                 # ivoa:nonnegativeInteger
    assert item.rval == 3.14                                 # ivoa:real
    assert item.iqty.value == 72                             # ivoa:IntegerQuantity
    assert item.iqty.unit  == "C"
    assert item.rqty.value == 15.3                           # ivoa:RealQuantity
    assert item.rqty.unit == "kg"
    
