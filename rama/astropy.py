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
import numpy
from astropy.time import Time
from numpy import nan_to_num


class SkyCoordDecorator:
    """
    A drop-in replacement for astropy's SkyCoord. The initializer takes a basic SkyPosition
    instance and builds an astropy.coordinates.SkyCoord object that it then uses as a delegate for all calls
    and assignments.
    """

    def __new__(self, stc_position_coord):
        from astropy.coordinates import SkyCoord
        try:
            frame = stc_position_coord.frame.space_ref_frame.lower()
            equinox = stc_position_coord.frame.equinox
        except AttributeError:
            frame = "ICRS"
            equinox = None

        try:
            ra = stc_position_coord.ra
            dec = stc_position_coord.dec
            sky_coord = SkyCoord(frame=frame, equinox=equinox, ra=ra, dec=dec)
            return sky_coord
        except:
            return stc_position_coord


class TimeDecorator:
    def __new__(self, stc_time_coord):
        # FIXME I can't figure out how to make astropy parse times as time columns, so I have to break
        # them down and extract times
        from rama.models.coordinates import ISOTime
        time = stc_time_coord.date.tolist()
        try:
            scale = 'tt' if stc_time_coord.frame is None else stc_time_coord.frame.timescale.lower()
            t_format = "isot" if isinstance(stc_time_coord, ISOTime) else "jd"
        except AttributeError:
            scale = None
            t_format = None

        try:
            # Astropy doesn't support nan in Time objects yet (should be coming in Astropy 3)
            date = nan_to_num(numpy.array(time))
            time = Time(date, scale=scale, format=t_format)
            return time
        except:
            return stc_time_coord