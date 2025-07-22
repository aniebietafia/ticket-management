from database import User, Ticket
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from schemas import TicketCreate, TicketUpdate
from typing import List, Optional

class TicketService:
    async def create_ticket(self, db: AsyncSession, ticket: TicketCreate, customer_id: str) -> Ticket:
        """Create a new ticket"""
        db_ticket = Ticket(
            **ticket.model_dump(),
            customer_id=customer_id
        )
        db.add(db_ticket)
        await db.commit()
        await db.refresh(db_ticket)
        return db_ticket

    async def get_ticket_by_customer(self, db: AsyncSession, customer_id: str) -> List[Ticket]:
        """Get tickets by customer ID"""
        result = await db.execute(select(Ticket).filter(Ticket.customer_id == customer_id))
        return result.scalars().all()

    async def get_tickets(self, db: AsyncSession, status: Optional[str] = None, agent_id: Optional[str] = None) -> List[Ticket]:
        """Get tickets with optional filters"""
        query = select(Ticket)
        if status:
            query = query.filter(Ticket.status == status)
        if agent_id:
            query = query.filter(Ticket.agent_id == agent_id)
        
        result = await db.execute(query)
        return result.scalars().all()

    async def get_ticket(self, db: AsyncSession, ticket_id: str) -> Optional[Ticket]:
        """Get ticket by ID"""
        result = await db.execute(select(Ticket).filter(Ticket.id == ticket_id))
        return result.scalar_one_or_none()

    async def update_ticket(self, db: AsyncSession, ticket_id: str, ticket_update: TicketUpdate) -> Optional[Ticket]:
        """Update ticket information"""
        db_ticket = await self.get_ticket(db, ticket_id)
        if not db_ticket:
            return None

        for field, value in ticket_update.model_dump(exclude_unset=True).items():
            setattr(db_ticket, field, value)
        await db.commit()
        await db.refresh(db_ticket)
        return db_ticket

    async def assign_ticket(self, db: AsyncSession, ticket_id: str, agent_id: str) -> Optional[Ticket]:
        """Assign ticket to an agent"""
        db_ticket = await self.get_ticket(db, ticket_id)
        if not db_ticket:
            return None

        db_ticket.agent_id = agent_id
        await db.commit()
        await db.refresh(db_ticket)
        return db_ticket


ticket_service = TicketService()
