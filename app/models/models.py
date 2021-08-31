from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Unicode, DateTime, LargeBinary
from app.db.base_class import Base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func


class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True, nullable=False)
    email = Column(String, unique=True, nullable=False)
    firstname = Column(String, nullable=False)
    lastname = Column(String, nullable=False)
    phone = Column(Unicode(255), unique=True, nullable=False)
    is_confirmed = Column(Boolean, nullable=False, default=False)
    is_admin = Column(Boolean, nullable=False, default=False)
    created_at = Column(DateTime, nullable=False, default=func.now())

    fido2credential = relationship("Fido2Credential", back_populates="user")

class Fido2Credential(Base):
    __tablename__ = 'fido2credential'

    id = Column(Integer, primary_key=True)
    attestation = Column(LargeBinary, unique=True, nullable=False)
    user_id = Column(Integer, ForeignKey('user.id'))
    is_enabled = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime, nullable=False, default=func.now())

    user = relationship("User", back_populates="fido2credential")
