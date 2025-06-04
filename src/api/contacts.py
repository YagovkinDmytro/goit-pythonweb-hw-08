from datetime import date
from typing import List
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status, Query, Path
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.db import get_db
from src.schemas import ContactCreateModel, ContactResponseModel, ContactBirthdayResponseModel, ContactPutModel, ContactPatchModel
from src.services.contacts import ContactService


router = APIRouter(prefix="/contacts", tags=["contacts"])


@router.post("/", response_model=ContactCreateModel, status_code=status.HTTP_201_CREATED)
async def create_contact(body: ContactCreateModel, db: AsyncSession = Depends(get_db)):
    contact_service = ContactService(db)
    return await contact_service.create_contact(body)


@router.get("/", response_model=List[ContactResponseModel])
async def read_contacts(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    name: Optional[str] = Query(None),
    surname: Optional[str] = Query(None),
    email: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
):
    contact_service = ContactService(db)
    contacts = await contact_service.get_contacts(skip, limit, name, surname, email)
    return contacts


@router.get("/birthdays", response_model=List[ContactBirthdayResponseModel])
async def get_upcoming_birthdays(db: AsyncSession = Depends(get_db)):
    contact_service = ContactService(db)
    contacts = await contact_service.get_contacts_upcoming_birthdays()
    return contacts


@router.get("/{contact_id}", response_model=ContactResponseModel)
async def read_contact(
    contact_id: int = Path(description="The ID of the contact to get", ge=0),
    db: AsyncSession = Depends(get_db),
):
    contact_service = ContactService(db)
    contact = await contact_service.get_contact(contact_id)
    if not contact:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")
    return contact


@router.put("/{contact_id}", response_model=ContactPutModel)
async def update_contact(
    body: ContactPutModel,
    contact_id: int = Path(description="The ID of the contact to put", ge=0),
    db: AsyncSession = Depends(get_db),
):
    contact_service = ContactService(db)
    contact = await contact_service.put_contact(contact_id, body)
    if not contact:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")
    return contact


@router.patch("/{contact_id}", response_model=ContactPatchModel)
async def update_contact(
    body: ContactPatchModel,
    contact_id: int = Path(description="The ID of the contact to patch", ge=0),
    db: AsyncSession = Depends(get_db),
):
    contact_service = ContactService(db)
    contact = await contact_service.patch_contact(contact_id, body)
    if not contact:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")
    return contact


@router.delete("/{contact_id}" , status_code=status.HTTP_204_NO_CONTENT)
async def delete_contact(
    contact_id: int = Path(description="The ID of the contact to delete", ge=0),
    db: AsyncSession = Depends(get_db),
):
    contact_service = ContactService(db)
    contact = await contact_service.delete_contact(contact_id)
    if not contact:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")
    return contact


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(router, host="127.0.0.1", port=8000)