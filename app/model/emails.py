import json
from typing import Optional, List, Type
import inspect
from fastapi import Form
from pydantic import BaseModel


def as_form(cls: Type[BaseModel]):
    params = []
    for attr_field_name, model_attr_field in cls.__fields__.items():
        model_attr_field: ModelField  # type: ignore

        if not model_attr_field.required:
            params.append(
                inspect.Parameter(
                    model_attr_field.alias,
                    inspect.Parameter.POSITIONAL_ONLY,
                    default=Form(model_attr_field.default),
                    annotation=model_attr_field.outer_type_,
                )
            )
        else:
            params.append(
                inspect.Parameter(
                    model_attr_field.alias,
                    inspect.Parameter.POSITIONAL_ONLY,
                    default=Form(...),
                    annotation=model_attr_field.outer_type_,
                )
            )

    async def as_form_func(**data):
        return cls(**data)

    sig = inspect.signature(as_form_func)
    sig = sig.replace(parameters=params)
    as_form_func.__signature__ = sig  # type: ignore
    setattr(cls, 'as_form', as_form_func)
    return cls


@as_form
class EmailRequest(BaseModel):
    sender: str = Form(...)
    sender_name: str = Form(None)
    recipient: Optional[List[str]] = []
    cc: Optional[List[str]] = []
    bcc: Optional[List[str]] = []
    subject: str = Form(...)
    text: str = Form(None)
    body: str = Form(None)

    class Config:
        orm_mode = True

    @classmethod
    def __get_validators__(cls):
        yield cls.validate_to_json

    @classmethod
    def validate_to_json(cls, value):
        if isinstance(value, str):
            return cls(**json.loads(value))
        return value


