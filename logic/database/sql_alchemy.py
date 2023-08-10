import asyncio
import datetime
from typing import List
from sqlalchemy import MetaData, Table, select, String, Column, Integer, func, ForeignKey, Text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncAttrs
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship




DATABASE_URL = "sqlite+aiosqlite:///./auto_db"


class Base(AsyncAttrs, DeclarativeBase):
    pass


class Brands(Base):
    __tablename__ = "brand"

    id = Column(Integer, autoincrement=True, primary_key=True, index=True)
    unique = Column(String(64), unique=True)
    av = Column(String(64))
    abw = Column(String(64))
    onliner = Column(String(64))

    def __repr__(self) -> str:
        return f"Brands(id={self.id!r}, name={self.unique!r})"


class Model(Base):
    __tablename__ = "model"
    id = Column(Integer, autoincrement=True, primary_key=True, index=True)
    brands_id = Column(String(64), ForeignKey("brand.id"))
    unique = Column(String(64), unique=True)
    av = Column(String(64))
    abw = Column(String(64))
    onliner = Column(String(64))

    def __repr__(self) -> str:
        return f"Models(id={self.id!r}, name={self.unique!r})"


class User(Base):
    __tablename__ = "user"
    id = Column(Integer, autoincrement=True, primary_key=True, index=True)
    tel_id = Column(Integer, unique=True)
    email = Column(String(64), unique=True)
    vip = Column(Integer)

    def __repr__(self) -> str:
        return f"User(id={self.id!r}, email={self.email!r})"


class Filter(Base):
    __tablename__ = "filter"
    id = Column(Integer, autoincrement=True, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("user.id"))
    filter = Column(String(128), unique=True)
    active = Column(Integer)

    def __repr__(self) -> str:
        return f"Filter(id={self.id!r}, filter={self.filter!r}, active={self.filter!r})"


class Car(Base):
    __tablename__ = "car"
    id = Column(Integer, autoincrement=True, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("user.id"))
    url = Column(String(256))
    price = Column(Integer)
    data = Column(Text)

    def __repr__(self) -> str:
        return f"Car(id={self.id!r}, car={self.url!r}, active={self.price!r})"



async def create_tables() -> None:
    engine = create_async_engine(DATABASE_URL, echo=True)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    await engine.dispose()




    #     await conn.execute(
    #         Brands.insert(), [{"unique": "some name 1"}, {"unique": "some name 2"}]
    #     )
    #
    # async with engine.connect() as conn:
    #     # select a Result, which will be delivered with buffered
    #     # results
    #     result = await conn.execute(select(brands).where(brands.c.unique == "some name 1"))
    #
    #     print(result.fetchall())

    # for AsyncEngine created in function scope, close and
    # clean-up pooled connections


if __name__ == '__main__':
    # asyncio.run(create_tables())
    pass
