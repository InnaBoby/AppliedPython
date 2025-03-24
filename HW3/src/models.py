from datetime import datetime
from typing import List
from sqlalchemy import Integer, ForeignKey, UUID
from fastapi_users.db import SQLAlchemyBaseUserTable
from sqlalchemy.orm import declarative_base, Mapped, mapped_column, relationship

Base = declarative_base()


# class User(SQLAlchemyBaseUserTable[int], Base):
#     __tablename__ = "user"
#
#     id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
#     email: Mapped[str] = mapped_column(nullable=False)
#     name: Mapped[str]
#     hashed_password: Mapped[str] = mapped_column(nullable=False)
#     registered_at: Mapped[datetime] = mapped_column(default=datetime.now())
#     links: Mapped[List['Links']]=relationship(back_populates='user')
#     # is_active: Mapped[bool] = mapped_column(default=True, nullable=False)
#     # is_superuser: Mapped[bool] = mapped_column(default=True, nullable=False)
#     # is_verified: Mapped[bool] = mapped_column(default=True, nullable=False)


# class Links(Base):
#     __tablename__ = 'links'
#
#     id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
#     user_id: Mapped[UUID] = mapped_column(Integer, ForeignKey('users.id', ondelete='CASCADE'))
#     user: Mapped['User'] = relationship(back_populates='links')
#     link: Mapped[str] = mapped_column(nullable=False)
#     short_link: Mapped[str] = mapped_column(unique=True, nullable=False)
#     number_of_clics: Mapped[int]


