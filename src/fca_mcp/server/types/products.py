"""Reflections of FCA api fund types"""

import fca_api.types.products as fca_product_types
import pydantic

from . import base


class ProductDetails(base.reflect_fca_api_t(fca_product_types.ProductDetails)):
    """Reflected ProductDetails model with conversion support"""
