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
# ----------------------------------------------------------------------
import itertools
import logging
import uuid
import warnings

import numpy
from astropy.io import votable
from astropy.table import QTable
from lxml import etree

from rama.framework import BaseType, InstanceId, Attribute, Reference, Composition, SingleReferenceWrapper, \
    RowReferenceWrapper
from rama.reader import Document, Reader
from rama.utils import ADAPTER_PROPERTY_NAME

LOG = logging.getLogger(__name__)


class Votable(Document):
    def __init__(self, xml):
        super().__init__(xml)
        # TBD Maybe I should remove TABLEDATA to reduce the size of the tree. TABLEDATA will be parsed by astropy.
        parser = etree.XMLParser(ns_clean=True)
        tree = etree.parse(xml, parser)
        self.document = tree.getroot()

    def find_instances(self, element_class, context):
        return find_instances(self, element_class, context)


def get_local_name(tag_name):
    return f"*[local-name() = '{tag_name}']"


TEMPLATES = get_local_name("TEMPLATES")
EXTINSTANCES = get_local_name("EXTINSTANCES")
INSTANCE = get_local_name("INSTANCE")
CONTAINER = get_local_name("CONTAINER")
LITERAL = get_local_name("LITERAL")
CONSTANT = get_local_name("CONSTANT")
COLUMN = get_local_name("COLUMN")
REFERENCE = get_local_name("REFERENCE")
COMPOSITION = get_local_name("COMPOSITION")
ATTRIBUTE = get_local_name("ATTRIBUTE")
TABLE = get_local_name("TABLE")
FIELD = get_local_name("FIELD")
PARAM = get_local_name("PARAM")
PRIMARYKEY = get_local_name("PRIMARYKEY")
FOREIGNKEY = get_local_name("FOREIGNKEY")
PKFIELD = get_local_name("PKFIELD")
IDREF = get_local_name("IDREF")
TARGETID = get_local_name("TARGETID")
ID = "ID"
REF_ATTR = "@ref"
ID_ATTR = f"@{ID}"
NAME_ATTR = "@name"
VALUE_ATTR = "@value"
TYPE_ATTR = "@dmtype"
ROLE_ATTR = "@dmrole"
UNIT_ATTR = "@unit"


def find_instances(votable: Votable, element_class: BaseType, context: Reader):
    return [read_instance(element, context) for element in find(votable, element_class)]


def find(votable: Votable, element_class: BaseType):
    type_id = [element_class.vodml_id, ]
    subtype_ids = [subtype.vodml_id for subtype in element_class.all_subclasses()]
    all_ids = type_id + subtype_ids
    elements = [find_instance_elements(votable.document, id) for id in all_ids]
    elements_flat = list(itertools.chain(*elements))
    return elements_flat


def find_instance_elements(xml_document, vodml_id):
    return xml_document.xpath(get_instance_element_by_id(vodml_id))


def get_instance_element_by_id(vodml_id):
    return get_type_xpath_expression("INSTANCE", vodml_id)


def read_instance(xml_element, context):
    type_id = resolve_type(xml_element)
    element_class = context.get_type_by_id(type_id)
    return make(element_class, xml_element, context)


def parse_table(context, column_element):
    """
    Parse VOTable <TABLE> Element

    Inputs:
      o context        - Reader
      o column_element - VOTable <FIELD> node

    Returns new/updated table as:
      o AstroPy QTable
    """
    # Get VOTable TABLE element..
    table_elements = column_element.xpath(f"parent::{TABLE}")
    if not table_elements:
        raise RuntimeError("COLUMN points to FIELD that does not have a TABLE parent")
    table_element = table_elements[0]

    # Which TABLE in the file?
    table_index = int(table_element.xpath(f"count(preceding-sibling::{TABLE})"))

    # Get or generate ID tag for this table (for storing)
    table_ids = table_element.xpath(ID_ATTR)
    if table_ids:
        table_id = table_ids[0]
    else:
        # NOTE: this only serves to create a no-match condition
        #       the actual table id is assigned within the table processing clause
        table_id = f"_GENERATED_ID_{table_index}"

    # Pull stored table from reader, or generate it and add it to reader
    table = context.get_table_by_id(table_id)
    if table is None:
        # Process table
        table = QTable(votable.parse_single_table(context.file, table_number=table_index).to_table())
        table_id = str(id(table)) # MCD TEMP: ACTUAL CODE CHANGE!!

        # Store table in context
        context.add_table(table_id, table)

        # Set the ID attribute in the XML so we have an handle if see it again
        table_element.attrib[ID] = table_id

    return table

