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
#  Test code for the parsing/interpretation of vo-dml annotation 
# ----------------------------------------------------------------------
import numpy
import pytest
from astropy import units as u
from astropy.table import MaskedColumn

from rama import read, is_template, unroll
from rama.models.test.sample import Source, SkyCoordinate, SkyCoordinateFrame, LuminosityMeasurement, MultiObj

from rama.models.photdmalt import PhotometryFilter
from rama.models.source import Detection

@pytest.fixture
def literals_file(make_data_path):
    return read(make_data_path('literals.vot.xml'))

@pytest.fixture
def constants_file(make_data_path):
    return read(make_data_path('constants.vot.xml'))

@pytest.fixture
def columns_file(make_data_path):
    return read(make_data_path('columns.vot.xml'))

@pytest.fixture
def compositions_file(make_data_path):
    return read(make_data_path('compositions.vot.xml'))

@pytest.fixture
def attributes_file(make_data_path):
    return read(make_data_path('attributes.vot.xml'))

@pytest.fixture
def references_file(make_data_path):
    return read(make_data_path('references.vot.xml'))

@pytest.fixture
def orm_file(make_data_path):
    return read(make_data_path('orm.vot.xml'))

# ----------------------------------------------------------------------
@pytest.fixture
def hsc_data_file(make_data_path):
    return read(make_data_path('hsc.vot.xml'))

# ----------------------------------------------------------------------
def test_parsing_literals( literals_file ):
    """
     Test parsing of LITERAL elements
         <LITERAL dmtype value [unit] >
          <OPTIONMAPPING>
             <OPTION>"string"</OPTION>
             <ENUMLITERAL>"vodml-id"</ENUMLITERAL> or <SEMANTICCONCEPT>
          </OPTIONMAPPING>
        </LITERAL>

    """
    luminosity = literals_file.find_instances( LuminosityMeasurement  )[0]

    # LITERAL with dmtype, value  (ivoa:string)
    assert luminosity.description == "some descriptive text"

    # LITERAL with dmtype, value, unit  (ivoa:RealQuantity)
    assert luminosity.value.value == 15.718
    assert luminosity.value.unit == "mag"
    
    # LITERAL with OPTIONMAPPING
    # MCD NOTE: TODO - enumeration type == 'string'.. OPTIONMAPPING not parsed/interpreted
    assert luminosity.type == "magnitude"
    #assert (luminosity.optionmapping) == 2

    # Check multiplicity handling
    elem = literals_file.find_instances( MultiObj  )[0]
    assert isinstance(elem.a, float)  # multiplicity 1:1 == scalar
    assert elem.a == 100.0
    assert len(elem.b) == 2           # multiplicity 2:2 == array
    assert elem.b == [200.0, 201.0]
    

def test_parsing_constants( constants_file ):
    """
     Test parsing of CONSTANT elements
        <CONSTANT dmtype ref >
          <OPTIONMAPPING>
             <OPTION>"string"</OPTION>
             <ENUMLITERAL>"vodml-id"</ENUMLITERAL> or <SEMANTICCONCEPT>
          </OPTIONMAPPING>
        </CONSTANT>

    """
    luminosity = constants_file.find_instances( LuminosityMeasurement  )[0]
 
    # CONSTANT with dmtype, value  (ivoa:string)
    assert luminosity.description == "some descriptive text"
    
    # CONSTANT with dmtype, value, unit  (ivoa:RealQuantity)
    assert luminosity.value.value == 15.718
    assert luminosity.value.unit == "mag"
    
    ## CONSTANT with OPTIONMAPPING
    ## MCD NOTE: TODO - enumeration type ==> 'string'.. OPTIONMAPPING not parsed/interpreted
    #assert luminosity.type == "magnitude"
    ##assert (luminosity.optionmapping) == 2
    #
    ## Check multiplicity handling
    elems = constants_file.find_instances( MultiObj  )
    elem = elems[0]
    assert isinstance(elem.a, float)  # multiplicity 1:1 == scalar
    assert elem.a == 100.0
    assert len(elem.b) == 2           # multiplicity 2:2 == array
    assert elem.b == [200.0, 201.0]

