from app.routes import api_router_v1
from fastapi import FastAPI

from app.api.utils.notification import init_fcm
from .engine import create_db_and_tables
from fastapi.responses import UJSONResponse
from fastapi.middleware.cors import CORSMiddleware

from fastapi.exceptions import RequestValidationError

from .exception_handlers import validation_exception_handler, http_exception_handler

from fastapi import status, HTTPException
from app.api.common.models import ResponseModel

import os


def get_app() -> FastAPI:
    """

    Get FastAPI application.

    This is the main constructor of an application.

    :return: application.
    """
    app = FastAPI()

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.on_event("startup")
    def startup():
        # create_db_and_tables()
        init_fcm()
        

    # @app.on_event("shutdown")
    # async def shutdown():
    #     os.remove('....sql_app.db')

    #create and mount version 1 of soberpal API
    appv1 = FastAPI(
        title="Hackathon Project",
        description="GenZ Hackathon API",
        docs_url="/docs",
        version="1.0",
        redoc_url="/redoc",
        openapi_url="/open.json",
        default_response_class=UJSONResponse,
        responses={
            422:
            ResponseModel.example(
                status=False,
                description='Validation error: Invalid request',
                message=
                'Error: Title field required, Error: Image field required',
                data={
                    "title": ["field required"],
                    "image": ["field required"]
                },
            ),
        },
    )

    @appv1.exception_handler(RequestValidationError)
    async def custom_validation_exception_handler(request, exc):
        return await validation_exception_handler(request, exc)

    @appv1.exception_handler(HTTPException)
    async def custom_http_exception_handler(request, exc):
        return await http_exception_handler(request, exc)

    appv1.include_router(router=api_router_v1)
    app.mount("/api/v1", appv1)

    # #create and mount version 2 of soberpal API
    # appv2 = FastAPI(title="Soberpal Project V2",
    #                 description="Soberpal API V2",
    #                 version="2.0",
    #                 docs_url="/docs/",
    #                 redoc_url="/redoc/",
    #                 openapi_url="/open.json",
    #                 default_response_class=UJSONResponse
    #             )

    # appv2.include_router(router=api_router_v2)
    # app.mount("/api/v2", appv2)

    return app
