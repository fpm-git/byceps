"""
byceps.announce.handlers.ticketing
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Announce ticketing events.

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from __future__ import annotations

from flask_babel import gettext, ngettext

from byceps.announce.helpers import (
    get_screen_name_or_fallback,
    with_locale,
)
from byceps.events.ticketing import TicketCheckedInEvent, TicketsSoldEvent
from byceps.services.ticketing import ticket_service
from byceps.services.webhooks.models import Announcement, OutgoingWebhook


@with_locale
def announce_ticket_checked_in(
    event_name: str, event: TicketCheckedInEvent, webhook: OutgoingWebhook
) -> Announcement | None:
    """Announce that a ticket has been checked in."""
    initiator_screen_name = get_screen_name_or_fallback(
        event.initiator_screen_name
    )
    user_screen_name = get_screen_name_or_fallback(event.user_screen_name)

    text = gettext(
        '%(initiator_screen_name)s has checked in ticket "%(ticket_code)s", used by %(user_screen_name)s.',
        initiator_screen_name=initiator_screen_name,
        ticket_code=event.ticket_code,
        user_screen_name=user_screen_name,
    )

    return Announcement(text)


@with_locale
def announce_tickets_sold(
    event_name: str, event: TicketsSoldEvent, webhook: OutgoingWebhook
) -> Announcement | None:
    """Announce that tickets have been sold."""
    owner_screen_name = get_screen_name_or_fallback(event.owner_screen_name)
    sale_stats = ticket_service.get_ticket_sale_stats(event.party_id)

    text = (
        ngettext(
            '%(owner_screen_name)s has paid %(quantity)s ticket.',
            '%(owner_screen_name)s has paid %(quantity)s tickets.',
            event.quantity,
            owner_screen_name=owner_screen_name,
            quantity=event.quantity,
        )
        + ' '
        + gettext(
            'Currently %(tickets_sold)s of %(tickets_max)s tickets have been paid.',
            tickets_sold=sale_stats.tickets_sold,
            tickets_max=sale_stats.tickets_max,
        )
    )

    return Announcement(text)
