from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Unicode, DateTime, LargeBinary
from db.base_class import Base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func


class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True, nullable=False)
    firstname = Column(String, nullable=False)
    lastname = Column(String, nullable=False)
    phone = Column(Unicode(255), unique=True, nullable=False)
    is_phone_confirmed = Column(Boolean, nullable=False, default=False)
    is_admin = Column(Boolean, nullable=False, default=False)
    created_at = Column(DateTime, nullable=False, default=func.now())

    fido2credential = relationship("Fido2Credential", back_populates="user")
    otp = relationship("OTP", back_populates="user")