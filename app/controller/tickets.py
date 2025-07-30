from fastapi import APIRouter, Depends, HTTPException, status, Query, Path
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from app.models.ticket import get_db, User
from app.schemas.ticket import TicketCreate, TicketUpdate, TicketResponse, TicketAssign
from app.api.ticket import ticket_service
from app.config.dependencies import get_current_active_user, require_role
from typing import Any

router = APIRouter(prefix="/tickets", tags=["Tickets"])

@router.post("/", response_model=TicketResponse, status_code=status.HTTP_201_CREATED)
async def create_ticket(
    ticket: TicketCreate,
    current_user: Any = Depends(require_role(["customer"])),
    db: AsyncSession = Depends(get_db)
):
    """Create a new ticket"""
    try:
        db_ticket = await ticket_service.create_ticket(db, ticket, current_user.id)
        return db_ticket
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create ticket"
        )

@router.get("/my", response_model=None, status_code=status.HTTP_200_OK)
async def get_my_tickets(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Get tickets for the current user"""
    tickets = await ticket_service.get_ticket_by_customer(db, current_user.id)
    if not tickets:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No tickets found for this user"
        )
    return {
        "status": "success",
        "status_code": status.HTTP_200_OK,
        "message": "Tickets retrieved successfully",
        "tickets": [ticket for ticket in tickets]
    }

@router.get("/", response_model=None, status_code=status.HTTP_200_OK)
async def get_tickets(
    ticket_id: str,
    ticket_status: Optional[str] = Query(None, description="Filter tickets by status or assigned agent"),
    current_user: Any = Depends(require_role(["agent", "admin"])),
    db: AsyncSession = Depends(get_db)
) -> List[TicketResponse]:
    """Get all tickets filtered by status or assigned agent"""
    if not ticket_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ticket ID is required"
        )

    tickets = await ticket_service.get_tickets(db, status=ticket_status, agent_id=current_user.id)
    if not tickets:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No tickets found"
        )

    return {
        "status": "success",
        "status_code": status.HTTP_200_OK,
        "message": "Tickets retrieved successfully",
        "tickets": [ticket for ticket in tickets]
    }

@router.get("/{id}", response_model=TicketResponse, status_code=status.HTTP_200_OK)
async def get_ticket(
    db: AsyncSession = Depends(get_db),
    current_user: Any = Depends(require_role(["agent", "admin", "customer"])),
    id: str = Path(..., description="Ticket ID to view")
):
    """View specific ticket with access control"""
    db_ticket = await ticket_service.get_ticket(db, id)
    if not db_ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ticket not found"
        )

    """Check if current user role has permission to view the ticket"""
    if current_user.role not in ["admin", "agent", "customer"] and db_ticket.customer_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to view this ticket"
        )
    return db_ticket
    
    # return {
    #     "status": "success",
    #     "status_code": status.HTTP_200_OK,
    #     "message": "Ticket retrieved successfully",
    #     "ticket": db_ticket.model_dump()
    # }

@router.patch("/{id}", response_model=None, status_code=status.HTTP_200_OK)
async def update_ticket(
    id: str,
    ticket_update: TicketUpdate,
    current_user: Any = Depends(require_role(["agent", "admin"])),
    db: AsyncSession = Depends(get_db)
):
    """Update ticket information"""
    db_ticket = await ticket_service.get_ticket(db, id)
    if not db_ticket or (current_user.role not in ["admin", "agent"] and db_ticket.agent_id != current_user.id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ticket not found or you do not have permission to update this ticket"
        )
    updated_ticket = await ticket_service.update_ticket(db, id, ticket_update)
    if not updated_ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ticket not found"
        )
    return {
        "status": "success",
        "status_code": status.HTTP_200_OK,
        "message": "Ticket updated successfully",
        "ticket": updated_ticket
    }

@router.patch("/{id}/assign", response_model=None, status_code=status.HTTP_200_OK)
async def assign_ticket(
    id: str,
    ticket_assign: TicketAssign,
    current_user: Any = Depends(require_role(["admin"])),
    db: AsyncSession = Depends(get_db)
):
    """Assign ticket to an agent"""
    db_ticket = await ticket_service.get_ticket(db, id)
    if not db_ticket or current_user.role not in ["admin"]:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ticket not found or you do not have permission to assign this ticket"
        )
    
    assigned_ticket = await ticket_service.assign_ticket(db, id, ticket_assign.agent_id)
    if not assigned_ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ticket not found"
        )

    return {
        "status": "success",
        "status_code": status.HTTP_200_OK,
        "message": "Ticket assigned successfully",
        "ticket": assigned_ticket
    }