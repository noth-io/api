from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from db.base_class import Base
from db.session import SessionLocal, engine
from api.v1.api import api_router
from core.config import settings

Base.metadata.create_all(bind=engine)

app = FastAPI(
    #title=settings.PROJECT_NAME, openapi_url=f"{settings.API_V1_STR}/openapi.json"
    title="Noth API"
)

# Set all CORS enabled origins
if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

app.include_router(api_router, prefix="/v1")