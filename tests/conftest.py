import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy import delete

from app.database import PredictionModel
from app.main import app


@pytest_asyncio.fixture()
async def started_app():
    async with app.router.lifespan_context(app):
        yield app


@pytest_asyncio.fixture
async def client(started_app):
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        yield client


@pytest_asyncio.fixture
async def db(started_app):
    async with app.state.session_maker() as session:
        yield session


@pytest_asyncio.fixture(autouse=True)
async def clean_db(db):
    yield

    await db.execute(delete(PredictionModel))
    await db.commit()
