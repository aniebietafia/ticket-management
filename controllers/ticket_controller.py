from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from database import get_db, User
from schemas import TicketCreate, TicketUpdate, TicketResponse, TicketAssign
from ticket_service import ticket_service
from dependencies import get_current_active_user, require_role

router = APIRouter(prefix="/tickets", tags=["Tickets"])

@router.post("/", response_model=TicketResponse)
async def create_ticket(
    ticket: TicketCreate,
    current_user: User = require_role(["customer"]),
    db: AsyncSession = Depends(get_db)
):
    """Create a new ticket"""
    try:
        db_ticket = await ticket_service.create_ticket(db, ticket, current_user.id)
        return {
            "status": "success",
            "status_code": status.HTTP_201_CREATED,
            "message": "Ticket created successfully",
            "ticket": db_ticket.model_dump()
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create ticket"
        )

@router.get("/my", response_model=List[TicketResponse])
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
        "tickets": [ticket.model_dump() for ticket in tickets]
    }

@router.get("/", response_model=TicketResponse)
async def get_ticket(
    ticket_id: str,
    status: Optional[str] = Query(None, description="Filter tickets by status"),
    current_user: User = require_role(["agent", "admin"]),
    db: AsyncSession = Depends(get_db)
):
    if current_user.role not in ["agent", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to access this ticket"
        )

    """Get ticket by ID"""
    db_ticket = await ticket_service.get_ticket(db, ticket_id)
    if not db_ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ticket not found"
        )
    
    if status and db_ticket.status != status:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ticket status does not match the provided filter"
        )
    
    return {
        "status": "success",
        "status_code": status.HTTP_200_OK,
        "message": "Ticket retrieved successfully",
        "ticket": db_ticket.model_dump()
    }

@router.get("/{id}", response_model=List[TicketResponse])
async def get_tickets(
    db: AsyncSession = Depends(get_db)
):
    """Get all tickets with optional filters"""
    tickets = await ticket_service.get_tickets(db)
    if not tickets:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No tickets found"
        )
    return {
        "status": "success",
        "status_code": status.HTTP_200_OK,
        "message": "Tickets retrieved successfully",
        "tickets": [ticket.model_dump() for ticket in tickets]
    }

@router.patch("/{id}", response_model=TicketResponse)
async def update_ticket(
    id: str,
    ticket_update: TicketUpdate,
    current_user: User = require_role(["agent"]),
    db: AsyncSession = Depends(get_db)
):
    """Update ticket information"""
    db_ticket = await ticket_service.get_ticket(db, id)
    if not db_ticket or db_ticket.agent_id != current_user.id:
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
        "ticket": updated_ticket.model_dump()
    }

@router.patch("/{id}/assign", response_model=TicketResponse)
async def assign_ticket(
    id: str,
    ticket_assign: TicketAssign,
    current_user: User = require_role(["admin"]),
    db: AsyncSession = Depends(get_db)
):
    """Assign ticket to an agent"""
    db_ticket = await ticket_service.get_ticket(db, id)
    if not db_ticket or db_ticket.agent_id != current_user.id:
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
        "ticket": assigned_ticket.model_dump()
    }