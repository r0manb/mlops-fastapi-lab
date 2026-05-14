import datetime as dt

from sqlalchemy import DateTime, func
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class PredictionModel(Base):
    __tablename__ = "predictions"

    id: Mapped[int] = mapped_column(primary_key=True)
    age: Mapped[int]
    weight: Mapped[int]
    height: Mapped[int]
    exercise: Mapped[str]
    sleep: Mapped[float]
    sugar_intake: Mapped[str]
    smoking: Mapped[str]
    alcohol: Mapped[str]
    married: Mapped[str]
    profession: Mapped[str]
    bmi: Mapped[float]
    predict: Mapped[int]
    predict_proba: Mapped[float]
    created_at: Mapped[dt.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )


def create_engine(dsn: str):
    return create_async_engine(dsn)


def create_session_maker(engine):
    return async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
