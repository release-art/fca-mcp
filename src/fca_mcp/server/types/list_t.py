from __future__ import annotations

import typing

import pydantic

ModelT = typing.TypeVar("ModelT", bound=pydantic.BaseModel)


class PaginatedList(pydantic.BaseModel, typing.Generic[ModelT]):
    items: typing.Annotated[typing.List[ModelT], pydantic.Field()]
    has_next: typing.Annotated[
        bool,
        pydantic.Field(
            default=False,
            description="Whether there are more items to fetch beyond the ones listed in `items`",
        ),
    ]
    start_index: typing.Annotated[
        int,
        pydantic.Field(
            description="The index of the first item in `items` within the full list of items that could be returned by the API",
        ),
    ]
