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
from rama.framework import Attribute, Composition, BaseType
from rama.utils.registry import VO


@VO('meas:Uncertainty')
class Uncertainty(BaseType):
    pass


@VO('meas:Symmetrical')
class Symmetrical(Uncertainty):
    radius = Attribute('meas:Symmetrical.radius', min_occurs=1, max_occurs=1)


@VO('meas:Asymmetrical1D')
class Asymmetrical1D(Uncertainty):
    plus = Attribute('meas:Asymmetrical1D.plus', min_occurs=1, max_occurs=1)
    minus = Attribute('meas:Asymmetrical1D.minus', min_occurs=1, max_occurs=1)


@VO('meas:Asymmetrical2D')
class Asymmetrical2D(Uncertainty):
    plus = Attribute('meas:Asymmetrical2D.plus', min_occurs=2, max_occurs=2)
    minus = Attribute('meas:Asymmetrical2D.minus', min_occurs=2, max_occurs=2)


@VO('meas:Asymmetrical3D')
class Asymmetrical3D(Uncertainty):
    plus = Attribute('meas:Asymmetrical3D.plus', min_occurs=3, max_occurs=3)
    minus = Attribute('meas:Asymmetrical3D.minus', min_occurs=3, max_occurs=3)


@VO('meas:Bounds1D')
class Bounds1D(Uncertainty):
    lo_limit = Attribute('meas:Bounds1D.loLimit', min_occurs=1, max_occurs=1)
    hi_limit = Attribute('meas:Bounds1D.hiLimit', min_occurs=1, max_occurs=1)


@VO('meas:Bounds2D')
class Bounds2D(Uncertainty):
    lo_limit = Attribute('meas:Bounds2D.loLimit', min_occurs=2, max_occurs=2)
    hi_limit = Attribute('meas:Bounds2D.hiLimit', min_occurs=2, max_occurs=2)


@VO('meas:Bounds3D')
class Bounds3D(Uncertainty):
    lo_limit = Attribute('meas:Bounds3D.loLimit', min_occurs=3, max_occurs=3)
    hi_limit = Attribute('meas:Bounds3D.hiLimit', min_occurs=3, max_occurs=3)


@VO('meas:Ellipse')
class Ellipse(Uncertainty):
    semi_axis = Attribute('meas:Ellipse.semiAxis', min_occurs=2, max_occurs=2)
    pos_angle = Attribute('meas:Ellipse.posAngle', min_occurs=1, max_occurs=1)


@VO('meas:Ellipsoid')
class Ellipsoid(Uncertainty):
    semi_axis = Attribute('meas:Ellipsoid.semiAxis', min_occurs=3, max_occurs=3)
    pos_angle = Attribute('meas:Ellipsoid.posAngle', min_occurs=2, max_occurs=2)


@VO('meas:Measure')
class Measure(BaseType):
    error = Composition('meas:Measure.error', min_occurs=0, max_occurs=1)


@VO('meas:Error')
class Error(BaseType):
    stat_error = Attribute('meas:Error.statError', min_occurs=0, max_occurs=1)
    sys_error = Attribute('meas:Error.sysError', min_occurs=0, max_occurs=1)


@VO('meas:GenericMeasure')
class GenericMeasure(Measure):
    coord = Attribute('meas:GenericMeasure.coord', min_occurs=1, max_occurs=1)


@VO('meas:Position')
class Position(Measure):
    coord = Attribute('meas:Position.coord', min_occurs=1, max_occurs=1)


@VO('meas:Time')
class Time(Measure):
    coord = Attribute('meas:Time.coord', min_occurs=1, max_occurs=1)


@VO('meas:Polarization')
class Polarization(Measure):
    coord = Attribute('meas:Polarization.coord', min_occurs=1, max_occurs=1)


@VO('meas:Velocity')
class Velocity(Measure):
    coord = Attribute('meas:Velocity.coord', min_occurs=1, max_occurs=1)


@VO('meas:ProperMotion')
class ProperMotion(Measure):
    lon = Attribute('meas:ProperMotion.lon', min_occurs=1, max_occurs=1)
    lat = Attribute('meas:ProperMotion.lat', min_occurs=1, max_occurs=1)
