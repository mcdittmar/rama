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

"""
This module provides astropy-specific adapters. See `~rama.adapters` for more information on adapters.
"""
import logging

from astropy.table import MaskedColumn
from astropy.coordinates import SkyCoord
from astropy.time import Time
from astropy.units import Quantity, UnitTypeError
import datetime

import numpy
from numpy import nan_to_num

from rama.models import coordinates

LOG = logging.getLogger(__name__)


class SkyCoordAdapter:
    """
    An adapter for sky coordinates. The initializer takes a standard
    :py:class:`~rama.models.coordinates.Point` instance and returns an astropy.coordinates.SkyCoord object based
    on the contents of the original instance.
    """

    def __new__(cls, spatial_coord):
        #
        # SkyCoord Frame Class map to coords model frame metadata
        # ----------------------------------------------------------------------------------
        #     SkyCoord:frame           | coords:refFrame  | coords:refPosition | equinox?   
        # ----------------------------------------------------------------------------------
        #    icrs                      | ICRS             | n/a                | N          
        #    fk4                       | FK4              | n/a                | Y [B1950.0]
        #    fk4noeterms               |                  | n/a                |            
        #    fk5                       | FK5              | n/a                | Y [J2000.0]
        #    galactic                  | GALACTIC         | n/a                | N          
        #    supergalactic             | SUPER_GALACTIC   | n/a                | N          
        #    galacticlsr               |                  | n/a                | N          
        #    hcrs                      |                  | n/a                |            
        #    barycentricmeanecliptic   | ECLIPTIC         | BARYCENTER         | Y          
        #    heliocentricmeanecliptic  | ECLIPTIC         | HELIOCENTER        | Y          
        #    barycentrictrueecliptic   | ECLIPTIC         | BARYCENTER         | Y          
        #    heliocentrictrueecliptic  | ECLIPTIC         | HELIOCENTER        | Y          
        #    heliocentriceclipticiau76 | ECLIPTIC         | HELIOCENTER        |            
        #    custombarycentricecliptic | ECLIPTIC         |                    |            
        #    lsr                       |                  |                    |            
        #    lsrk                      |                  |                    |            
        #    lsrd                      |                  |                    |            
        #    galactocentric            |                  |                    | N          
        #    cirs                      |                  |                    |            
        #    altaz                     |                  |                    | N          
        #    itrs                      |                  |                    | N          
        #    tete                      |                  |                    |            
        #    teme                      |                  |                    |            
        #    gcrs                      |                  |                    |            
        #    precessedgeocentric       |                  |                    | Y          
        #    geocentricmeanecliptic    | ECLIPTIC         | GEOCENTER          | Y          
        #    geocentrictrueecliptic    | ECLIPTIC         | GEOCENTER          | Y          
        # ----------------------------------------------------------------------------------
        #
        # Get Frame metadata from coord
        try:
            refframe = spatial_coord.coord_sys.frame.space_ref_frame.lower()
        except (AttributeError, ValueError) as exc:
            LOG.warning(f"Can not determine Reference Frame: {exc}")
            return spatial_coord
            
        try:
            refpos = spatial_coord.coord_sys.frame.ref_position.lower()
        except (AttributeError, ValueError):
            refpos = None

        try:
            equinox  = spatial_coord.coord_sys.frame.equinox
        except (AttributeError, ValueError):
            equinox = None

        # Resolve to SkyCoord frame tag.
        if refframe == "fk4" and equinox is None:
            frame = refframe
            equinox = "B1950.0"
        elif refframe == "fk5" and equinox is None:
            frame = refframe
            equinox = "J2000.0"
        elif refframe == "ecliptic" and refpos is not None:
            # STUB: will not work, do not know how to decide 'mean' vs 'true' yet
            frame = refpos + reframe
        elif refframe == "super_galactic":
            frame = "supergalactic"
        else:
            frame = refframe
            
        # Representation
        space = spatial_coord.coord_sys.coord_space
        if space is None or isinstance( space, coordinates.SphericalCoordSpace ):
            rep = "spherical"
        elif isinstance( space, coordinates.CartesianCoordSpace ):
            rep = "cartesian"

        # Instantiate
        try:
            if rep == "spherical" :
                # spherical coordinate space
                lon = spatial_coord.axis1
                lat = spatial_coord.axis2
                if spatial_coord.axis3 is None:
                    sky_coord = SkyCoord(lon, lat, frame=frame, equinox=equinox)
                else:
                    dist = spatial_coord.axis3
                    sky_coord = SkyCoord(lon, lat, dist, frame=frame, equinox=equinox)
                return sky_coord
            elif rep == "cartesian" :
                x = spatial_coord.axis1
                y = spatial_coord.axis2
                z = spatial_coord.axis3
                sky_coord = SkyCoord(frame=frame, equinox=equinox, representation_type=rep, x=x, y=y, z=z)
                return sky_coord
            else:
                raise ValueError("Unrecognized coordinate space type")
        except (AttributeError, UnitTypeError, ValueError, TypeError) as exc:
            LOG.warning(f"Can't apply adapter: {exc}")
            return spatial_coord


