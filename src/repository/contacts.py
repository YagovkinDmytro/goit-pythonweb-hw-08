from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from sqlalchemy import extract, or_, and_
from datetime import datetime, timedelta
from src.database.models import Contact
from src.schemas import ContactCreateModel, ContactPutModel, ContactPatchModel

class ContactRepository:
    def __init__(self, session: AsyncSession):
        self.db = session

    async def create_contact(self, body: ContactCreateModel) -> Contact:
        contact = Contact(**body.model_dump(exclude_unset=True))
        self.db.add(contact)
        await self.db.commit()
        await self.db.refresh(contact)
        return contact


    async def get_contacts(self, skip: int, limit: int, name: Optional[str] = None,
    surname: Optional[str] = None, email: Optional[str] = None) -> List[Contact]:
        stmt = select(Contact)
        if name:
            stmt = stmt.where(Contact.name.ilike(f"%{name}%"))
        if surname:
            stmt = stmt.where(Contact.surname.ilike(f"%{surname}%"))
        if email:
            stmt = stmt.where(Contact.email.ilike(f"%{email}%"))
        stmt = stmt.offset(skip).limit(limit)
        result = await self.db.execute(stmt)
        return result.scalars().all()
    

    async def get_contacts_for_birthdays(self, days_limit: int = 7) -> List[Contact]:
        today = datetime.today().date()
        end_date = today + timedelta(days=days_limit)
        start_month, start_day = today.month, today.day
        end_month, end_day = end_date.month, end_date.day
        stmt = select(Contact)
        if start_month == end_month:
            stmt = stmt.where(
                extract('month', Contact.birth_date) == start_month,
                extract('day', Contact.birth_date).between(start_day, end_day)
            )
        else:
            stmt = stmt.where(
                or_(
                    (
                        (extract('month', Contact.birth_date) == start_month) &
                        (extract('day', Contact.birth_date) >= start_day)
                    ),
                    (
                        (extract('month', Contact.birth_date) == end_month) &
                        (extract('day', Contact.birth_date) <= end_day)
                    )
                )
            )
        result = await self.db.execute(stmt)
        return result.scalars().all()


    async def get_contact_by_id(self, contact_id: int) -> Contact | None:
        stmt = select(Contact).where(Contact.id == contact_id)
        contact = await self.db.execute(stmt)
        return contact.scalar_one_or_none()
    
    async def put_contact(self, contact_id: int, body: ContactPutModel) -> Contact | None:
        contact = await self.get_contact_by_id(contact_id)
        if contact:
            for key, value in body.model_dump().items():
                setattr(contact, key, value)
            await self.db.commit()
            await self.db.refresh(contact)
        return contact

    async def patch_contact(self, contact_id: int, body: ContactPatchModel) -> Contact | None:
        contact = await self.get_contact_by_id(contact_id)
        if contact:
            for key, value in body.model_dump(exclude_unset=True).items():
                setattr(contact, key, value)
            await self.db.commit()
            await self.db.refresh(contact)
        return contact

    async def delete_contact(self, contact_id: int) -> Contact | None:
        contact = await self.get_contact_by_id(contact_id)
        if contact:
            await self.db.delete(contact)
            await self.db.commit()
        return contact
