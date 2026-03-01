"""Reflections of FCA api firm types"""

import fca_api.types.firm as fca_firm_types

from . import base


class FirmDetails(base.reflect_fca_api_t(fca_firm_types.FirmDetails)):
    """Reflected FirmDetails model with conversion support"""


class FirmNameAlias(base.reflect_fca_api_t(fca_firm_types.FirmNameAlias)):
    """Reflected FirmNameAlias model with conversion support"""


class FirmAddress(base.reflect_fca_api_t(fca_firm_types.FirmAddress)):
    """Reflected FirmAddress model with conversion support"""


class FirmControlledFunction(base.reflect_fca_api_t(fca_firm_types.FirmControlledFunction)):
    """Reflected FirmControlledFunction model with conversion support"""


class FirmIndividual(base.reflect_fca_api_t(fca_firm_types.FirmIndividual)):
    """Reflected FirmIndividual model with conversion support"""


class FirmPermission(base.reflect_fca_api_t(fca_firm_types.FirmPermission)):
    """Reflected FirmPermission model with conversion support"""


class FirmRequirement(base.reflect_fca_api_t(fca_firm_types.FirmRequirement)):
    """Reflected FirmRequirement model with conversion support"""


class FirmRequirementInvestmentType(base.reflect_fca_api_t(fca_firm_types.FirmRequirementInvestmentType)):
    """Reflected FirmRequirementInvestmentType model with conversion support"""


class FirmRegulator(base.reflect_fca_api_t(fca_firm_types.FirmRegulator)):
    """Reflected FirmRegulator model with conversion support"""


class FirmPassport(base.reflect_fca_api_t(fca_firm_types.FirmPassport)):
    """Reflected FirmPassport model with conversion support"""


class FirmPassportPermission(base.reflect_fca_api_t(fca_firm_types.FirmPassportPermission)):
    """Reflected FirmPassportPermission model with conversion support"""


class FirmWaiver(base.reflect_fca_api_t(fca_firm_types.FirmWaiver)):
    """Reflected FirmWaiver model with conversion support"""
