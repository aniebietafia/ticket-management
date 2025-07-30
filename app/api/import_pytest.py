import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from app.api.ticket import TicketService
from app.schemas.ticket import TicketCreate, TicketUpdate

@pytest.mark.asyncio
async def test_create_ticket():
    db = AsyncMock()
    ticket_data = MagicMock(spec=TicketCreate)
    ticket_data.model_dump.return_value = {"title": "Test", "description": "Test desc"}
    mock_ticket = MagicMock()
    with patch("app.api.ticket.Ticket", return_value=mock_ticket):
        service = TicketService()
        result = await service.create_ticket(db, ticket_data, "customer123")
    db.add.assert_called_once_with(mock_ticket)
    assert result == mock_ticket

@pytest.mark.asyncio
async def test_get_ticket_by_customer():
    db = AsyncMock()
    mock_result = AsyncMock()
    mock_scalars = MagicMock()
    mock_scalars.all.return_value = ["ticket1", "ticket2"]
    mock_result.scalars.return_value = mock_scalars
    db.execute.return_value = mock_result
    service = TicketService()
    with patch("app.api.ticket.Ticket"):
        tickets = await service.get_ticket_by_customer(db, "customer123")
    assert tickets == ["ticket1", "ticket2"]

@pytest.mark.asyncio
async def test_get_tickets():
    db = AsyncMock()
    mock_result = AsyncMock()
    mock_scalars = MagicMock()
    mock_scalars.all.return_value = ["ticketA"]
    mock_result.scalars.return_value = mock_scalars
    db.execute.return_value = mock_result
    service = TicketService()
    with patch("app.api.ticket.Ticket"):
        tickets = await service.get_tickets(db, status="open", agent_id="agent1")
    assert tickets == ["ticketA"]

@pytest.mark.asyncio
async def test_get_ticket():
    db = AsyncMock()
    mock_result = AsyncMock()
    mock_result.scalar_one_or_none.return_value = "ticketX"
    db.execute.return_value = mock_result
    service = TicketService()
    with patch("app.api.ticket.Ticket"):
        ticket = await service.get_ticket(db, "ticket_id")
    assert ticket == "ticketX"

@pytest.mark.asyncio
async def test_update_ticket_found():
    db = AsyncMock()
    ticket_update = MagicMock(spec=TicketUpdate)
    ticket_update.model_dump.return_value = {"status": "closed"}
    db_ticket = MagicMock()
    service = TicketService()
    service.get_ticket = AsyncMock(return_value=db_ticket)
    db.commit = AsyncMock()
    db.refresh = AsyncMock()
    result = await service.update_ticket(db, "ticket_id", ticket_update)
    assert result == db_ticket
    db.commit.assert_awaited()
    db.refresh.assert_awaited_with(db_ticket)
    db_ticket.__setattr__.assert_not_called()  # setattr is used, not __setattr__

@pytest.mark.asyncio
async def test_update_ticket_not_found():
    db = AsyncMock()
    ticket_update = MagicMock(spec=TicketUpdate)
    service = TicketService()
    service.get_ticket = AsyncMock(return_value=None)
    result = await service.update_ticket(db, "ticket_id", ticket_update)
    assert result is None

@pytest.mark.asyncio
async def test_assign_ticket_found():
    db = AsyncMock()
    db_ticket = MagicMock()
    service = TicketService()
    service.get_ticket = AsyncMock(return_value=db_ticket)
    db.commit = AsyncMock()
    db.refresh = AsyncMock()
    result = await service.assign_ticket(db, "ticket_id", "agent123")
    assert result == db_ticket
    assert db_ticket.agent_id == "agent123"
    db.commit.assert_awaited()
    db.refresh.assert_awaited_with(db_ticket)

@pytest.mark.asyncio
async def test_assign_ticket_not_found():
    db = AsyncMock()
    service = TicketService()
    service.get_ticket = AsyncMock(return_value=None)
    result = await service.assign_ticket(db, "ticket_id", "agent123")
    assert result is None