"""
byceps.services.ticketing.ticket_seat_management_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2021 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from ...database import db
from ...typing import UserID

# Load `Seat.assignment` backref.
from ..seating.dbmodels.seat_group import SeatGroup as DbSeatGroup
from ..seating import seat_service, seat_group_service
from ..seating.transfer.models import Seat, SeatID

from . import log_service
from .exceptions import (
    SeatChangeDeniedForBundledTicket,
    SeatChangeDeniedForGroupSeat,
    TicketCategoryMismatch,
    TicketIsRevoked,
)
from .dbmodels.ticket import Ticket as DbTicket
from . import ticket_service
from .transfer.models import TicketID


def appoint_seat_manager(
    ticket_id: TicketID, manager_id: UserID, initiator_id: UserID
) -> None:
    """Appoint the user as the ticket's seat manager."""
    ticket = _get_ticket(ticket_id)

    ticket.seat_managed_by_id = manager_id

    log_entry = log_service.build_log_entry(
        'seat-manager-appointed',
        ticket.id,
        {
            'appointed_seat_manager_id': str(manager_id),
            'initiator_id': str(initiator_id),
        },
    )
    db.session.add(log_entry)

    db.session.commit()


def withdraw_seat_manager(ticket_id: TicketID, initiator_id: UserID) -> None:
    """Withdraw the ticket's custom seat manager."""
    ticket = _get_ticket(ticket_id)

    ticket.seat_managed_by_id = None

    log_entry = log_service.build_log_entry(
        'seat-manager-withdrawn',
        ticket.id,
        {
            'initiator_id': str(initiator_id),
        },
    )
    db.session.add(log_entry)

    db.session.commit()


def occupy_seat(
    ticket_id: TicketID, seat_id: SeatID, initiator_id: UserID
) -> None:
    """Occupy the seat with this ticket."""
    ticket = _get_ticket(ticket_id)

    _deny_seat_management_if_ticket_belongs_to_bundle(ticket)

    seat = seat_service.get_seat(seat_id)

    if seat.category_id != ticket.category_id:
        raise TicketCategoryMismatch(
            'Ticket and seat belong to different categories.'
        )

    _deny_seat_management_if_seat_belongs_to_group(seat)

    previous_seat_id = ticket.occupied_seat_id

    ticket.occupied_seat_id = seat.id

    log_entry_data = {
        'seat_id': str(seat.id),
        'initiator_id': str(initiator_id),
    }
    if previous_seat_id is not None:
        log_entry_data['previous_seat_id'] = str(previous_seat_id)

    log_entry = log_service.build_log_entry(
        'seat-occupied', ticket.id, log_entry_data
    )
    db.session.add(log_entry)

    db.session.commit()


def release_seat(ticket_id: TicketID, initiator_id: UserID) -> None:
    """Release the seat occupied by this ticket."""
    ticket = _get_ticket(ticket_id)

    _deny_seat_management_if_ticket_belongs_to_bundle(ticket)

    seat = seat_service.find_seat(ticket.occupied_seat_id)
    if seat is None:
        raise ValueError('Ticket does not occupy a seat.')

    _deny_seat_management_if_seat_belongs_to_group(seat)

    ticket.occupied_seat_id = None

    log_entry = log_service.build_log_entry(
        'seat-released',
        ticket.id,
        {
            'seat_id': str(seat.id),
            'initiator_id': str(initiator_id),
        },
    )
    db.session.add(log_entry)

    db.session.commit()


def _get_ticket(ticket_id: TicketID) -> DbTicket:
    """Return the ticket with that ID.

    Raise an exception if the ID is unknown or if the ticket has been
    revoked.
    """
    ticket = ticket_service.get_ticket(ticket_id)

    if ticket.revoked:
        raise TicketIsRevoked(f'Ticket {ticket_id} has been revoked.')

    return ticket


def _deny_seat_management_if_ticket_belongs_to_bundle(ticket: DbTicket) -> None:
    """Raise an exception if this ticket belongs to a bundle.

    A ticket bundle is meant to occupy a matching seat group with the
    appropriate mechanism, not to separately occupy single seats.
    """
    if ticket.belongs_to_bundle:
        raise SeatChangeDeniedForBundledTicket(
            f"Ticket '{ticket.code}' belongs to a bundle and, thus, "
            'must not be used to occupy or release a single seat.'
        )


def _deny_seat_management_if_seat_belongs_to_group(seat: Seat) -> None:
    if seat_group_service.is_seat_part_of_a_group(seat.id):
        raise SeatChangeDeniedForGroupSeat(
            f"Seat '{seat.label}' belongs to a group and, thus, "
            'cannot be occupied by a single ticket, or removed separately.'
        )
