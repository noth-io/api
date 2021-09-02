from sqlalchemy.orm import Session
from app import models, schemas
from fastapi import Depends, FastAPI, HTTPException
import math, random
from datetime import datetime, timedelta

def generateOTP() :
    digits = "0123456789"
    OTP = ""
    for i in range(6) :
        OTP += digits[math.floor(random.random() * 10)]
    return OTP

def is_valid_otp(db: Session, code: int, user_id: int, lifetime: int):
    db_otp = db.query(models.OTP).filter(models.OTP.user_id == user_id).order_by(models.OTP.created_at.desc()).first()
    if not db_otp or db_otp.code != code:
        raise HTTPException(status_code=400, detail="Invalid OTP code")
    if db_otp.created_at < datetime.now() - timedelta(seconds=int(lifetime)):
        raise HTTPException(status_code=400, detail="Expired OTP code")
    return True

def create_otp(db: Session, user_id: int) -> int:
    code = generateOTP()
    db_otp = models.OTP(code=code, user_id=user_id)
    db.add(db_otp)
    db.commit()
    return code

