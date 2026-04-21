from __future__ import annotations

import logging

logger = logging.getLogger(__name__)

num_version = (0, 0, 0, "dev", 0)

cache_version = ".".join(str(x) for x in num_version[:2])

__version__ = ".".join(str(x) for x in num_version)
