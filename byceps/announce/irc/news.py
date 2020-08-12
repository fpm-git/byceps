"""
byceps.announce.irc.news
~~~~~~~~~~~~~~~~~~~~~~~~

Announce news events on IRC.

:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from ...events.news import NewsItemPublished
from ...services.brand import service as brand_service
from ...services.news import (
    channel_service as news_channel_service,
    service as news_service,
)
from ...services.user import service as user_service
from ...signals import news as news_signals
from ...util.irc import send_message
from ...util.jobqueue import enqueue

from ._config import CHANNEL_ORGA_LOG, CHANNEL_PUBLIC


@news_signals.item_published.connect
def _on_news_item_published(sender, *, event: NewsItemPublished = None) -> None:
    enqueue(announce_news_item_published_publicly, event)
    enqueue(announce_news_item_published_internally, event)


def announce_news_item_published_publicly(event: NewsItemPublished) -> None:
    """Announce publicly that a news item has been published."""
    channels = [CHANNEL_PUBLIC]

    item = news_service.find_item(event.item_id)
    channel = news_channel_service.find_channel(item.channel.id)
    brand = brand_service.find_brand(channel.brand_id)

    text = (
        f'{brand.title}: Die News "{item.title}" wurde veröffentlicht. '
        f'{item.external_url}'
    )

    send_message(channels, text)


def announce_news_item_published_internally(event: NewsItemPublished) -> None:
    """Announce internally that a news item has been published."""
    channels = [CHANNEL_ORGA_LOG]

    initiator_label = user_service.find_screen_name(event.initiator_id) or 'Jemand'
    item = news_service.find_item(event.item_id)

    text = (
        f'{initiator_label} hat die News "{item.title}" veröffentlicht. '
        f'{item.external_url}'
    )

    send_message(channels, text)