class TimeAdapter:
    """
    Adapter for time coordinates.  The initializer takes a standard
      :py:class:`~rama.models.coordinates.TimeStamp` instance
    and returns an astropy Time quantity.
    """
    def __new__(cls, time_coord):
        # TimeOffset does not have a direct counterpart in AstroPy.Time
        # It has 'Time from Epoch formats, but they are specific cases
        #   eg: cxcsec = offset from Chandra reference date, in TT.
        if isinstance( time_coord, coordinates.TimeOffset ):
            return time_coord

        # Massage values as needed
        if isinstance( time_coord, coordinates.ISOTime ):
            # ISOTime.date is datetime type for string type for columns
            #  - unify to string representation so can use 'fits' time format
            #  - replace empty values with datetime.max (date equivalent to NaN?)
            if isinstance( time_coord.date, datetime.datetime ):
                values = numpy.array(time_coord.date.isoformat())
            else:
                values = numpy.array(time_coord.date.data)
            values[ values == b''] = '9999-12-31T23:59:59.999999'
        else:
            # Astropy doesn't support nan in Time objects yet (should be coming in Astropy 3)
            if not isinstance( time_coord.date, Quantity):
                values = nan_to_num(numpy.array(time_coord.date))
            else:
                values = nan_to_num(time_coord.date)

        # Time Scale
        try:
            scale = 'tt' if time_coord.coord_sys is None else time_coord.coord_sys.frame.timescale.lower()
        except AttributeError:
            scale = None

        # Format (Representation)
        if isinstance( time_coord, coordinates.ISOTime ):
            t_format = "fits"
        elif isinstance( time_coord, coordinates.JD ):
            t_format = "jd"
        elif isinstance( time_coord, coordinates.MJD ):
            t_format = "mjd"
        else:
            t_format = None

        # Instantiate
        try:
            time = Time( values, scale=scale, format=t_format )
            return time
        except (AttributeError, ValueError) as exc:
            LOG.warning(f"Can't apply adapter: {exc}")
            return time_coord
        
    #def __new__(cls, time_coord):
        # FIXME I can't figure out how to make astropy parse iso times as time columns, so I have to break
        # them down and extract times
        #date = time_coord.date
        #if not isinstance(date, Quantity):
        #    quantity = False
        #    time = date.tolist()
        #else:
        #    quantity = True
        #    time = date
        #
        #try:
        #    # Astropy doesn't support nan in Time objects yet (should be coming in Astropy 3)
        #    if not quantity:
        #        time = nan_to_num(numpy.array(time))
        #    else:
        #        time = nan_to_num(time)
        #    time = Time(time, scale=scale, format=t_format)
        #    time.name = time_coord.date.name
        #    return time
        #except AttributeError:
        #    return time_coord
