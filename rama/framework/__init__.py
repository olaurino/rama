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
import inspect
import logging
from weakref import WeakKeyDictionary

from astropy.units import Quantity

LOG = logging.getLogger(__name__)


class VodmlDescriptor:
    def __init__(self, vodml_id, min_occurs=0, max_occurs=1):
        self.vodml_id = vodml_id
        self.default = None
        self.min = min_occurs
        self.max = max_occurs
        self.name = None
        self.values = WeakKeyDictionary()

    def __get__(self, instance, owner):
        if instance is None:
            return self
        return self.values.get(instance, self.default)

    def __set__(self, instance, value):
        self.values[instance] = value
        if hasattr(value, "__parent__"):
            value.__parent__ = instance

    def __delete__(self, instance):
        del self.values[instance]

    def __set_name__(self, owner, name):
        self.name = name


class Composition(VodmlDescriptor):
    def get_index(self, instance, instance_index):
        """
        For each member of the composition call unroll and return a list of the resulting instances
        """
        values = self.values[instance]
        if values is None:
            return
        return [value.__class__.unroll(value, instance_index) for value in values]


class Attribute(VodmlDescriptor):
    def __set__(self, instance, value):
        VodmlDescriptor.__set__(self, instance, value)
        if hasattr(value, 'count'):  # BaseTypes
            instance.count = value.count
        elif isinstance(value, Quantity) and not value.isscalar:
            instance.count = len(value)

    def get_index(self, instance, instance_index):
        value = self.values[instance]
        if self._is_basetype(value):
            return value.__class__.unroll(value, instance_index)
        if self._is_string(value):
            return value
        if value is not None:
            return value[instance_index]

    def _is_string(self, value):
        return isinstance(value, str)

    def _is_basetype(self, value):
        return isinstance(value, BaseType)


class Reference(VodmlDescriptor):
    def get_index(self, instance, _):
        """
        References should just pass through
        """
        return self.values[instance]


class BaseType:
    def __init__(self):
        self.__parent__ = None
        self.__count = None

    def set_field(self, field_name, field_instance):
        setattr(self, field_name, field_instance)

    @property
    def count(self):
        return self.__count

    @count.setter
    def count(self, value):
        self.__count = value

    def flatten(self):
        return [self.__class__.unroll(self, instance_index) for instance_index in range(self.count)]

    @classmethod
    def find_fields(cls):
        def is_field(attr):
            return inspect.isdatadescriptor(attr) and isinstance(attr, VodmlDescriptor)

        return inspect.getmembers(cls, is_field)

    @classmethod
    def unroll(cls, template_instance, instance_index):
        instance = cls()
        for field_name, field_object in cls.find_fields():
            value = field_object.get_index(template_instance, instance_index)
            instance.set_field(field_name, value)
        return instance
