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
from rama.framework import Attribute, Reference, Composition
from rama.models.ivoa import StringQuantity
from rama.registry import VO


@VO('ds:experiment.Observation')
class Observation:
    observation_i_d = Attribute('ds:experiment.Observation.observationID', min=1, max=1)
    obs_config = Composition('ds:experiment.Observation.obsConfig', min=1, max=1)
    result = Composition('ds:experiment.Observation.result', min=0, max=-1)
    target = Composition('ds:experiment.Observation.target', min=1, max=1)
    proposal = Composition('ds:experiment.Observation.proposal', min=0, max=1)


@VO('ds:experiment.ObsConfig')
class ObsConfig:
    bandpass = Attribute('ds:experiment.ObsConfig.bandpass', min=0, max=1)
    datasource = Attribute('ds:experiment.ObsConfig.datasource', min=0, max=1)
    facility = Composition('ds:experiment.ObsConfig.facility', min=0, max=1)
    instrument = Composition('ds:experiment.ObsConfig.instrument', min=0, max=1)


@VO('ds:experiment.BaseTarget')
class BaseTarget:
    name = Attribute('ds:experiment.BaseTarget.name', min=1, max=1)
    description = Attribute('ds:experiment.BaseTarget.description', min=0, max=1)
    position = Reference('ds:experiment.BaseTarget.position', min=0, max=1)


@VO('ds:experiment.Target')
class Target(BaseTarget):
    object_class = Attribute('ds:experiment.Target.objectClass', min=0, max=1)


@VO('ds:experiment.AstroTarget')
class AstroTarget(BaseTarget):
    object_class = Attribute('ds:experiment.AstroTarget.objectClass', min=0, max=1)
    spectral_class = Attribute('ds:experiment.AstroTarget.spectralClass', min=0, max=1)
    redshift = Attribute('ds:experiment.AstroTarget.redshift', min=0, max=1)
    var_ampl = Attribute('ds:experiment.AstroTarget.varAmpl', min=0, max=1)


@VO('ds:experiment.Instrument')
class Instrument:
    name = Attribute('ds:experiment.Instrument.name', min=1, max=1)


@VO('ds:experiment.Proposal')
class Proposal:
    identifier = Attribute('ds:experiment.Proposal.identifier', min=1, max=1)


@VO('ds:experiment.Derived')
class Derived:
    derived_element = Composition('ds:experiment.Derived.derivedElement', min=0, max=-1)


@VO('ds:dataset.Dataset')
class Dataset:
    data_product_type = Attribute('ds:dataset.Dataset.dataProductType', min=1, max=1)
    data_product_subtype = Attribute('ds:dataset.Dataset.dataProductSubtype', min=0, max=1)
    curation = Composition('ds:dataset.Dataset.curation', min=1, max=1)
    data_i_d = Composition('ds:dataset.Dataset.dataID', min=1, max=1)


@VO('ds:experiment.ObsDataset')
class ObsDataset(Dataset):
    calib_level = Attribute('ds:experiment.ObsDataset.calibLevel', min=0, max=1)
    derived = Composition('ds:experiment.ObsDataset.derived', min=0, max=1)
    target = Reference('ds:experiment.ObsDataset.target', min=1, max=1)
    proposal = Reference('ds:experiment.ObsDataset.proposal', min=0, max=1)
    obs_config = Reference('ds:experiment.ObsDataset.obsConfig', min=0, max=1)


@VO('ds:experiment.DerivedElement')
class DerivedElement:
    pass


@VO('ds:experiment.DerivedScalar')
class DerivedScalar(DerivedElement):
    name = Attribute('ds:experiment.DerivedScalar.name', min=1, max=1)
    value = Attribute('ds:experiment.DerivedScalar.value', min=1, max=1)


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
class DataModel:
    name = Attribute('ds:dataset.DataModel.name', min=1, max=1)
    prefix = Attribute('ds:dataset.DataModel.prefix', min=0, max=1)
    u_r_l = Attribute('ds:dataset.DataModel.URL', min=0, max=1)


@VO('ds:dataset.DataID')
class DataID:
    title = Attribute('ds:dataset.DataID.title', min=1, max=1)
    dataset_i_d = Attribute('ds:dataset.DataID.datasetID', min=0, max=1)
    creator_d_i_d = Attribute('ds:dataset.DataID.creatorDID', min=0, max=1)
    version = Attribute('ds:dataset.DataID.version', min=0, max=1)
    date = Attribute('ds:dataset.DataID.date', min=0, max=1)
    creation_type = Attribute('ds:dataset.DataID.creationType', min=0, max=1)
    creator = Composition('ds:dataset.DataID.creator', min=0, max=1)
    contributor = Composition('ds:dataset.DataID.contributor', min=0, max=-1)
    collection = Composition('ds:dataset.DataID.collection', min=0, max=-1)


@VO('ds:dataset.Curation')
class Curation:
    publisher_d_i_d = Attribute('ds:dataset.Curation.publisherDID', min=0, max=1)
    version = Attribute('ds:dataset.Curation.version', min=0, max=1)
    release_date = Attribute('ds:dataset.Curation.releaseDate', min=0, max=1)
    rights = Attribute('ds:dataset.Curation.rights', min=0, max=1)
    publisher = Composition('ds:dataset.Curation.publisher', min=1, max=1)
    contact = Composition('ds:dataset.Curation.contact', min=0, max=1)
    reference = Composition('ds:dataset.Curation.reference', min=0, max=-1)


@VO('ds:party.Role')
class Role:
    party = Reference('ds:party.Role.party', min=1, max=1)


@VO('ds:experiment.Facility')
class Facility(Role):
    pass


@VO('ds:dataset.Publisher')
class Publisher(Role):
    publisher_i_d = Attribute('ds:dataset.Publisher.publisherID', min=0, max=1)


@VO('ds:dataset.Contact')
class Contact(Role):
    pass


@VO('ds:dataset.Creator')
class Creator(Role):
    pass


@VO('ds:dataset.Contributor')
class Contributor(Role):
    acknowledgment = Attribute('ds:dataset.Contributor.acknowledgment', min=1, max=1)


@VO('ds:dataset.Publication')
class Publication:
    ref_code = Attribute('ds:dataset.Publication.refCode', min=1, max=1)


@VO('ds:dataset.Collection')
class Collection:
    name = Attribute('ds:dataset.Collection.name', min=1, max=1)


@VO('ds:party.Party')
class Party:
    name = Attribute('ds:party.Party.name', min=1, max=1)


@VO('ds:party.Individual')
class Individual(Party):
    address = Attribute('ds:party.Individual.address', min=0, max=1)
    phone = Attribute('ds:party.Individual.phone', min=0, max=1)
    email = Attribute('ds:party.Individual.email', min=0, max=1)


@VO('ds:party.Organization')
class Organization(Party):
    address = Attribute('ds:party.Organization.address', min=0, max=1)
    phone = Attribute('ds:party.Organization.phone', min=0, max=1)
    email = Attribute('ds:party.Organization.email', min=0, max=1)
    logo = Attribute('ds:party.Organization.logo', min=0, max=1)
