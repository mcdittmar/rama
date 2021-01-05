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
#----------------------------------------------------------------------------------------------------
from rama.adapters.astropy import SkyCoordAdapter, TimeAdapter
from rama.framework import Attribute, Reference, Composition, BaseType
from rama.models.ivoa import StringQuantity
from rama.utils import Adapter
from rama.utils.registry import VO

# ----------------------------------------------------------------------
# Manually-Generated Classes:
#  o override basic implementation with special handling
#     Epoch:     primitiveType in model (not auto-generated)
#     TimeStamp: Interpret as AstroPy.Time type
#     Point:     Interpret as AstroPy.SkyCoord type
## ----------------------------------------------------------------------

# primitiveType - classes not generated for primitives (TODO - fix in model?)
@VO('coords:Epoch')
class Epoch(StringQuantity):
    pass


@VO('coords:Handedness')
class Handedness(StringQuantity):
    pass


@VO('coords:PolStateEnum')
class PolStateEnum(StringQuantity):
    pass


@VO('coords:Coordinate')
class Coordinate(BaseType):
    coord_sys = Reference('coords:Coordinate.coordSys', min_occurs=1, max_occurs=1)


@VO('coords:BinnedCoordinate')
class BinnedCoordinate(Coordinate):
    cval = Attribute('coords:BinnedCoordinate.cval', min_occurs=1, max_occurs=1)


@VO('coords:PixelIndex')
class PixelIndex(BinnedCoordinate):
    pass


@VO('coords:PhysicalCoordinate')
class PhysicalCoordinate(Coordinate):
    cval = Attribute('coords:PhysicalCoordinate.cval', min_occurs=1, max_occurs=1)


@VO('coords:Point')
@Adapter(SkyCoordAdapter)
class Point(Coordinate):
    axis1 = Attribute('coords:Point.axis1', min_occurs=0, max_occurs=1)
    axis2 = Attribute('coords:Point.axis2', min_occurs=0, max_occurs=1)
    axis3 = Attribute('coords:Point.axis3', min_occurs=0, max_occurs=1)
    pass

@VO('coords:TimeStamp')
@Adapter(TimeAdapter)
class TimeStamp(Coordinate):
    pass


@VO('coords:TimeOffset')
class TimeOffset(TimeStamp):
    time = Attribute('coords:TimeOffset.time', min_occurs=1, max_occurs=1)
    time0 = Attribute('coords:TimeOffset.time0', min_occurs=1, max_occurs=1)


@VO('coords:TimeInstant')
class TimeInstant(TimeStamp):
    pass


@VO('coords:JD')
class JD(TimeInstant):
    date = Attribute('coords:JD.date', min_occurs=1, max_occurs=1)


@VO('coords:MJD')
class MJD(TimeInstant):
    date = Attribute('coords:MJD.date', min_occurs=1, max_occurs=1)


@VO('coords:ISOTime')
class ISOTime(TimeInstant):
    date = Attribute('coords:ISOTime.date', min_occurs=1, max_occurs=1)


@VO('coords:PolCoordinate')
class PolCoordinate(Coordinate):
    pass


@VO('coords:PolState')
class PolState(PolCoordinate):
    cval = Attribute('coords:PolState.cval', min_occurs=1, max_occurs=1)


@VO('coords:RefLocation')
class RefLocation(BaseType):
    pass


@VO('coords:StdRefLocation')
class StdRefLocation(RefLocation):
    position = Attribute('coords:StdRefLocation.position', min_occurs=1, max_occurs=1)


@VO('coords:CustomRefLocation')
class CustomRefLocation(RefLocation):
    epoch = Attribute('coords:CustomRefLocation.epoch', min_occurs=0, max_occurs=1)
    position = Attribute('coords:CustomRefLocation.position', min_occurs=1, max_occurs=1)
    velocity = Attribute('coords:CustomRefLocation.velocity', min_occurs=0, max_occurs=1)


@VO('coords:CoordSpace')
class CoordSpace(BaseType):
    axis = Composition('coords:CoordSpace.axis', min_occurs=1, max_occurs=-1)


