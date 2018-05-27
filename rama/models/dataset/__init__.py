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
from rama.framework import Attribute, Reference, Composition, BaseType
from rama.models.ivoa import StringQuantity
from rama.utils.registry import VO


@VO('ds:experiment.Observation')
class Observation(BaseType):
    observation_i_d = Attribute('observationID', min_occurs=1, max_occurs=1)
    obs_config = Composition('obsConfig', min_occurs=1, max_occurs=1)
    result = Composition('result', min_occurs=0, max_occurs=-1)
    target = Composition('target', min_occurs=1, max_occurs=1)
    proposal = Composition('proposal', min_occurs=0, max_occurs=1)


@VO('ds:experiment.ObsConfig')
class ObsConfig(BaseType):
    bandpass = Attribute('bandpass', min_occurs=0, max_occurs=1)
    datasource = Attribute('datasource', min_occurs=0, max_occurs=1)
    facility = Composition('facility', min_occurs=0, max_occurs=1)
    instrument = Composition('instrument', min_occurs=0, max_occurs=1)


@VO('ds:experiment.BaseTarget')
class BaseTarget(BaseType):
    name = Attribute('name', min_occurs=1, max_occurs=1)
    description = Attribute('description', min_occurs=0, max_occurs=1)
    position = Reference('position', min_occurs=0, max_occurs=1)


@VO('ds:experiment.Target')
class Target(BaseTarget):
    object_class = Attribute('objectClass', min_occurs=0, max_occurs=1)


@VO('ds:experiment.AstroTarget')
class AstroTarget(BaseTarget):
    object_class = Attribute('objectClass', min_occurs=0, max_occurs=1)
    spectral_class = Attribute('spectralClass', min_occurs=0, max_occurs=1)
    redshift = Attribute('redshift', min_occurs=0, max_occurs=1)
    var_ampl = Attribute('varAmpl', min_occurs=0, max_occurs=1)


@VO('ds:experiment.Instrument')
class Instrument(BaseType):
    name = Attribute('name', min_occurs=1, max_occurs=1)


@VO('ds:experiment.Proposal')
class Proposal(BaseType):
    identifier = Attribute('identifier', min_occurs=1, max_occurs=1)


@VO('ds:experiment.Derived')
class Derived(BaseType):
    derived_element = Composition('derivedElement', min_occurs=0, max_occurs=-1)


@VO('ds:dataset.Dataset')
class Dataset(BaseType):
    data_product_type = Attribute('dataProductType', min_occurs=1, max_occurs=1)
    data_product_subtype = Attribute('dataProductSubtype', min_occurs=0, max_occurs=1)
    curation = Composition('curation', min_occurs=1, max_occurs=1)
    data_id = Composition('dataID', min_occurs=1, max_occurs=1)


@VO('ds:experiment.ObsDataset')
class ObsDataset(Dataset):
    calib_level = Attribute('calibLevel', min_occurs=0, max_occurs=1)
    derived = Composition('derived', min_occurs=0, max_occurs=1)
    target = Reference('target', min_occurs=1, max_occurs=1)
    proposal = Reference('proposal', min_occurs=0, max_occurs=1)
    obs_config = Reference('obsConfig', min_occurs=0, max_occurs=1)


@VO('ds:experiment.DerivedElement')
class DerivedElement(BaseType):
    pass


@VO('ds:experiment.DerivedScalar')
class DerivedScalar(DerivedElement):
    name = Attribute('name', min_occurs=1, max_occurs=1)
    value = Attribute('value', min_occurs=1, max_occurs=1)


@VO('ds:dataset.DataProductType')
class DataProductType(StringQuantity):
    pass


@VO('ds:dataset.CreationType')
class CreationType(StringQuantity):
    pass


@VO('ds:dataset.RightsType')
class RightsType(StringQuantity):
    pass


@VO('ds:dataset.SpectralBandType')
class SpectralBandType(StringQuantity):
    pass


@VO('ds:dataset.DataModel')
class DataModel(BaseType):
    name = Attribute('name', min_occurs=1, max_occurs=1)
    prefix = Attribute('prefix', min_occurs=0, max_occurs=1)
    u_r_l = Attribute('URL', min_occurs=0, max_occurs=1)


@VO('ds:dataset.DataID')
class DataID(BaseType):
    title = Attribute('title', min_occurs=1, max_occurs=1)
    dataset_i_d = Attribute('datasetID', min_occurs=0, max_occurs=1)
    creator_d_i_d = Attribute('creatorDID', min_occurs=0, max_occurs=1)
    version = Attribute('version', min_occurs=0, max_occurs=1)
    date = Attribute('date', min_occurs=0, max_occurs=1)
    creation_type = Attribute('creationType', min_occurs=0, max_occurs=1)
    creator = Composition('creator', min_occurs=0, max_occurs=1)
    contributor = Composition('contributor', min_occurs=0, max_occurs=-1)
    collection = Composition('collection', min_occurs=0, max_occurs=-1)


@VO('ds:dataset.Curation')
class Curation(BaseType):
    publisher_d_i_d = Attribute('publisherDID', min_occurs=0, max_occurs=1)
    version = Attribute('version', min_occurs=0, max_occurs=1)
    release_date = Attribute('releaseDate', min_occurs=0, max_occurs=1)
    rights = Attribute('rights', min_occurs=0, max_occurs=1)
    publisher = Composition('publisher', min_occurs=1, max_occurs=1)
    contact = Composition('contact', min_occurs=0, max_occurs=1)
    reference = Composition('reference', min_occurs=0, max_occurs=-1)


@VO('ds:party.Role')
class Role(BaseType):
    party = Reference('party', min_occurs=1, max_occurs=1)


@VO('ds:experiment.Facility')
class Facility(Role):
    pass


@VO('ds:dataset.Publisher')
class Publisher(Role):
    publisher_i_d = Attribute('publisherID', min_occurs=0, max_occurs=1)


@VO('ds:dataset.Contact')
class Contact(Role):
    pass


@VO('ds:dataset.Creator')
class Creator(Role):
    pass


@VO('ds:dataset.Contributor')
class Contributor(Role):
    acknowledgment = Attribute('acknowledgment', min_occurs=1, max_occurs=1)


@VO('ds:dataset.Publication')
class Publication(BaseType):
    ref_code = Attribute('refCode', min_occurs=1, max_occurs=1)


@VO('ds:dataset.Collection')
class Collection(BaseType):
    name = Attribute('name', min_occurs=1, max_occurs=1)


@VO('ds:party.Party')
class Party(BaseType):
    name = Attribute('name', min_occurs=1, max_occurs=1)


@VO('ds:party.Individual')
class Individual(Party):
    address = Attribute('address', min_occurs=0, max_occurs=1)
    phone = Attribute('phone', min_occurs=0, max_occurs=1)
    email = Attribute('email', min_occurs=0, max_occurs=1)


@VO('ds:party.Organization')
class Organization(Party):
    address = Attribute('address', min_occurs=0, max_occurs=1)
    phone = Attribute('phone', min_occurs=0, max_occurs=1)
    email = Attribute('email', min_occurs=0, max_occurs=1)
    logo = Attribute('logo', min_occurs=0, max_occurs=1)
