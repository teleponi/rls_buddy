from database import Base
from enums import Role
from sqlalchemy import CheckConstraint, Column
from sqlalchemy import Enum as SQLAEnum
from sqlalchemy import Integer, String, UniqueConstraint


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    role = Column(SQLAEnum(Role), nullable=False)

    __table_args__ = (UniqueConstraint("email", name="unique_email"),)
