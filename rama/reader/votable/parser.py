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
import warnings

from lxml import etree

from astropy.table import QTable
from astropy.io import votable

import numpy

from rama.framework import Attribute, Reference, Composition
from rama.reader import Document
from rama.reader.votable.utils import get_children, get_local_name, \
    get_type_xpath_expression, resolve_id, resolve_type, find_element_for_role, is_field

LOG = logging.getLogger(__name__)


class Votable(Document):
    def __init__(self, xml):
        super().__init__(xml)
        self.parser = Parser(self)
        self.document = None
        self._open_document(xml)

    def _open_document(self, xml_document):
        # TBD Maybe I should remove TABLEDATA to reduce the size of the tree. TABLEDATA will be parsed by astropy.
        parser = etree.XMLParser(ns_clean=True)
        tree = etree.parse(xml_document, parser)
        self.document = tree.getroot()

    def find_instances(self, element_class, context):
        return self.parser.find_instances(element_class, context)


class Parser:
    def __init__(self, votable_file):
        self.votable = votable_file
        self.field_readers = {
            Attribute: self.parse_attributes,
            Reference: self.parse_references,
            Composition: self.parse_composed_instances
        }

    def find_instances(self, element_class, context):
        return [self.read_instance(element, context) for element in self.find(element_class)]

    def read_instance(self, xml_element, context):
        type_id = resolve_type(xml_element)
        element_class = context.get_type_by_id(type_id)
        return self.make(element_class, xml_element, context)

    def parse_attributes(self, xml_element, field_object, context):
        return AttributeElement(xml_element, field_object, context, self).all

    def parse_composed_instances(self, xml_element, field_object, context):
        return CompositionElement(xml_element, field_object, context, self).all

    def parse_references(self, xml_element, field_object, context):
        return ReferenceElement(xml_element, field_object, context, self).all

    def find(self, element_class):
        type_id = element_class.vodml_id
        elements = self.votable.document.xpath(get_type_xpath_expression('INSTANCE', type_id))
        return elements

    def make(self, instance_class, xml_element, context):
        instance_id = resolve_id(xml_element)
        instance = context.get_instance_by_id(instance_id)
        if instance is not None:
            return instance
        else:
            return self._make(instance_class, instance_id, xml_element, context)

    def is_template(self, xml_element):
        return len(xml_element.xpath(f'.//{get_local_name("COLUMN")}')) > 0

    def _make(self, instance_class, instance_id, xml_element, context):
        instance = instance_class()
        instance.is_template = self.is_template(xml_element)
        instance_info = _InstanceInfo(instance, instance_id, instance_class, xml_element, context)
        self._attach_fields(instance_info)
        return self._decorate_with_adapter(instance_info)

    def _attach_fields(self, instance_info):
        fields = inspect.getmembers(instance_info.instance_class, is_field)
        for field_name, field_object in fields:
            field_reader = self.field_readers[field_object.__class__]
            field_instance = field_reader(instance_info.xml_element, field_object, instance_info.context)
            setattr(instance_info.instance, field_name, field_instance)

    def _decorate_with_adapter(self, instance_info):
        if hasattr(instance_info.instance_class, '__delegate__'):
            vo_instance = instance_info.instance
            instance_info.instance = instance_info.instance_class.__delegate__(vo_instance)
            instance_info.instance.__vo_object__ = vo_instance
        instance_info.instance.__vo_id__ = instance_info.instance_id
        instance_info.context.add_instance(instance_info.instance)
        return instance_info.instance


class _InstanceInfo:
    def __init__(self, instance, instance_id, instance_class, xml_element, context):
        self.context = context
        self.xml_element = xml_element
        self.instance_class = instance_class
        self.instance_id = instance_id
        self.instance = instance


class Element:
    TAG_NAME = None

    def __init__(self, xml_element, field_object, context, parser):
        self.field_object = field_object
        self.role_id = role_id = field_object.vodml_id
        self.xml = find_element_for_role(xml_element, self.TAG_NAME, role_id)
        self.context = context
        self.parser = parser

    def select_return_value(self, values):
        max_occurs = self.field_object.max
        if max_occurs == 1 and len(values) == 1:
            return values[0]

        if max_occurs == 1 and not values:
            return None

        return values


class ElementWithInstances(Element):
    @property
    def structured_instances(self):
        elements = get_children(self.xml, "INSTANCE")
        return [self.parser.read_instance(element, self.context) for element in elements]


