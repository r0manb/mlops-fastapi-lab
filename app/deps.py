from typing import Annotated

from fastapi import Request, Depends
from sqlalchemy.ext.asyncio import AsyncSession


async def get_session(request: Request):
    session_maker = request.app.state.session_maker

    async with session_maker() as session:
        yield session


SessionDep = Annotated[AsyncSession, Depends(get_session)]
