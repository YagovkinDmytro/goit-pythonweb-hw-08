from sqlalchemy.ext.asyncio import AsyncSession

from src.repository.contacts import ContactRepository
from src.schemas import ContactCreateModel, ContactPutModel, ContactPatchModel

class ContactService:
    def __init__(self, db: AsyncSession):
        self.repository = ContactRepository(db)

    async def create_contact(self, body: ContactCreateModel):
        return await self.repository.create_contact(body)

    async def get_contacts(self, skip: int, limit: int, name: str, surname: str, email: str):
        return await self.repository.get_contacts(skip, limit, name, surname, email)
    
    async def get_contacts_upcoming_birthdays(self):
        return await self.repository.get_contacts_for_birthdays()

    async def get_contact(self, contact_id: int):
        return await self.repository.get_contact_by_id(contact_id)

    async def put_contact(self, contact_id: int, body: ContactPutModel):
        return await self.repository.put_contact(contact_id, body)
    
    async def patch_contact(self, contact_id: int, body: ContactPatchModel):
        return await self.repository.patch_contact(contact_id, body)

    async def delete_contact(self, contact_id: int):
        return await self.repository.delete_contact(contact_id)