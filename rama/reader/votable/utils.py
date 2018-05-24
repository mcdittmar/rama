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
import uuid
import warnings

from astropy.table import QTable
from astropy.io import votable

import numpy

from rama.framework import InstanceId

LOG = logging.getLogger(__name__)


def parse_column(context, xml_element):
    column_ref = xml_element.xpath("@ref")[0]
    find_column_xpath = f"//{get_local_name('FIELD')}[@ID='{column_ref}']"
    column_elements = xml_element.xpath(find_column_xpath)
    if not column_elements:
        msg = f"Can't find column with ID {column_ref}. Setting values to NaN"
        LOG.warning(msg)
        warnings.warn(msg, SyntaxWarning)
        return numpy.NaN

    column_element = column_elements[0]
    table = parse_table(context, column_element)

    column_ref = context.get_column_mapping(column_ref)
    column = table[column_ref]

    # Another hack: it simplify things if the byte columns are converted to strings... maybe this is an issue
    # in the VOTable parser needing some attention?
    try:
        if column.dtype == 'object':
            column = column.astype('U')
            table[column_ref] = column
    except:
        pass

    name = column_element.xpath("@name")[0]
    column.name = name

    # Kind of a hack, but I couldn't find a better way.
    # For instances with primary keys which use the same column(s) as a different attribute, in some but not all
    # cases changing the column names makes it impossible for the second pass to find the same column implementing a
    # different attribute (for instance, in test5, the same column is used for the primary key and for Source.name)
    # Whether or not this happens seems to depend on what class the column is (e.g. Quantity vs MappedColumn).
    try:
        column = table[column_ref]
    except KeyError:
        context.add_column_mapping(column_ref, name)
    return column


def parse_table(context, column_element):
    table_elements = column_element.xpath(f"parent::{get_local_name('TABLE')}")
    if not table_elements:
        raise RuntimeError("COLUMN points to FIELD that does not have a TABLE parent")
    table_element = table_elements[0]
    table_index = int(table_element.xpath(f"count(preceding-sibling::{get_local_name('TABLE')})"))

    table_ids = table_element.xpath('@ID')
    if table_ids:
        no_id = False
        table_id = table_ids[0]
        table = context.get_table_by_id(table_id)
        if table is not None:
            return table
    else:
        no_id = True
        table_id = f"_GENERATED_ID_{table_index}"

    table = QTable(votable.parse_single_table(context.file, table_number=table_index).to_table())

    if no_id:
        table_id = id(table)
        table_element.attrib["ID"] = str(table_id)  # We set the attribute so we have an handle if we parse it again

    context.add_table(table_id, table)

    return table


def parse_literal(context, xml_element):
    value = xml_element.xpath("@value")[0]
    value_type = xml_element.xpath("@dmtype")[0]
    units = xml_element.xpath("@unit")
    unit = units[0] if units else None
    return context.get_type_by_id(value_type)(value, unit)


def parse_id(context, xml_element, instance_class):
    keys = None
    primary_key_elements = xml_element.xpath(f"./{get_local_name('PRIMARYKEY')}")
    if primary_key_elements:
        keys = parse_identifier_field(context, primary_key_elements[0])
    ids = xml_element.xpath('@ID')
    if not ids:
        # Randomly generate an ID for each instance that doesn't have any.
        id = f"{instance_class.vodml_id}-{str(uuid.uuid4())}"
    else:
        id = ids[0]

    return InstanceId(id, keys)


def find_instance(context, key):
    context.get_instance_by_id(key)


def parse_identifier_field(context, xml_element):
    pk_fields = xml_element.xpath(f"./{get_local_name('PKFIELD')}")
    keys_array = numpy.array([parse_primary_key_field(context, pk_field) for pk_field in pk_fields]).T
    return keys_array


def parse_primary_key_field(context, xml_element):
    literal_elements = xml_element.xpath(f"./{get_local_name('LITERAL')}")
    if literal_elements:
        return parse_literal(context, literal_elements[0])
    column_elements = xml_element.xpath(f"./{get_local_name('COLUMN')}")
    if column_elements:
        return parse_column(context, column_elements[0]).data


def get_type_xpath_expression(tag_name, type_id):
    tag_selector = get_local_name(tag_name)
    return f"//{tag_selector}[@dmtype='{type_id}']"


def get_role_xpath_expression(tag_name, role_id):
    tag_selector = get_local_name(tag_name)
    return f".//{tag_selector}[@dmrole='{role_id}']"


def get_local_name(tag_name):
    return f"*[local-name() = '{tag_name}']"


def get_child_selector(tag_name):
    tag_selector = get_local_name(tag_name)
    return f"child::{tag_selector}"


def get_children(element, child_tag_name):
    return element.xpath(get_child_selector(child_tag_name))


def resolve_type(xml_element):
    element_type = xml_element.xpath("@dmtype")[0]
    return element_type


def find_element_for_role(xml_element, tag_name, role_id):
    elements = xml_element.xpath(get_role_xpath_expression(tag_name, role_id))
    n_elements = len(elements)

    if n_elements > 1:
        warnings.warn(SyntaxWarning, f"Too many elements with dmrole = {role_id}")

    if n_elements:
        return elements[0]

    return None