class ReferenceElement(Element):
    TAG_NAME = 'REFERENCE'

    @property
    def idref_instances(self):
        elements = get_children(self.xml, "IDREF")
        return [self._parse_idref(element) for element in elements]

    @property
    def all(self):
        if self.xml is not None:
            return self.select_return_value(self.idref_instances)
        return None

    def _parse_idref(self, xml_element):
        ref = xml_element.text

        referred_instance = self.context.get_instance_by_id(ref)
        if referred_instance is not None:
            return referred_instance

        referred_elements = xml_element.xpath(f"//{get_local_name('INSTANCE')}[@ID='{ref}']")

        if not referred_elements:
            # TODO make a single call?
            msg = f"Dangling reference {ref}"
            warnings.warn(msg, SyntaxWarning)
            LOG.warning(msg)
            return None

        referred_element = referred_elements[0]
        return self.parser.read_instance(referred_element, self.context)


class CompositionElement(ElementWithInstances):
    TAG_NAME = 'COMPOSITION'

    # @property
    # def external_instances(self):
    #     elements = _get_children(self.xml, "EXTINSTANCES")
    #     return [self._parse_externals(element) for element in elements]

    @property
    def all(self):
        if self.xml is not None:
            return self.select_return_value(self.structured_instances)
        return None

    # def _parse_externals(self, xml_element):
    #     ref = xml_element.text
    #
    #     referred_instance = self.context.get_instance_by_id(ref)
    #     if referred_instance is not None:
    #         return referred_instance
    #
    #     referred_elements = xml_element.xpath(f"//{get_local_name('INSTANCE')}[@ID='{ref}']")
    #     if not len(referred_elements):
    #         # TODO make a single call?
    #         msg = f"Dangling reference {ref}"
    #         warnings.warn(msg, SyntaxWarning)
    #         LOG.warning(msg)
    #     else:
    #         referred_element = referred_elements[0]
    #         return self.context.read_instance(referred_element)


class AttributeElement(ElementWithInstances):
    TAG_NAME = "ATTRIBUTE"

    @property
    def constants(self):
        elements = get_children(self.xml, "LITERAL")
        return [self._parse_literal(element) for element in elements]

    @property
    def columns(self):
        elements = get_children(self.xml, "COLUMN")
        return [self._parse_column(element) for element in elements]

    @property
    def all(self):
        if self.xml is not None:
            return self.select_return_value(self.structured_instances + self.constants + self.columns)
        return None

    def _parse_literal(self, xml_element):
        value = xml_element.xpath("@value")[0]
        value_type = xml_element.xpath("@dmtype")[0]
        units = xml_element.xpath("@unit")
        unit = units[0] if units else None
        return self.context.get_type_by_id(value_type)(value, unit)

    def _parse_column(self, xml_element):
        column_ref = xml_element.xpath("@ref")[0]
        find_column_xpath = f"//{get_local_name('FIELD')}[@ID='{column_ref}']"
        column_elements = xml_element.xpath(find_column_xpath)
        if not column_elements:
            msg = f"Can't find column with ID {column_ref}. Setting values to NaN"
            LOG.warning(msg)
            warnings.warn(msg, SyntaxWarning)
            return numpy.NaN

        column_element = column_elements[0]
        table = self._parse_table(column_element)

        column = table[column_ref]

        name = column_element.xpath("@name")[0]
        column.name = name

        return column

    def _parse_table(self, column_element):

        table_elements = column_element.xpath(f"parent::{get_local_name('TABLE')}")
        if not table_elements:
            raise RuntimeError("COLUMN points to FIELD that does not have a TABLE parent")
        table_element = table_elements[0]
        table_index = int(table_element.xpath(f"count(preceding-sibling::{get_local_name('TABLE')})"))

        table_ids = table_element.xpath('@ID')
        if table_ids:
            no_id = False
            table_id = table_ids[0]
            table = self.context.get_table_by_id(table_id)
            if table is not None:
                return table
        else:
            no_id = True
            table_id = f"_GENERATED_ID_{table_index}"

        table = QTable(votable.parse_single_table(self.context.file, table_number=table_index).to_table())

        if no_id:
            table_id = id(table)
            table_element.attrib["ID"] = str(table_id)  # We set the attribute so we have an handle if we parse it again

        self.context.add_table(table_id, table)

        return table
