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
#
#  Auto-generated using Jovial on Sample data model vo-dml/xml 
#
from rama.framework import Attribute, Reference, Composition, BaseType
from rama.models.ivoa import StringQuantity

from rama.utils.registry import VO


@VO('sample:catalog.LuminosityType')
class LuminosityType(StringQuantity):
    pass


@VO('sample:catalog.SourceClassification')
class SourceClassification(StringQuantity):
    pass


@VO('sample:catalog.SkyError')
class SkyError(BaseType):
    pass


@VO('sample:catalog.AlignedEllipse')
class AlignedEllipse(SkyError):
    long_error = Attribute('sample:catalog.AlignedEllipse.longError', min_occurs=1, max_occurs=1)
    lat_error = Attribute('sample:catalog.AlignedEllipse.latError', min_occurs=1, max_occurs=1)


@VO('sample:catalog.CircleError')
class CircleError(SkyError):
    radius = Attribute('sample:catalog.CircleError.radius', min_occurs=1, max_occurs=1)


@VO('sample:catalog.GenericEllipse')
class GenericEllipse(SkyError):
    major = Attribute('sample:catalog.GenericEllipse.major', min_occurs=1, max_occurs=1)
    min_occursor = Attribute('sample:catalog.GenericEllipse.min_occursor', min_occurs=1, max_occurs=1)
    pa = Attribute('sample:catalog.GenericEllipse.pa', min_occurs=0, max_occurs=-1)


@VO('sample:catalog.SkyCoordinate')
class SkyCoordinate(BaseType):
    longitude = Attribute('sample:catalog.SkyCoordinate.longitude', min_occurs=1, max_occurs=1)
    latitude = Attribute('sample:catalog.SkyCoordinate.latitude', min_occurs=1, max_occurs=1)
    frame = Reference('sample:catalog.SkyCoordinate.frame', min_occurs=1, max_occurs=1)


@VO('sample:catalog.AstroObject')
class AstroObject(BaseType):
    label = Attribute('sample:catalog.AstroObject.label', min_occurs=0, max_occurs=1)


@VO('sample:catalog.AbstractSource')
class AbstractSource(AstroObject):
    name = Attribute('sample:catalog.AbstractSource.name', min_occurs=1, max_occurs=1)
    description = Attribute('sample:catalog.AbstractSource.description', min_occurs=0, max_occurs=1)
    position = Attribute('sample:catalog.AbstractSource.position', min_occurs=1, max_occurs=1)
    position_error = Attribute('sample:catalog.AbstractSource.positionError', min_occurs=0, max_occurs=1)
    classification = Attribute('sample:catalog.AbstractSource.classification', min_occurs=1, max_occurs=1)
    luminosity = Composition('sample:catalog.AbstractSource.luminosity', min_occurs=0, max_occurs=-1)


@VO('sample:catalog.LuminosityMeasurement')
class LuminosityMeasurement(BaseType):
    value = Attribute('sample:catalog.LuminosityMeasurement.value', min_occurs=1, max_occurs=1)
    error = Attribute('sample:catalog.LuminosityMeasurement.error', min_occurs=0, max_occurs=1)
    description = Attribute('sample:catalog.LuminosityMeasurement.description', min_occurs=0, max_occurs=1)
    type = Attribute('sample:catalog.LuminosityMeasurement.type', min_occurs=1, max_occurs=1)
    filter = Reference('sample:catalog.LuminosityMeasurement.filter', min_occurs=1, max_occurs=1)


@VO('sample:catalog.SDSSSource')
class SDSSSource(AbstractSource):
    pass


@VO('sample:catalog.SkyCoordinateFrame')
class SkyCoordinateFrame(BaseType):
    """
    Manual adjustment: jovial converts camelcase variables to underscored..
       documentURI => document_u_r_i ==> adjusting to document_uri
    """
    name = Attribute('sample:catalog.SkyCoordinateFrame.name', min_occurs=1, max_occurs=1)
    document_uri = Attribute('sample:catalog.SkyCoordinateFrame.documentURI', min_occurs=1, max_occurs=1)
    equinox = Attribute('sample:catalog.SkyCoordinateFrame.equinox', min_occurs=0, max_occurs=1)
    system = Attribute('sample:catalog.SkyCoordinateFrame.system', min_occurs=0, max_occurs=1)


@VO('sample:catalog.Source')
class Source(AbstractSource):
    pass


@VO('sample:catalog.TwoMassSource')
class TwoMassSource(AbstractSource):
    pass


# --------------------------------------------------------------------------------
# Manual additions
# --------------------------------------------------------------------------------
#
@VO('sample:test.BaseTypeElements')
class BaseTypeElements(BaseType):
    """
    Object with Attributes in each of the base types spec'd in the IVOA model
       sval == ivoa:string
       unit ==    ivoa:Unit
       link ==    ivoa:anyURI
       qval == ivoa:boolean
       tval == ivoa:datetime
       ival == ivoa:integer
       wval == ivoa:nonnegativeInteger
       rval == ivoa:real
       ---- == ivoa:Quantity (Abstract)
       iqty ==   ivoa:IntegerQuantity
       rqty ==   ivoa:RealQuantity

       cplx == ivoa:complex   << TODO
       rtnl == ivoa:rational  << TODO

    """
    sval = Attribute('sample:test.BaseTypeElements.sval', min_occurs=1, max_occurs=1)
    unit = Attribute('sample:test.BaseTypeElements.unit', min_occurs=1, max_occurs=1)
    link = Attribute('sample:test.BaseTypeElements.link', min_occurs=1, max_occurs=1)
    qval = Attribute('sample:test.BaseTypeElements.qval', min_occurs=1, max_occurs=1)
    tval = Attribute('sample:test.BaseTypeElements.tval', min_occurs=1, max_occurs=1)
    ival = Attribute('sample:test.BaseTypeElements.ival', min_occurs=1, max_occurs=1)
    wval = Attribute('sample:test.BaseTypeElements.wval', min_occurs=1, max_occurs=1)
    rval = Attribute('sample:test.BaseTypeElements.rval', min_occurs=1, max_occurs=1)
    iqty = Attribute('sample:test.BaseTypeElements.iqty', min_occurs=1, max_occurs=1)
    rqty = Attribute('sample:test.BaseTypeElements.rqty', min_occurs=1, max_occurs=1)


@VO('sample:test.MultiObj')
class MultiObj(BaseType):
    """
    Object with Attributes with various multiplicities

    """
    a = Attribute('sample:test.MultiObj.a', min_occurs=1, max_occurs=1)
    b = Attribute('sample:test.MultiObj.b', min_occurs=2, max_occurs=2)
