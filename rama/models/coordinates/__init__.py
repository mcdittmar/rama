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
from rama.adapters.astropy import SkyCoordAdapter, TimeAdapter
from rama.framework import Attribute, Reference, Composition, BaseType
from rama.models.ivoa import StringQuantity
from rama.utils import Adapter
from rama.utils.registry import VO


@VO('coords:domain.space.Epoch')
class Epoch(StringQuantity):
    pass


@VO('coords:Handedness')
class Handedness(StringQuantity):
    pass


@VO('coords:Coordinate')
class Coordinate(BaseType):
    frame = Reference('frame', min_occurs=0, max_occurs=1)


@VO('coords:CoordValue')
class CoordValue(Coordinate):
    axis = Reference('axis', min_occurs=1, max_occurs=1)


@VO('coords:CompositeCoordinate')
class CompositeCoordinate(Coordinate):
    cmpt = Attribute('cmpt', min_occurs=1, max_occurs=-1)


@VO('coords:PhysicalCoordValue')
class PhysicalCoordValue(CoordValue):
    cval = Attribute('cval', min_occurs=1, max_occurs=1)


@VO('coords:BinnedCoordValue')
class BinnedCoordValue(CoordValue):
    cval = Attribute('cval', min_occurs=1, max_occurs=1)


@VO('coords:CompositeCoord1D')
class CompositeCoord1D(CompositeCoordinate):
    pass


@VO('coords:CompositeCoord2D')
class CompositeCoord2D(CompositeCoordinate):
    pass


@VO('coords:CompositeCoord3D')
class CompositeCoord3D(CompositeCoordinate):
    pass


@VO('coords:CoordFrame')
class CoordFrame(BaseType):
    pass


@VO('coords:CoordSys')
class CoordSys(BaseType):
    pass


@VO('coords:AstroCoordSystem')
class AstroCoordSystem(CoordSys):
    coord_frame = Reference('coordFrame', min_occurs=0, max_occurs=-1)


@VO('coords:CoordSpace')
class CoordSpace(BaseType):
    axis = Composition('axis', min_occurs=1, max_occurs=-1)


@VO('coords:Axis')
class Axis(BaseType):
    name = Attribute('name', min_occurs=0, max_occurs=1)


@VO('coords:ContinuousAxis')
class ContinuousAxis(Axis):
    domain_min = Attribute('domainMin', min_occurs=0, max_occurs=1)
    domain_max = Attribute('domainMax', min_occurs=0, max_occurs=1)
    cyclic = Attribute('cyclic', min_occurs=0, max_occurs=1)


@VO('coords:BinnedAxis')
class BinnedAxis(Axis):
    length = Attribute('length', min_occurs=1, max_occurs=1)


@VO('coords:DiscreteSetAxis')
class DiscreteSetAxis(Axis):
    pass


@VO('coords:GenericCoordFrame')
class GenericCoordFrame(CoordFrame):
    ref_position = Attribute('refPosition', min_occurs=1, max_occurs=1)
    planetary_ephem = Attribute('planetaryEphem', min_occurs=0, max_occurs=1)


@VO('coords:domain.pixel.PixelIndex')
class PixelIndex(BinnedCoordValue):
    pass


@VO('coords:domain.pixel.PixelCoordSystem')
class PixelCoordSystem(CoordSys):
    pixel_space = Composition('pixelSpace', min_occurs=1, max_occurs=1)


@VO('coords:domain.pixel.PixelSpace')
class PixelSpace(CoordSpace):
    handedness = Attribute('handedness', min_occurs=0, max_occurs=1)


@VO('coords:domain.space.StdRefPosition')
class StdRefPosition(StringQuantity):
    pass


@VO('coords:domain.space.StdRefFrame')
class StdRefFrame(StringQuantity):
    pass


@VO('coords:domain.space.RefLocation')
class RefLocation(BaseType):
    pass


@VO('coords:domain.space.StdRefLocation')
class StdRefLocation(RefLocation):
    position = Attribute('position', min_occurs=1, max_occurs=1)


@VO('coords:domain.space.CustomRefLocation')
class CustomRefLocation(RefLocation):
    epoch = Attribute('epoch', min_occurs=0, max_occurs=1)
    position = Attribute('position', min_occurs=1, max_occurs=1)
    velocity = Attribute('velocity', min_occurs=0, max_occurs=1)


@VO('coords:domain.space.SpaceCoord')
@Adapter(SkyCoordAdapter)
class SpaceCoord(Coordinate):
    pass


