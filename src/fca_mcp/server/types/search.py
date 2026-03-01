"""Reflections of FCA api fund types"""

import fca_api.types.search as fca_search_types

from . import base


class FirmSearchResult(base.reflect_fca_api_t(fca_search_types.FirmSearchResult)):
    """Reflected FirmSearchResult model with conversion support"""