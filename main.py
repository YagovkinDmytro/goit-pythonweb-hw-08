from datetime import date
from typing import Optional
from fastapi import FastAPI, Depends, HTTPException, status, Query, Path
from pydantic import BaseModel, Field, EmailStr
from sqlalchemy import text, extract, or_, and_
from sqlalchemy.orm import Session
from datetime import datetime, timedelta


from db import get_db, Contact

app = FastAPI()


@app.get("/api/healthchecker")
def healthchecker(db: Session = Depends(get_db)):
    try:
        # Make request
        result = db.execute(text("SELECT 1")).fetchone()
        if result is None:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database is not configured correctly",
            )
        return {"message": "Welcome to FastAPI!"}
    except Exception as e:
        print(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error connecting to the database",
        )


class ContactCreateModel(BaseModel):
    name: str = Field(..., min_length=1, max_length=50, example="John")
    surname: str = Field(..., min_length=1, max_length=50, example="Doe")
    email: EmailStr = Field(..., example="john.doe@example.com")
    phone: str = Field(..., min_length=7, max_length=50, example="+00123456789")
    birth_date: date = Field(..., example="1990-01-31")
    extra_info: Optional[str] = Field(None, max_length=255, example="Some additional info")


@app.post("/contacts", response_model=ContactCreateModel)
async def create_contact(contact: ContactCreateModel, db: Session = Depends(get_db)):
    contact_data = contact.model_dump(exclude_unset=True)
    new_contact = Contact(**contact_data)
    db.add(new_contact)
    db.commit()
    db.refresh(new_contact)
    return new_contact


class ContactResponseModel(BaseModel):
    id: int
    name: str
    surname: str
    email: EmailStr
    phone: str
    birth_date: date
    extra_info: Optional[str]


@app.get("/contacts")
async def read_contacts(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    name: Optional[str] = Query(None),
    surname: Optional[str] = Query(None),
    email: Optional[str] = Query(None),
    db: Session = Depends(get_db),
) -> list[ContactResponseModel]:
    query = db.query(Contact)
    if name:
        query = query.filter(Contact.name.ilike(f"%{name}%"))
    if surname:
        query = query.filter(Contact.surname.ilike(f"%{surname}%"))
    if email:
        query = query.filter(Contact.email.ilike(f"%{email}%"))
    contacts = query.offset(skip).limit(limit).all()
    return contacts


@app.get("/contacts")
async def read_contacts(
    skip: int = 0,
    limit: int = Query(default=10, ge=10, le=100),
    db: Session = Depends(get_db),
) -> list[ContactResponseModel]:
    contacts = db.query(Contact).offset(skip).limit(limit).all()
    return contacts


@app.get("/contacts/{contact_id}", response_model=ContactResponseModel)
async def read_contact(
    contact_id: int = Path(description="The ID of the contact to get", ge=0),
    db: Session = Depends(get_db),
):
    contact = db.query(Contact).filter(Contact.id == contact_id).first()
    if not contact:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")
    return contact


class ContactPutModel(BaseModel):
    id: int = Field(...)
    name: str = Field(..., min_length=1, max_length=50, example="John")
    surname: str = Field(..., min_length=1, max_length=50, example="Doe")
    email: EmailStr = Field(..., example="john.doe@example.com")
    phone: str = Field(..., min_length=7, max_length=50, example="+00123456789")
    birth_date: date = Field(..., example="1990-01-31")
    extra_info: Optional[str] = Field(None, max_length=255, example="Some additional info")


@app.put("/contacts/{contact_id}", response_model=ContactPutModel)
async def update_contact(
    contact_data: ContactPutModel,
    contact_id: int = Path(description="The ID of the contact to put", ge=0),
    db: Session = Depends(get_db),
):
    contact = db.query(Contact).filter(Contact.id == contact_id).first()
    if not contact:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")
    contact_data = contact_data.model_dump()
    for field, value in contact_data.items():
        setattr(contact, field, value)
    db.commit()
    db.refresh(contact)
    return contact


class ContactPatchModel(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=50, example="John")
    surname: Optional[str] = Field(None, min_length=1, max_length=50, example="Doe")
    email: Optional[EmailStr] = Field(None, example="john.doe@example.com")
    phone: Optional[str] = Field(None, min_length=7, max_length=50, example="+00123456789")
    birth_date: Optional[date] = Field(None, example="1990-01-31")
    extra_info: Optional[str] = Field(None, max_length=255, example="Some additional info")


@app.patch("/contacts/{contact_id}", response_model=ContactPatchModel)
async def update_contact(
    contact_data: ContactPatchModel,
    contact_id: int = Path(description="The ID of the contact to patch", ge=0),
    db: Session = Depends(get_db),
):
    contact = db.query(Contact).filter(Contact.id == contact_id).first()
    if not contact:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")
    contact_data = contact_data.model_dump(exclude_unset=True)
    for field, value in contact_data.items():
        setattr(contact, field, value)
    db.commit()
    db.refresh(contact)
    return contact


@app.delete("/contacts/{contact_id}" , status_code=status.HTTP_204_NO_CONTENT)
async def delete_contact(
    contact_id: int = Path(description="The ID of the contact to delete", ge=0),
    db: Session = Depends(get_db),
):
    contact = db.query(Contact).filter(Contact.id == contact_id).first()
    if not contact:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")
    db.delete(contact)
    db.commit()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)