import typing

import pydantic

ModelT = typing.TypeVar("ModelT", bound=pydantic.BaseModel)


class PaginatedList(pydantic.BaseModel, typing.Generic[ModelT]):
    items: typing.List[ModelT]
