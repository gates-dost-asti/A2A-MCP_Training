from typing import Type, TypeVar

import requests
from pydantic import BaseModel
from openai.types.responses import Response
from openai.lib._pydantic import to_strict_json_schema

BASE_URL = "http://172.16.0.237:8004/v1"

T = TypeVar("T", bound=BaseModel)


def create_response(**kwargs) -> Response:
    # payload = {
    #     "kwargs": kwargs
    # }
    payload = kwargs
    response = requests.post(
        f"{BASE_URL}/responses",
        json=payload,
        timeout=120,
    )
    # print(response.status_code)
    # print(response.text)

    response.raise_for_status()

    return Response.model_validate(response.json())


def parse_response(
    *,
    text_format: Type[T],
    **kwargs,
) -> T:
    """
    Equivalent to OpenAI's responses.parse().
    """

    kwargs["text"] = {
        "format":{
            "type": "json_schema",
            "name": text_format.__name__,
            "schema": to_strict_json_schema(text_format),
        }
    }

    response = create_response(**kwargs)

    return text_format.model_validate_json(
        response.output_text
    )

def assign_route() -> str:
    return requests.get(f"{BASE_URL}/assignroute", timeout=120).json()