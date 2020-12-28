"""
byceps.announce.irc.news
~~~~~~~~~~~~~~~~~~~~~~~~

Announce news events on IRC.

:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from ...events.news import NewsItemPublished

from ..common import news

from ._util import send_message


def announce_news_item_published(event: NewsItemPublished) -> None:
    """Announce that a news item has been published."""
    text = news.assemble_text_for_news_item_published(event)

    send_news_message(event, text)


# helpers


def send_news_message(event: NewsItemPublished, text: str) -> None:
    scope = 'news'
    scope_id = str(event.channel_id)

    send_message(event, scope, scope_id, text)