def parse_id(context, xml_element, instance_class):
    keys = None
    primary_key_elements = xml_element.xpath(f"./{PRIMARYKEY}")
    if primary_key_elements:
        keys = parse_identifier_field(context, primary_key_elements[0])
    ids = xml_element.xpath(ID_ATTR)
    if not ids:
        # Randomly generate an ID for each instance that doesn't have any.
        id = f"{instance_class.vodml_id}-{str(uuid.uuid4())}"
    else:
        id = ids[0]

    return InstanceId(id, keys)


def parse_identifier_field(context, xml_element):
    pk_fields = xml_element.xpath(f"./{PKFIELD}")
    keys_array = numpy.array([parse_primary_key_field(context, pk_field) for pk_field in pk_fields]).T
    return keys_array


def parse_primary_key_field(context, xml_element):
    literal_elements = xml_element.xpath(f"./{LITERAL}")
    if literal_elements:
        return parse_literal(context, literal_elements[0])
    constant_elements = xml_element.xpath(f"./{CONSTANT}")
    if constant_elements:
        return parse_constant(context, constant_elements[0])
    column_elements = xml_element.xpath(f"./{COLUMN}")
    if column_elements:
        return parse_column(context, column_elements[0]).data


def get_type_xpath_expression(tag_name, type_id):
    tag_selector = get_local_name(tag_name)
    return f"//{tag_selector}[{TYPE_ATTR}='{type_id}']"


def get_role_xpath_expression(tag_name, role_id):
    return f".//{tag_name}[{ROLE_ATTR}='{role_id}']"


def get_local_name(tag_name):
    return f"*[local-name() = '{tag_name}']"


def get_child_selector(tag_name):
    return f"child::{tag_name}"


def get_children(element, child_tag_name):
    return element.xpath(get_child_selector(child_tag_name))


def resolve_type(xml_element):
    element_type = xml_element.xpath(TYPE_ATTR)[0]
    return element_type


def find_element_for_role(xml_element, tag_name, role_id):
    elements = xml_element.xpath(get_role_xpath_expression(tag_name, role_id))
    n_elements = len(elements)

    if n_elements > 1:
        warnings.warn(SyntaxWarning, f"Too many elements with dmrole = {role_id}")

    if n_elements:
        return elements[0]

    return None


def is_template(xml_element):
    """
    Is Element within TEMPLATES node?
    """
    has_template_ancestor = len(xml_element.xpath(f'./ancestor::{TEMPLATES}')) > 0
    return has_template_ancestor


def decorate_with_adapter(instance_info):
    decorated_instance = instance_info.instance
    if hasattr(instance_info.instance_class, ADAPTER_PROPERTY_NAME):
        vo_instance = instance_info.instance
        adapter = getattr(instance_info.instance_class, ADAPTER_PROPERTY_NAME)
        decorated_instance = adapter(vo_instance)
        decorated_instance.__vo_object__ = vo_instance
    decorated_instance.__vo_id__ = instance_info.instance_id
    return decorated_instance


def attach_fields(instance_info):
    field_readers = {
        Attribute: parse_attributes,
        Reference: parse_references,
        Composition: parse_composed_instances
    }
    fields = instance_info.instance_class.find_fields()
    for field_name, field_object in fields:
        field_reader = field_readers[field_object.__class__]
        field_instance = field_reader(instance_info.xml_element, field_object, instance_info.context)
        instance_info.instance.set_field(field_name, field_instance)
    return instance_info
