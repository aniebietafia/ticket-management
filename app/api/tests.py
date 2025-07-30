import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from app.api.ticket import TicketService
from app.schemas.ticket import TicketCreate

@pytest.mark.asyncio
async def test_create_ticket_adds_and_returns_ticket():
    # Arrange
    db = AsyncMock()
    ticket_data = TicketCreate(title="Test Title", description="Test Description")
    customer_id = "customer123"

    # Patch Ticket model in the correct namespace
    with patch("app.api.ticket.Ticket") as MockTicket:
        mock_ticket_instance = MagicMock()
        MockTicket.return_value = mock_ticket_instance

        # Act
        service = TicketService()
        result = await service.create_ticket(db, ticket_data, customer_id)

        # Assert
        MockTicket.assert_called_once_with(
            **ticket_data.model_dump(),
            customer_id=customer_id
        )
        db.add.assert_called_once_with(mock_ticket_instance)
        db.commit.assert_awaited_once()
        db.refresh.assert_awaited_once_with(mock_ticket_instance)
        assert result == mock_ticket_instance