@VO('coords:Axis')
class Axis(BaseType):
    name = Attribute('coords:Axis.name', min_occurs=0, max_occurs=1)


@VO('coords:ContinuousAxis')
class ContinuousAxis(Axis):
    domain_min = Attribute('coords:ContinuousAxis.domainMin', min_occurs=0, max_occurs=1)
    domain_max = Attribute('coords:ContinuousAxis.domainMax', min_occurs=0, max_occurs=1)
    cyclic = Attribute('coords:ContinuousAxis.cyclic', min_occurs=0, max_occurs=1)


@VO('coords:BinnedAxis')
class BinnedAxis(Axis):
    length = Attribute('coords:BinnedAxis.length', min_occurs=1, max_occurs=1)


@VO('coords:DiscreteSetAxis')
class DiscreteSetAxis(Axis):
    pass


@VO('coords:CoordFrame')
class CoordFrame(BaseType):
    pass


@VO('coords:GenericFrame')
class GenericFrame(CoordFrame):
    ref_position = Attribute('coords:GenericFrame.refPosition', min_occurs=1, max_occurs=1)
    planetary_ephem = Attribute('coords:GenericFrame.planetaryEphem', min_occurs=0, max_occurs=1)


@VO('coords:SpaceFrame')
class SpaceFrame(CoordFrame):
    ref_position = Attribute('coords:SpaceFrame.refPosition', min_occurs=1, max_occurs=1)
    space_ref_frame = Attribute('coords:SpaceFrame.spaceRefFrame', min_occurs=1, max_occurs=1)
    equinox = Attribute('coords:SpaceFrame.equinox', min_occurs=0, max_occurs=1)
    planetary_ephem = Attribute('coords:SpaceFrame.planetaryEphem', min_occurs=0, max_occurs=1)


@VO('coords:TimeFrame')
class TimeFrame(CoordFrame):
    ref_position = Attribute('coords:TimeFrame.refPosition', min_occurs=1, max_occurs=1)
    timescale = Attribute('coords:TimeFrame.timescale', min_occurs=1, max_occurs=1)
    ref_direction = Attribute('coords:TimeFrame.refDirection', min_occurs=0, max_occurs=1)


@VO('coords:CoordSys')
class CoordSys(BaseType):
    pass


@VO('coords:AstroCoordSystem')
class AstroCoordSystem(CoordSys):
    coord_sys = Composition('coords:AstroCoordSystem.coordSys', min_occurs=1, max_occurs=-1)


@VO('coords:PixelCoordSystem')
class PixelCoordSystem(CoordSys):
    pixel_space = Composition('coords:PixelCoordSystem.pixelSpace', min_occurs=1, max_occurs=1)


@VO('coords:PixelSpace')
class PixelSpace(CoordSpace):
    handedness = Attribute('coords:PixelSpace.handedness', min_occurs=0, max_occurs=1)


@VO('coords:PhysicalCoordSys')
class PhysicalCoordSys(CoordSys):
    coord_space = Composition('coords:PhysicalCoordSys.coordSpace', min_occurs=0, max_occurs=1)
    frame = Composition('coords:PhysicalCoordSys.frame', min_occurs=0, max_occurs=1)


@VO('coords:GenericSys')
class GenericSys(PhysicalCoordSys):
    pass


@VO('coords:SpaceSys')
class SpaceSys(PhysicalCoordSys):
    pass


@VO('coords:TimeSys')
class TimeSys(PhysicalCoordSys):
    pass


@VO('coords:PhysicalCoordSpace')
class PhysicalCoordSpace(CoordSpace):
    pass


@VO('coords:GenericCoordSpace')
class GenericCoordSpace(PhysicalCoordSpace):
    pass


@VO('coords:SphericalCoordSpace')
class SphericalCoordSpace(PhysicalCoordSpace):
    pass


@VO('coords:CartesianCoordSpace')
class CartesianCoordSpace(PhysicalCoordSpace):
    pass