#
# ----------------------------------------------------------------------
def parse_attributes(xml_element, field_object, context):
    xml_element = find_element_for_role(xml_element, ATTRIBUTE, field_object.vodml_id)
    if xml_element is not None:
        values = parse_structured_instances(xml_element, context) +\
                 parse_literals(xml_element, context) +\
                 parse_constants(xml_element, context) +\
                 parse_columns(xml_element, context)
        return field_object.select_return_value(values)


def parse_composed_instances(xml_element, field_object, context):
    xml_element = find_element_for_role(xml_element, COMPOSITION, field_object.vodml_id)
    if xml_element is not None:
        values = parse_structured_instances(xml_element, context) +\
                 parse_extinstances(xml_element, context)
        result = field_object.select_return_value(values)
        return result


def parse_references(xml_element, field_object, context):
    # In the votable 1.4 schema there is a choice among IDREF, FOREIGNKEY, and REMOREREFERENCE (currently
    # unsupported). In invalid cases where multiple elements are given, we give precedence to IDREF.

    xml_element = find_element_for_role(xml_element, REFERENCE, field_object.vodml_id)
    if xml_element is not None:
        idref_instances = parse_idref_instances(xml_element, context)
        if idref_instances:
            return field_object.select_return_value(idref_instances)

        foreign_key_instances = parse_foreign_key_instances(xml_element, context)
        if foreign_key_instances:
            return field_object.select_return_value(foreign_key_instances)

def parse_structured_instances(xml_element, context):
    elements = get_children(xml_element, INSTANCE)
    return [read_instance(element, context) for element in elements]

def parse_literals(xml_element, context):
    elements = get_children(xml_element, LITERAL)
    return [parse_literal(context, element) for element in elements]

def parse_constants(xml_element, context):
    elements = get_children(xml_element, CONSTANT)
    return [parse_constant(context, element) for element in elements]

def parse_columns(xml_element, context):
    elements = get_children(xml_element, COLUMN)
    return [parse_column(context, element) for element in elements]

def parse_idref_instances(xml_element, context):
    elements = get_children(xml_element, IDREF)
    return [parse_idref(element, context) for element in elements]

def parse_foreign_key_instances(xml_element, context):
    elements = get_children(xml_element, FOREIGNKEY)
    return [parse_foreign_key(element, context) for element in elements]

def parse_extinstances(xml_element, context):
    elements = get_children(xml_element, EXTINSTANCES)
    instances = []
    for element in elements:
        instances += parse_extinstance(element, context)
    return instances

#
# ----------------------------------------------------------------------
def parse_extinstance(xml_element, context):
    # get extinstance reference id
    ref = InstanceId(xml_element.text, None)
    
    # pull referred instance element
    referred_elements = xml_element.xpath(f"//{INSTANCE}[{ID_ATTR}='{ref.id}']")
    if not referred_elements:
        # TODO make a single call?
        msg = f"Dangling reference {ref}"
        warnings.warn(msg, SyntaxWarning)
        LOG.warning(msg)
        return None
    referred_element = referred_elements[0]

    # process extinstance template
    #  - we want the individual instances in this case.
    #    may be getting appended to local instances and needs to be a list of instances
    instance = read_instance( referred_element, context )
    instances = instance.unroll()

    # FOREIGNKEY = constrains returned instance set
    has_foreign_key = len(referred_element.xpath(f'./child::{CONTAINER}/{FOREIGNKEY}')) > 0

    if not has_foreign_key:
        # No screening criteria, return List of resolved instances
        result = instances
    else:
        element = get_children(referred_element, CONTAINER)[0]
        result = group_extinstances( instances, element, context )

    return result


