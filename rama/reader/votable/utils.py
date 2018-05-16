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
import warnings


def resolve_id(xml_element):
    ids = xml_element.xpath('@ID')
    if ids:
        return ids[0]
    return None


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
