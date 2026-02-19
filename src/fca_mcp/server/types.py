from __future__ import annotations

import typing

import pydantic

ModelT = typing.TypeVar("ModelT", bound=pydantic.BaseModel)


class PaginatedList(pydantic.BaseModel, typing.Generic[ModelT]):
    items: typing.List[ModelT]
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


def remove_httpurl_fields(model_cls: typing.Type[pydantic.BaseModel]) -> typing.Type[pydantic.BaseModel]:
    """
    Dynamically creates a new Pydantic model class with all fields from the input model,
    except those whose type is pydantic.HttpUrl.
    """
    fields = {
        name: (field.outer_type_, field.field_info)
        for name, field in model_cls.model_fields.items()
        if field.annotation is not pydantic.HttpUrl and field.outer_type_ is not pydantic.HttpUrl
    }
    return pydantic.create_model(
        f"{model_cls.__name__}WithoutHttpUrl",
        **fields,
        __base__=pydantic.BaseModel,
    )
