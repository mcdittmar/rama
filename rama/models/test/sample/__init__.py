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
    long_error = Attribute('longError', min_occurs=1, max_occurs=1)
    lat_error = Attribute('latError', min_occurs=1, max_occurs=1)


@VO('sample:catalog.CircleError')
class CircleError(SkyError):
    radius = Attribute('radius', min_occurs=1, max_occurs=1)


@VO('sample:catalog.GenericEllipse')
class GenericEllipse(SkyError):
    major = Attribute('major', min_occurs=1, max_occurs=1)
    min_occursor = Attribute('min_occursor', min_occurs=1, max_occurs=1)
    pa = Attribute('pa', min_occurs=0, max_occurs=-1)


@VO('sample:catalog.SkyCoordinate')
class SkyCoordinate(BaseType):
    longitude = Attribute('longitude', min_occurs=1, max_occurs=1)
    latitude = Attribute('latitude', min_occurs=1, max_occurs=1)
    frame = Reference('frame', min_occurs=1, max_occurs=1)


@VO('sample:catalog.AstroObject')
class AstroObject(BaseType):
    label = Attribute('label', min_occurs=0, max_occurs=1)


@VO('sample:catalog.AbstractSource')
class AbstractSource(AstroObject):
    name = Attribute('name', min_occurs=1, max_occurs=1)
    description = Attribute('description', min_occurs=0, max_occurs=1)
    position = Attribute('position', min_occurs=1, max_occurs=1)
    position_error = Attribute('positionError', min_occurs=0, max_occurs=1)
    classification = Attribute('classification', min_occurs=1, max_occurs=1)
    luminosity = Composition('luminosity', min_occurs=0, max_occurs=-1)


@VO('sample:catalog.LuminosityMeasurement')
class LuminosityMeasurement(BaseType):
    value = Attribute('value', min_occurs=1, max_occurs=1)
    error = Attribute('error', min_occurs=0, max_occurs=1)
    description = Attribute('description', min_occurs=0, max_occurs=1)
    type = Attribute('type', min_occurs=1, max_occurs=1)
    filter = Reference('filter', min_occurs=1, max_occurs=1)


@VO('sample:catalog.SDSSSource')
class SDSSSource(AbstractSource):
    pass


@VO('sample:catalog.SkyCoordinateFrame')
class SkyCoordinateFrame(BaseType):
    name = Attribute('name', min_occurs=1, max_occurs=1)
    document_u_r_i = Attribute('documentURI', min_occurs=1, max_occurs=1)
    equinox = Attribute('equinox', min_occurs=0, max_occurs=1)
    system = Attribute('system', min_occurs=0, max_occurs=1)


@VO('sample:catalog.Source')
class Source(AbstractSource):
    pass


@VO('sample:catalog.TwoMassSource')
class TwoMassSource(AbstractSource):
    pass
