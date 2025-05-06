import logging
from fastapi import APIRouter, HTTPException
from fastapi import Query

router = APIRouter()

@router.get("/logout")
async def logout(force_error: bool = Query(False, description="Force error for testing purposes")):
    try:
        if force_error:
            # This branch is for testing exception handling
            raise Exception("Forced error")
        return {"message": "Logout successful"}
    except Exception as e:
        logging.error(e, exc_info=True)
        raise HTTPException(status_code=500, detail="An error occurred while logging out")
