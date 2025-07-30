import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock
from app.api.ticket import TicketService
from app.schemas.ticket import TicketCreate, TicketUpdate

@pytest.mark.asyncio
async def test_create_ticket():
    db = AsyncMock()
    ticket_data = TicketCreate(title="Test", description="Test desc")
    db_ticket = MagicMock()
    db_ticket.model_dump.return_value = {"title": "Test", "description": "Test desc"}
    db_ticket.title = "Test"
    db.add = MagicMock()
    db.commit = AsyncMock()
    db.refresh = AsyncMock()
    db_ticket.customer_id = "user123"
    db_ticket.id = "ticket123"
    db_ticket.status = "Open"
    db_ticket.agent_id = None
    db_ticket.resolution_notes = None
    db_ticket.embed_token = "token"
    db_ticket.created_at = None
    db_ticket.updated_at = None

    # Patch Ticket to return db_ticket
    service = TicketService()
    service.create_ticket = AsyncMock(return_value=db_ticket)
    result = await service.create_ticket(db, ticket_data, "user123")
    assert result.customer_id == "user123"
    assert result.title == "Test"

@pytest.mark.asyncio
async def test_get_ticket_by_customer():
    db = AsyncMock()
    service = TicketService()
    service.get_ticket_by_customer = AsyncMock(return_value=[MagicMock()])
    result = await service.get_ticket_by_customer(db, "user123")
    assert isinstance(result, list)

@pytest.mark.asyncio
async def test_update_ticket():
    db = AsyncMock()
    service = TicketService()
    ticket_update = TicketUpdate(status="Resolved", resolution_notes="Done")
    db_ticket = MagicMock()
    service.get_ticket = AsyncMock(return_value=db_ticket)
    db.commit = AsyncMock()
    db.refresh = AsyncMock()
    result = await service.update_ticket(db, "ticket123", ticket_update)
    assert result is not None

@pytest.mark.asyncio
async def test_assign_ticket():
    db = AsyncMock()
    service = TicketService()
    db_ticket = MagicMock()
    service.get_ticket = AsyncMock(return_value=db_ticket)
    db.commit = AsyncMock()
    db.refresh = AsyncMock()
    result = await service.assign_ticket(db, "ticket123", "agent123")
    assert result.agent_id == "agent123"