@VO('coords:domain.space.EquatorialCoord')
class EquatorialCoord(SpaceCoord):
    ra = Attribute('ra', min_occurs=0, max_occurs=1)
    dec = Attribute('dec', min_occurs=0, max_occurs=1)
    r = Attribute('r', min_occurs=0, max_occurs=1)


@VO('coords:domain.space.CartesianCoord')
class CartesianCoord(SpaceCoord):
    x = Attribute('x', min_occurs=0, max_occurs=1)
    y = Attribute('y', min_occurs=0, max_occurs=1)
    z = Attribute('z', min_occurs=0, max_occurs=1)


@VO('coords:domain.space.LongLatCoord')
class LongLatCoord(SpaceCoord):
    long = Attribute('long', min_occurs=0, max_occurs=1)
    lat = Attribute('lat', min_occurs=0, max_occurs=1)
    r = Attribute('r', min_occurs=0, max_occurs=1)


@VO('coords:domain.space.GalacticCoord')
class GalacticCoord(SpaceCoord):
    l = Attribute('l', min_occurs=0, max_occurs=1)
    b = Attribute('b', min_occurs=0, max_occurs=1)
    r = Attribute('r', min_occurs=0, max_occurs=1)


@VO('coords:domain.space.EclipticCoord')
class EclipticCoord(SpaceCoord):
    elong = Attribute('elong', min_occurs=0, max_occurs=1)
    elat = Attribute('elat', min_occurs=0, max_occurs=1)
    r = Attribute('r', min_occurs=0, max_occurs=1)


@VO('coords:domain.space.SpaceFrame')
class SpaceFrame(CoordFrame):
    ref_position = Attribute('refPosition', min_occurs=1, max_occurs=1)
    space_ref_frame = Attribute('spaceRefFrame', min_occurs=1, max_occurs=1)
    equinox = Attribute('equinox', min_occurs=0, max_occurs=1)
    planetary_ephem = Attribute('planetaryEphem', min_occurs=1, max_occurs=1)


@VO('coords:domain.time.TimeScale')
class TimeScale(StringQuantity):
    pass


@VO('coords:domain.time.TimeStamp')
@Adapter(TimeAdapter)
class TimeStamp(Coordinate):
    pass


@VO('coords:domain.time.TimeInstant')
class TimeInstant(TimeStamp):
    pass


@VO('coords:domain.time.ISOTime')
class ISOTime(TimeInstant):
    date = Attribute('date', min_occurs=1, max_occurs=1)


@VO('coords:domain.time.JD')
class JD(TimeInstant):
    date = Attribute('date', min_occurs=1, max_occurs=1)


@VO('coords:domain.time.MJD')
class MJD(TimeInstant):
    date = Attribute('date', min_occurs=1, max_occurs=1)


@VO('coords:domain.time.TimeOffset')
class TimeOffset(TimeStamp):
    time = Attribute('time', min_occurs=1, max_occurs=1)
    time0 = Attribute('time0', min_occurs=1, max_occurs=1)


@VO('coords:domain.time.TimeFrame')
class TimeFrame(CoordFrame):
    ref_position = Attribute('refPosition', min_occurs=1, max_occurs=1)
    timescale = Attribute('timescale', min_occurs=1, max_occurs=1)
    ref_direction = Attribute('refDirection', min_occurs=0, max_occurs=1)


@VO('coords:domain.polarization.PolStokesEnum')
class PolStokesEnum(StringQuantity):
    pass


@VO('coords:domain.polarization.PolCircularEnum')
class PolCircularEnum(StringQuantity):
    pass


@VO('coords:domain.polarization.PolLinearEnum')
class PolLinearEnum(StringQuantity):
    pass


@VO('coords:domain.polarization.PolVectorEnum')
class PolVectorEnum(StringQuantity):
    pass


@VO('coords:domain.polarization.PolCoordValue')
class PolCoordValue(CoordValue):
    pass


@VO('coords:domain.polarization.PolLinear')
class PolLinear(PolCoordValue):
    cval = Attribute('cval', min_occurs=1, max_occurs=1)


@VO('coords:domain.polarization.PolVector')
class PolVector(PolCoordValue):
    cval = Attribute('cval', min_occurs=1, max_occurs=1)


@VO('coords:domain.polarization.PolStokes')
class PolStokes(PolCoordValue):
    cval = Attribute('cval', min_occurs=1, max_occurs=1)


@VO('coords:domain.polarization.PolCircular')
class PolCircular(PolCoordValue):
    cval = Attribute('cval', min_occurs=1, max_occurs=1)
