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
from astropy import units as u
from matplotlib import pyplot as plt

from rama.models.measurements import GenericMeasure, Position, Time
from rama.models.measurements import Symmetrical


def plotter(plotter_class):
    def decorator(cls):
        def plot(instance, *args, **kwargs):
            instance._plotter.plot(instance, *args, **kwargs)

        cls._plotter = plotter_class()
        cls.plot = plot
        return cls
    return decorator


class VoAxis:
    name = None
    model_class = None

    def __init__(self, axis):
        self._axis = axis

    @property
    def dependent(self):
        return self._axis.dependent

    @property
    def measure(self):
        return self._axis.measure.coord

    @property
    def stat_error(self):
        try:
            errors = self._axis.measure.error.stat_error
        except:
            errors = None
            pass
        return errors

    @property
    def is_scalar(self):
        return self.measure.isscalar

    @property
    def unit(self):
        return self.measure.unit

    @classmethod
    def is_vo_axis_for(cls, axis):
        return isinstance(axis.measure, cls.model_class)


class TimeAxis(VoAxis):
    name = 'time'
    model_class = Time

    def __init__(self, axis):
        super().__init__(axis)
        try:
            # MCD NOTE: This is not where the axis name should be coming from.
            self.name = axis.measure.coord.name
        except:
            pass

    @property
    def measurement(self):
        return self._axis.measure.coord


class SkyPositionPlotter:
    MOLLWEIDE_TICKS = ['14h', '16h', '18h', '20h', '22h', '0h', '2h', '4h', '6h', '8h', '10h']

    def plot(self, instance, *args, **kwargs):
        ra = instance.measure.ra.wrap_at(180 * u.Unit('degree'))
        dec = instance.measure.dec
        fig = plt.figure()
        ax = fig.add_subplot(111, projection="mollweide")
        ax.set_xticklabels(self.MOLLWEIDE_TICKS)
        ax.grid(True)
        ax.scatter(ra.radian, dec.radian, *args, **kwargs)


@plotter(SkyPositionPlotter)
class SkyPositionAxis(VoAxis):
    name = 'position'
    model_class = Position


class GenericCoordMeasureAxis(VoAxis):
    name = 'generic'
    model_class = GenericMeasure

    def __init__(self, axis):
        super().__init__(axis)
        if hasattr( axis.measure.coord.cval, "name"):
            self.name = axis.measure.coord.cval.name
            # MCD NOTE: This is not where the axis name should be coming from.

    @property
    def measure(self):
        return self._axis.measure.coord.cval


def vo_axis_factory(axis):
    for cls in VoAxis.__subclasses__():
        if cls.is_vo_axis_for(axis):
            return cls(axis)

    raise ValueError(f"No VoAxis subclasses found for instance axis: {axis.measure}")


class CubePointPlotter:
    def plot(self, instance, x_name, y_name, *args, **kwargs):
        fig = plt.figure()
        ax = fig.add_subplot(111)
        ax.grid(True)

        ax.set_title("Cube Data Points")
        label = x_name
        if hasattr(instance[x_name].measure, 'unit'):
            label += f" ({instance[x_name].measure.unit})"
        ax.set_xlabel(label)
        label = y_name
        if hasattr(instance[y_name].measure, 'unit'):
            label += f" ({instance[y_name].measure.unit})"
        ax.set_ylabel(label)

        xvals = instance[x_name].measure.value
        yvals = instance[y_name].measure.value
        if ( isinstance( instance[y_name].stat_error, Symmetrical ) ):
            yerr = instance[y_name].stat_error.radius.value
        else:
            yerr = None
            
        ax.errorbar( xvals, yvals, yerr=yerr, fmt="bo", ecolor='#FF0000')

        plt.show()


@plotter(CubePointPlotter)
class CubePoint:
    def __init__(self, ndpoint):
        self._ndpoint = ndpoint
        self._index = {}
        self.dependent = []
        self.independent = []

        for observable in ndpoint.observable:
            vo_axis = vo_axis_factory(observable)
            self._index[vo_axis.name] = vo_axis
            if observable.dependent:
                self.dependent.append(vo_axis.name)
            else:
                self.independent.append(vo_axis.name)

    @property
    def axes(self):
        return self._index.values()

    def __getitem__(self, item):
        return self._index[item]

    def unroll(self):
        '''
        NDPoint structure is not good for unrolling automatically
          * it holds a composition of Observable..
          * unrolled, each NDPoint needs 1 value from each Observable
        '''
        observables = self._ndpoint.observable
        self._ndpoint.observables = None
        result = [self._unroll( observables, instance_index ) for instance_index in range(observables[0].cardinality)]
            
        self._ndpoint.observable = observables
        
        return result

    def _unroll(self, observables, instance_index ):
        instance = self._ndpoint._unroll( self._ndpoint, instance_index )
        instance.observable = [ item._unroll( item, instance_index) for item in observables ]
        return self.__class__(instance)
