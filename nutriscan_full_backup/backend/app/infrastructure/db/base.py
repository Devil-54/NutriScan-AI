"""
Shared declarative base. Every model in app/infrastructure/db/models/
inherits from this so Alembic's autogenerate can discover them all via a
single `Base.metadata`.
"""
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass
