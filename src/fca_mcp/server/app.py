import dataclasses

import fca_api


@dataclasses.dataclass(slots=True)
class FcaApp:
    fca_api: fca_api.async_api.Client
