from typing import TYPE_CHECKING
from sqlalchemy.orm import DeclarativeBase,declarative_base


class Base(DeclarativeBase):
    abstract = True
    