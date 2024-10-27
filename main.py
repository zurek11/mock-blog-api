import logging
from contextlib import asynccontextmanager

import sentry_sdk
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.logging import LoggingIntegration
from sqlmodel import SQLModel

from apps import version
from apps.api.errors import ProblemDetailException
from apps.core.session import engine
from config import settings

if settings.SENTRY_DSN:
    sentry_logging = LoggingIntegration(
        level=logging.WARNING,
        event_level=logging.ERROR
    )
    sentry_sdk.init(
        dsn=settings.SENTRY_DSN,
        environment=settings.SENTRY_ENVIRONMENT,
        integrations=[FastApiIntegration(), sentry_logging],
        traces_sample_rate=1.0,
        profiles_sample_rate=1.0,
        attach_stacktrace=True,
        include_source_context=True,
        include_local_variables=True,
        send_default_pii=True,
        max_request_body_size='always'
    )


@asynccontextmanager
async def app_lifespan(fastapi_app: FastAPI):
    await startup_event()
    yield
    await shutdown_event()


async def startup_event():
    SQLModel.metadata.create_all(engine)


async def shutdown_event():
    pass

app = FastAPI(
    lifespan=app_lifespan,
    debug=settings.DEBUG,
    title="Mock Blog API",
    description="""
    The ultimate testbed blog template where fun meets functionality! This lightweight project is built for
    experimenting with tools, integrations, and new ideas—no serious blogging here, just testing the waters. Dive in,
    play around, and make it your own!
    """,
    version=version.__version__,
    docs_url='/docs' if settings.DEBUG else None,
    openapi_url='/openapi.json' if settings.DEBUG else None,
    default_response_class=JSONResponse,
    servers=[
        {
            "url": settings.BASE_URL,
            "description": f"Ares v{version.__version__}"
        }
    ]
)

# Middlewares
app.add_middleware(
    middleware_class=CORSMiddleware,
    allow_origins=settings.ALLOWED_HOSTS.split(';'),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Exceptions
@app.exception_handler(ProblemDetailException)
async def problem_detail_exception_handler(exc: ProblemDetailException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail, "detail_type": exc.detail_type},
    )
