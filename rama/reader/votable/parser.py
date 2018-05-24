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
import logging
import warnings

import itertools
from lxml import etree

from rama.framework import Attribute, Reference, Composition, InstanceId, RowReferenceWrapper, SingleReferenceWrapper, \
    BaseType
from rama.reader import Document
from rama.reader.votable.utils import get_children, get_local_name, \
    get_type_xpath_expression, parse_id, resolve_type, find_element_for_role, parse_literal, parse_column, \
    find_instance, parse_identifier_field

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

    def find(self, element_class: BaseType):
        type_id = [element_class.vodml_id,]
        subtype_ids = [subtype.vodml_id for subtype in element_class.all_subclasses()]
        all_ids = type_id + subtype_ids
        elements = [self.votable.document.xpath(get_type_xpath_expression('INSTANCE', id)) for id in all_ids]
        elements_flat = list(itertools.chain(*elements))
        return elements_flat

    def make(self, instance_class, xml_element, context):
        instance_id = parse_id(context, xml_element, instance_class)
        instance = context.get_instance_by_id(instance_id)
        if instance is not None:
            return instance
        else:
            return self._make(instance_class, instance_id, xml_element, context)

    def is_template(self, xml_element):
        has_template_parent = len(xml_element.xpath(f'./parent::{get_local_name("TEMPLATES")}')) > 0
        has_column_descendants = len(xml_element.xpath(f'.//{get_local_name("COLUMN")}')) > 0
        return has_template_parent or has_column_descendants

    def _make(self, instance_class, instance_id, xml_element, context):
        instance = instance_class()
        instance.is_template = self.is_template(xml_element)
        instance_info = _InstanceInfo(instance, instance_id, instance_class, xml_element, context)
        self._attach_fields(instance_info)
        decorated_instance = self._decorate_with_adapter(instance_info)
        context.add_instance(decorated_instance)
        return decorated_instance

    def _attach_fields(self, instance_info):
        fields = instance_info.instance_class.find_fields()
        for field_name, field_object in fields:
            field_reader = self.field_readers[field_object.__class__]
            field_instance = field_reader(instance_info.xml_element, field_object, instance_info.context)
            instance_info.instance.set_field(field_name, field_instance)

    def _decorate_with_adapter(self, instance_info):
        decorated_instance = instance_info.instance
        if hasattr(instance_info.instance_class, '__delegate__'):
            vo_instance = instance_info.instance
            decorated_instance = instance_info.instance_class.__delegate__(vo_instance)
            decorated_instance.__vo_object__ = vo_instance
        decorated_instance.__vo_id__ = instance_info.instance_id
        return decorated_instance


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
        self.role_id = field_object.vodml_id
        self.xml = find_element_for_role(xml_element, self.TAG_NAME, self.role_id)
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
    def foreign_key_instances(self):
        elements = get_children(self.xml, "FOREIGNKEY")
        return [self._parse_foreign_key(element) for element in elements]

    @property
    def all(self):
        if self.xml is not None:
            # In the votable 1.4 schema there is a choice among IDREF, FOREIGNKEY, and REMOREREFERENCE (currently
            # unsupported). In invalid cases where multiple elements are given, we give precedence to IDREF.
            if self.idref_instances:
                return self.select_return_value(self.idref_instances)
            if self.foreign_key_instances:
                return self.select_return_value(self.foreign_key_instances)
        return None

    def _parse_idref(self, xml_element):
        ref = InstanceId(xml_element.text, None)

        referred_instance = find_instance(self.context, ref)
        if referred_instance is not None:
            return SingleReferenceWrapper(referred_instance)

        referred_elements = xml_element.xpath(f"//{get_local_name('INSTANCE')}[@ID='{ref.id}']")

        if not referred_elements:
            # TODO make a single call?
            msg = f"Dangling reference {ref}"
            warnings.warn(msg, SyntaxWarning)
            LOG.warning(msg)
            return None

        referred_element = referred_elements[0]
        return SingleReferenceWrapper(self.parser.read_instance(referred_element, self.context))

    def _parse_foreign_key(self, xml_element):
        ref = InstanceId(None, parse_identifier_field(self.context, xml_element))
        referred_instance = find_instance(self.context, ref)
        if referred_instance is not None:
            return referred_instance

        target_id = xml_element.xpath(f"./{get_local_name('TARGETID')}")[0].text
        referred_elements = xml_element.xpath(f"//*[@ID='{target_id}']/{get_local_name('INSTANCE')}")

        instances = [self.parser.read_instance(referred_element, self.context)
                     for referred_element in referred_elements]
        instances_index = {tuple(instance.__vo_id__.keys): instance for instance in instances}
        references = [instances_index.get(tuple(key), None) for key in ref.keys]
        return RowReferenceWrapper(references)


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
        return [parse_literal(self.context, element) for element in elements]

    @property
    def columns(self):
        elements = get_children(self.xml, "COLUMN")
        return [parse_column(self.context, element) for element in elements]

    @property
    def all(self):
        if self.xml is not None:
            return self.select_return_value(self.structured_instances + self.constants + self.columns)
        return None
