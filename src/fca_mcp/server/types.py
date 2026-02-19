from __future__ import annotations

import typing

import fca_api
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
    fields = {}
    for name, field in model_cls.model_fields.items():
        # Remove fields whose annotation is pydantic.HttpUrl
        if field.annotation is pydantic.HttpUrl:
            continue
        # Handle required and default values
        if field.default is pydantic.fields.PydanticUndefined:
            fields[name] = (field.annotation, ...)
        else:
            fields[name] = (field.annotation, field.default)
    return pydantic.create_model(
        f"{model_cls.__name__}WithoutHttpUrl",
        **fields,
        __base__=pydantic.BaseModel,
    )


CleanFirmDetails = remove_httpurl_fields(fca_api.types.firm.FirmDetails)