def test_parsing_columns( columns_file ):
    """
     Test parsing of COLUMN elements
        <COLUMN dmtype ref >
          <OPTIONMAPPING>
             <OPTION>"string"</OPTION>
             <ENUMLITERAL>"vodml-id"</ENUMLITERAL> or <SEMANTICCONCEPT>
          </OPTIONMAPPING>
        </COLUMN>

     The parser pushes the Table rows into value arrays

    """
    luminosity = columns_file.find_instances( LuminosityMeasurement  )[0]

    # COLUMN with dmtype, value  (ivoa:string)
    assert len(luminosity.description) == 2
    assert luminosity.description[0] == "some descriptive text"
    assert luminosity.description[1] == "more descriptive text"

    # COLUMN with dmtype, value, unit  (ivoa:RealQuantity)
    #  - uses astropy Quantity
    #    o luminosity.value    = Quantity with value array length 2 + unit
    #    o luminosity.value[0] = Quantity with first value + unit
    assert len(luminosity.value) == 2
    expected_lum  = numpy.array([15.718, 14.847], dtype='float32') * u.Unit('mag')
    numpy.testing.assert_array_equal( expected_lum, luminosity.value )
    
    # COLUMN with OPTIONMAPPING
    # MCD NOTE: TODO - enumeration type == 'string'.. OPTIONMAPPING not parsed/interpreted
    assert len(luminosity.type) == 2
    assert luminosity.type[0] == "magnitude"
    assert luminosity.type[1] == "magnitude"
    #assert (luminosity.optionmapping) == 2

    # Check multiplicity handling
    #  o values dimension 1 == 'row'
    elem = columns_file.find_instances( MultiObj  )[0]
    assert len(elem.a) == 2
    assert isinstance(elem.a, MaskedColumn)
    assert elem.a.shape == (2,)
    numpy.testing.assert_array_equal( elem.a, MaskedColumn([100.0, 100.1], dtype='float32'))

    # MCD NOTE: TODO - check this, I do not think 'b' should be a List of MaskedColumn
    assert len(elem.b) == 1                     # b is a list of length=1
    assert isinstance(elem.b[0], MaskedColumn)  #   of MaskedColumn
    assert elem.b[0].shape == (2,2)             #   2 rows x 2 values each
    numpy.testing.assert_array_equal( elem.b[0], MaskedColumn([[200.0, 201.0],[200.1,201.1]], dtype='float32'))

    
def test_parsing_attributes( attributes_file ):
    """
    Test parsing of ATTRIBUTE elements 
      <ATTRIBUTE [dmrole] >
        ->(<COLUMN>|<CONSTANT>|<LITERAL>)
        -><INSTANCE>
      </ATTRIBUTE>

    NOTE: This test is for the handling of ATTRIBUTE contents
          at the high level.  Detailed testing of the contained
          elements are covered by other tests.
    """
    sources = attributes_file.find_instances(Source)
    assert len(sources) == 2
    
    # Check ATTRIBUTE with INSTANCE content in GLOBAL context
    #   Soure.position      == SkyCoordinate
    #   Soure.positionError == AlignedEllipse
    source = sources[0]
    assert source.position is not None
    assert source.position_error is not None
    assert not is_template( source.position ) 

    # Check ATTRIBUTE with LITERAL content
    position = source.position
    assert position.longitude == 122.992773 * u.Unit("deg")
    assert position.latitude ==   -2.092676 * u.Unit("deg")

    # Check ATTRIBUTE with CONSTANT content
    err = source.position_error
    assert err.long_error == 0.1
    assert err.lat_error  == 0.2

    # Check ATTRIBUTE with COLUMN content in TEMPLATE context
    expected_lon = numpy.array([122.99277, 122.986794, 123.033734], dtype='float64') * u.Unit('deg')
    expected_lat = numpy.array([ -2.092676,  -2.095231,  -2.103671], dtype='float64') * u.Unit('deg')
    source = sources[1]
    assert source.position is not None
    assert is_template( source.position ) 
    assert len(source.position.longitude) == 3
    assert len(source.position.latitude)  == 3
    assert source.position.longitude[0] == expected_lon[0]
    assert source.position.longitude[1] == expected_lon[1]
    assert source.position.longitude[2] == expected_lon[2]
    assert source.position.latitude[0]  == expected_lat[0]
    assert source.position.latitude[1]  == expected_lat[1]
    assert source.position.latitude[2]  == expected_lat[2]
    
    
def test_parsing_compositions( compositions_file ):
    """
    Test parsing of COMPOSITION elements
      <COMPOSITION>
         <INSTANCE>
         <EXTINSTANCES>
      </COMPOSITON
    """    
    sources = compositions_file.find_instances(Source)
    assert len(sources) == 1

    # Each source record has luminosities in multiple bands
    #   o each is a separate instance of LuminosityMeasure
    source = sources[0]
    assert len(source.luminosity) == 2
    assert source.luminosity[0].type == "magnitude"
    assert source.luminosity[0].value == 15.718 * u.Unit("mag")
    assert source.luminosity[1].type == "flux"
    assert source.luminosity[1].value == 7.3201E-17 * u.Unit("J/(m2 s)")

    # MCD NOTE: TODO - EXTINSTANCES not tested


def test_references_are_same_object(references_file):
    """
    Test handling of REFERENCEs:
      all references to an object should be the same
    """
    sky = references_file.find_instances( SkyCoordinate )
    assert len(sky) == 2

    # have 2 SkyCoordinate instances referencing the same frame
    assert sky[0].frame is sky[1].frame

    