def group_extinstances( instances, xml_element, context ):
    # ----------------------------------------------------------------------
    # instances: List of resolved EXTINSTANCEs
    # xml_element: CONTAINER element
    #----------------------------------------------------------------------
    # CONTAINER is a backward connection to a parent instance.
    #   - Contains one of: IDREF, FOREIGNKEY, REMOTEREF
    #      - implementing FOREIGNKEY

    fk_elements = get_children(xml_element, FOREIGNKEY)
    for fk_element in fk_elements:
        target_id = fk_element.xpath(f"./{TARGETID}")[0].text
        
        # Get keys associated with each instance
        instance_keys = parse_identifier_field(context, fk_element)
        #print("DEBUG: EXTINSTANCE KEYS = %s"%(str(instance_keys)))
        
        # Get target keys
        target = context.get_instance_by_id( InstanceId( target_id, None ) )
        if target is not None:
            # Untested
            target_instance_keys = target.__vo_id__.keys
        else:
            # Target instance not already processed..
            # NOTE: do not want to 'make' it, can set up recursive loop
            #  ie: we are currently processing the Target instance.
            target_elements = xml_element.xpath(f"//*[{ID_ATTR}='{target_id}']")
            target_element = target_elements[0]
            
            # Resolve PRIMARYKEY value set from target element:
            #   pulled from read_instance() and make()
            type_id = resolve_type(target_element)
            element_class = context.get_type_by_id(type_id)
            target_instance_id = parse_id(context, target_element, element_class)
            target_instance_keys = target_instance_id.keys
            #print("DEBUG: TARGET instance keys = %s"%(str(target_instance_keys)))
            
    # Have keys resolved.. sort instances
    # target instance keys are the selection criteria
    sorted_instances = {}
    for key in target_instance_keys:
        matches = [instances[n] for n in range(len(instances)) if ( tuple(key) == tuple(instance_keys[n]) )]
        sorted_instances[ tuple(key) ] = matches
                
    # We want to return slices of the sorted_instances, with 1 instance per target 'row'
    #   - determine maximumn # matches; this is # slices to return`
    #   - pad each entry to the same length (with None)
    #   - generate slices
    result = []
    max_matches = max( [len(matches) for matches in sorted_instances.values() ] )

    for values in sorted_instances.values():
        values += [None]*(max_matches - len(values))

    for n in range(max_matches):
        group = [ sorted_instances[ tuple(key) ][n] for key in target_instance_keys ]
        result.append(group)

    return result


def parse_literal(context, xml_element):
    value = xml_element.xpath(VALUE_ATTR)[0]
    value_type = xml_element.xpath(TYPE_ATTR)[0]
    units = xml_element.xpath(UNIT_ATTR)
    unit = units[0] if units else None
    return context.get_type_by_id(value_type)(value, unit)

def parse_constant(context, xml_element):
    """
    Interpret input VODML <CONSTANT> element and associated VOTable <PARAM>

    Inputs:
      o context        - Reader
      o xml_element    - VODML <COLUMN> node

    Returns
      o value as type mapping to specified vodml-id
         - interpretation done by Reader
    """
    # Find VOTable PARAM element referenced by CONSTANT
    param_ref = xml_element.xpath(REF_ATTR)[0]
    find_param_xpath = f"//{PARAM}[{ID_ATTR}='{param_ref}']"
    param_elements = xml_element.xpath(find_param_xpath)
    if not param_elements:
        msg = f"Can't find param with ID {param_ref}.  Setting value to NaN"
        LOG.warning(msg)
        warnings.warn(msg, SyntaxWarning)
        return numpy.NaN
    param_element = param_elements[0]

    # Pull desired type, and param data
    value_type = xml_element.xpath(TYPE_ATTR)[0]
    value = param_element.xpath(VALUE_ATTR)[0]
    units = param_element.xpath(UNIT_ATTR)
    unit = units[0] if units else None

    # Create instance of specified type
    #   - resulting type determined by Reader
    result = context.get_type_by_id(value_type)(value, unit)

    # MCD NOTE:
    #  o unlike columns, there is no place to store PARAM name in the result
    #    at least not for many base types (eg ivoa:real )
    #  o CONSTANTs within TEMPLATES are singluar while
    #    COLUMNs   within TEMPLATES are arrays (per row)
    #  o what does this do for multiplicity > 1?
    #    a) float( [a,b] ) == Error?
    #    b) Quantity may work, but maybe problems in FIELD (2D array)
    
    return result

