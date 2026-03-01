"""Reflections of FCA api firm types"""

import fca_api.types.firm as fca_firm_types

from . import base


class FirmDetails(base.reflect_fca_api_t(fca_firm_types.FirmDetails)):
    """Reflected FirmDetails model with conversion support"""


FirmNameAlias = base.reflect_fca_api_t(fca_firm_types.FirmNameAlias)
FirmAddress = base.reflect_fca_api_t(fca_firm_types.FirmAddress)
FirmControlledFunction = base.reflect_fca_api_t(fca_firm_types.FirmControlledFunction)
FirmIndividual = base.reflect_fca_api_t(fca_firm_types.FirmIndividual)
FirmPermission = base.reflect_fca_api_t(fca_firm_types.FirmPermission)
FirmRequirement = base.reflect_fca_api_t(fca_firm_types.FirmRequirement)
FirmRequirementInvestmentType = base.reflect_fca_api_t(fca_firm_types.FirmRequirementInvestmentType)
FirmRegulator = base.reflect_fca_api_t(fca_firm_types.FirmRegulator)
FirmPassport = base.reflect_fca_api_t(fca_firm_types.FirmPassport)
FirmPassportPermission = base.reflect_fca_api_t(fca_firm_types.FirmPassportPermission)
FirmWaiver = base.reflect_fca_api_t(fca_firm_types.FirmWaiver)
