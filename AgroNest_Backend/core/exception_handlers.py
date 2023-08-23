from collections import defaultdict

from fastapi import status
from fastapp.api.responses import JSONResponse
from app.app.api.common.models import ResponseModel


async def validation_exception_handler(request, exc):
    reformatted_message = defaultdict(list)
    human_friendly_message = ''

    for pydantic_error in exc.errors():
        loc, msg = pydantic_error["loc"], pydantic_error["msg"]
        filtered_loc = loc[1:] if loc[0] in ("body", "query", "path") else loc
        field_string = ",".join(
            filtered_loc)  # nested fields with dot-notation
        reformatted_message[field_string].append(msg)

        human_friendly_message += f'Error: {field_string.title()} {msg}, '

    # Remove trailing comma
    human_friendly_message = human_friendly_message.rstrip(', ')

    return JSONResponse(
        status_code=422,
        content=ResponseModel.error(
            message=human_friendly_message,
            data=reformatted_message,
        ),
    )


async def http_exception_handler(request, exc):

    return JSONResponse(
        status_code=exc.status_code,
        content=ResponseModel.error(
            message=str(exc.detail),
            data=None,
        ),
    )