def parse_column(context, xml_element):
    """
    Interpret input VODML <COLUMN> element and associated VOTable <FIELD>

    Inputs:
      o context     - Reader
      o xml_element - VODML <COLUMN> node to process

    Returns column as:
      o AstroPy Quantity if FIELD has units
      o AstroPy MaskedColumn if FIELD does not have units
    """
    # Find VOTable FIELD element referenced by COLUMN
    column_ref = xml_element.xpath(REF_ATTR)[0]
    find_column_xpath = f"//{FIELD}[{ID_ATTR}='{column_ref}']"
    column_elements = xml_element.xpath(find_column_xpath)
    if not column_elements:
        msg = f"Can't find column with ID {column_ref}. Setting values to NaN"
        LOG.warning(msg)
        warnings.warn(msg, SyntaxWarning)
        return numpy.NaN
    column_element = column_elements[0]

    # Get Table containing the column
    #  - will either process table or pull from storage in context.
    table = parse_table(context, column_element)
    
    # Pull column from table
    #  - check column mapping in case ID is an alias for a different column (see below).
    column_ref = context.get_column_mapping(column_ref)
    column = table[column_ref]

    # We want the column to contain the FIELD name.. BUT changing it can
    # affect future access to the same column.  For example, if the same
    # column is used in multiple roles.
    # ======================================================================
    # QTable has 2 kinds of columns:
    # ======================================================================
    # MaskedColumn
    #   + column.name appears to be the column ID, probably falling back on NAME
    #   + changing column name appears to also change the table access.
    #       ie: afterwards, table[<ref_id>] does not work.
    #   + so need to add a column_mapping to retain link between ref_id and column
    #   * can CAUSE a problem if multiple columns have the same name but different ids
    #
    # Quantity Column
    #   + does not natively have a 'name' attribute
    #   + settting column.name adds it to the object
    #   + this has no affect on the table access
    # ======================================================================
    # Get name from FIELD element.. assign to column
    name = column_element.xpath(NAME_ATTR)[0]
    column.name = name
    try:
        # check if the assignment affected access.
        dummy = table[column_ref]
    except KeyError:
        # it did.. add column mapping for this column
        context.add_column_mapping(column_ref, name)

    # Another hack:
    #   it simplify things if the byte columns are converted to strings...
    #   maybe this is an issue in the VOTable parser needing some attention?
    try:
        if column.dtype == 'object':
            column = column.astype('U')
            table[column_ref] = column
    except:
        pass

    return column

def parse_idref(xml_element, context):
    ref = InstanceId(xml_element.text, None)

    referred_elements = xml_element.xpath(f"//{INSTANCE}[{ID_ATTR}='{ref.id}']")

    if not referred_elements:
        # TODO make a single call?
        msg = f"Dangling reference {ref}"
        warnings.warn(msg, SyntaxWarning)
        LOG.warning(msg)
        return None

    referred_element = referred_elements[0]
    return SingleReferenceWrapper(read_instance(referred_element, context))


def parse_foreign_key(xml_element, context):
    ref = InstanceId(None, parse_identifier_field(context, xml_element))

    target_id = xml_element.xpath(f"./{TARGETID}")[0].text
    referred_elements = xml_element.xpath(f"//*[{ID_ATTR}='{target_id}']/{INSTANCE}")

    instances = [read_instance(referred_element, context)
                 for referred_element in referred_elements]
    instances_index = {tuple(instance.__vo_id__.keys): instance for instance in instances}
    references = [instances_index.get(tuple(key), None) for key in ref.keys]
    return RowReferenceWrapper(references)

#
# ----------------------------------------------------------------------
def make(instance_class, xml_element, context):
    instance_id = parse_id(context, xml_element, instance_class)
    instance = context.get_instance_by_id(instance_id)
    if instance is not None:
        return instance
    else:
        instance = instance_class()
        instance.is_template = is_template(xml_element)
        instance_info = InstanceInfo(instance, instance_id, instance_class, xml_element, context)
        instance_info = attach_fields(instance_info)
        decorated_instance = decorate_with_adapter(instance_info)
        context.add_instance(decorated_instance)
        return decorated_instance


class InstanceInfo:
    def __init__(self, instance, instance_id, instance_class, xml_element, context):
        self.context = context
        self.xml_element = xml_element
        self.instance_class = instance_class
        self.instance_id = instance_id
        self.instance = instance
