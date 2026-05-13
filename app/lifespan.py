from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.config import get_config
from app.database import create_engine, create_session_maker


@asynccontextmanager
async def lifespan(app: FastAPI):
    config = get_config()

    engine = create_engine(config.database_url)
    session_maker = create_session_maker(engine)

    app.state.session_maker = session_maker

    try:
        yield
    finally:
        await engine.dispose()
