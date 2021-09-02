from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Unicode, DateTime, LargeBinary
from app.db.base_class import Base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

class OTP(Base):
    __tablename__ = 'otp'

    id = Column(Integer, primary_key=True)
    code = Column(Integer, nullable=False)
    user_id = Column(Integer, ForeignKey('user.id'))
    created_at = Column(DateTime, nullable=False, default=func.now())

    user = relationship("User", back_populates="otp")