def test_referred_built_only_once(references_file):
    """
    Test handling of REFERENCEs:
      referred object should only be built once.
    """
    frames = references_file.find_instances(SkyCoordinateFrame)
    sky    = references_file.find_instances(SkyCoordinate)

    assert len(sky) == 2
    assert len(frames) == 1
    assert sky[0].frame is frames[0]
    assert sky[1].frame is frames[0]

def test_references_context(references_file):
    """
    Test handling of REFERENCEs within GLOBAL and TEMPLATE
      o Elements in GLOBAL and TEMPLATE
        - reference element in GLOBAL
    """
    sky = references_file.find_instances( SkyCoordinate )
    assert len(sky) == 2

    assert not is_template( sky[0] )
    assert not is_template( sky[0].frame )
    assert is_template( sky[1] )
    assert not is_template( sky[1].frame )

    
def test_reference_target_missing(references_file, recwarn):
    """
    Test handling of missing reference target.
    """
    elem = references_file.find_instances(LuminosityMeasurement)[0]

    assert "Dangling reference" in str(recwarn[0].message)

def test_invalid_refid(references_file):
    """
    Test handling of invalid ref=<tag> syntax
      - get warning for invalid syntax
      - element generated with NaN values

    NOTE: creates column with NaN values regardless of spec'd 
          column type (eg: ivoa:string)
    """
    with pytest.warns(SyntaxWarning) as record:
        sources = references_file.find_instances(Source)
        assert "ID foo" in str(record[-1].message)

    source = sources[0]

    assert 1 == len(sources)
    expected_name  = numpy.array([numpy.NaN, numpy.NaN])
    expected_class = numpy.array(['star', 'star', 'star'], dtype='|S4')
    numpy.testing.assert_array_equal(expected_name,  source.name)
    numpy.testing.assert_array_equal(expected_class, source.classification)


def test_references_orm(orm_file, recwarn):
    sources = orm_file.find_instances(Source)
    filters = orm_file.find_instances(PhotometryFilter)

    f814w = None
    f606w = None

    for hsc_filter in filters:
        if hsc_filter.name == "F814W":
            f814w = hsc_filter
        else:
            f606w = hsc_filter

    source = sources[0]
    assert source.luminosity[0].filter[0] is f606w
    assert source.luminosity[0].filter[1] is f814w


def test_references_orm_unroll(orm_file, recwarn):
    sources = orm_file.find_instances(Source)
    filters = orm_file.find_instances(PhotometryFilter)

    f814w = None
    f606w = None

    for hsc_filter in filters:
        if hsc_filter.name == "F814W":
            f814w = hsc_filter
        else:
            f606w = hsc_filter

    source = unroll(sources[0])
    assert source[0].luminosity[0].filter is f606w
    assert source[1].luminosity[0].filter is f814w


def test_references_orm_hsc(hsc_data_file, recwarn):
    sources = hsc_data_file.find_instances(Detection)
    filters = hsc_data_file.find_instances(PhotometryFilter)

    f814w = None
    f606w = None

    for hsc_filter in filters:
        if hsc_filter.name == "F814W":
            f814w = hsc_filter
        else:
            f606w = hsc_filter

    source = sources[0]
    assert source.luminosity[0].filter[0] is f814w
    assert source.luminosity[0].filter[1] is f606w
    assert source.luminosity[0].filter[2] is f606w
    assert source.luminosity[0].filter[3] is f606w
    assert source.luminosity[0].filter[4] is f606w
    assert source.luminosity[0].filter[5] is f606w
    assert source.luminosity[0].filter[6] is f606w


def test_references_orm_unroll_hsc(hsc_data_file, recwarn):
    sources = hsc_data_file.find_instances(Detection)
    filters = hsc_data_file.find_instances(PhotometryFilter)

    f814w = None
    f606w = None

    for hsc_filter in filters:
        if hsc_filter.name == "F814W":
            f814w = hsc_filter
        else:
            f606w = hsc_filter

    assert sources[0].cardinality == 7

    source = unroll(sources[0])
    assert source[0].luminosity[0].filter is f814w
    assert source[1].luminosity[0].filter is f606w
    assert source[2].luminosity[0].filter is f606w
    assert source[3].luminosity[0].filter is f606w
    assert source[4].luminosity[0].filter is f606w
    assert source[5].luminosity[0].filter is f606w
    assert source[6].luminosity[0].filter is f606w


def test_polymorphism(hsc_data_file, recwarn):
    # There is no explicit instantiation of Source in the hsc file, but there is and instantiation of Detection,
    # which is a subtype of Source.
    from rama.models.source import Source
    sources = hsc_data_file.find_instances(Source)

    assert sources[0].cardinality == 7
    assert isinstance(sources[0], Detection)
    assert isinstance(sources[0], Source)
