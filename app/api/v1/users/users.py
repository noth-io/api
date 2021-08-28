from fastapi import APIRouter, Body, Depends, HTTPException

router = APIRouter()

@router.get("/")
async def root():
    return {"message": "Hello World"}