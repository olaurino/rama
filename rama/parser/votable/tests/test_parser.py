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
import os

import numpy
import pytest
from astropy import units as u

from rama.models.coordinates import SpaceFrame
from rama.models.measurements import SkyPosition
from rama.parser.votable import VodmlParser, Context


def make_data_path(filename):
    basedir = os.path.dirname(__file__)
    return os.path.join(basedir, 'data', filename)


@pytest.fixture
def parser():
    return VodmlParser()


@pytest.fixture
def simple_position_file():
    return make_data_path('simple-position.vot.xml')


@pytest.fixture
def simple_position_columns_file():
    return make_data_path('simple-position-columns.vot.xml')


@pytest.fixture
def references_file():
    return make_data_path('references.vot.xml')

def test_parsing_coordinates(parser, simple_position_file):
    sky_positions = parser.find_instances(simple_position_file, SkyPosition)
    pos = sky_positions[0]

    assert 1 == len(sky_positions)
    assert 10.34209135 == pos.coord.ra.value
    assert 41.13232112 == pos.coord.dec.value
    assert "FK5" == pos.coord_frame.space_ref_frame.value
    assert "J1975" == pos.coord_frame.equinox.value
    assert "TOPOCENTER" == pos.coord_frame.ref_position.position.value


def test_references_are_same_object(parser, references_file):
    sky_positions = parser.find_instances(references_file, SkyPosition)

    assert sky_positions[0].coord_frame is sky_positions[1].coord_frame


def test_referred_built_only_once(parser, references_file):
    context = Context(parser, xml=references_file)
    frame = context.find_instances(SpaceFrame)[0]
    frame2 = context.find_instances(SpaceFrame)[0]
    sky_positions = context.find_instances(SkyPosition)

    assert frame is frame2
    assert sky_positions[0].coord_frame is frame
    assert sky_positions[1].coord_frame is frame


def test_context_without_filaname(parser):
    context = Context(parser)
    with pytest.raises(AttributeError):
        context.find_instances(SpaceFrame)


def test_parsing_columns(parser, simple_position_columns_file):
    context = Context(parser, xml=simple_position_columns_file)
    sky_positions = context.find_instances(SkyPosition)
    position = sky_positions[0]

    assert 1 == len(sky_positions)
    expected_ra = numpy.array([10.0, 20.0]) * u.deg
    expected_dec = numpy.array([11.0, 21.0]) * u.deg
    numpy.testing.assert_array_equal(expected_ra, position.coord.ra)
    numpy.testing.assert_array_equal(expected_dec, position.coord.dec)


# TODO
# def test_parsing_columns_non_existent_reference(parser, simple_position_columns_file):
#     context = Context(parser, xml=simple_position_columns_file)
#     sky_positions = context.find_instances(SkyPosition)
#
#     assert 1 == len(sky_positions)