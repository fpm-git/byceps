"""
:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from flask import Flask

from byceps.announce.announce import build_announcement_request
from byceps.events.board import (
    BoardPostingCreatedEvent,
    BoardPostingHiddenEvent,
    BoardPostingUnhiddenEvent,
    BoardTopicCreatedEvent,
    BoardTopicHiddenEvent,
    BoardTopicLockedEvent,
    BoardTopicMovedEvent,
    BoardTopicPinnedEvent,
    BoardTopicUnhiddenEvent,
    BoardTopicUnlockedEvent,
    BoardTopicUnpinnedEvent,
)
from byceps.services.board.models import (
    BoardCategoryID,
    BoardID,
    PostingID,
    TopicID,
)
from byceps.services.brand.models import BrandID
from byceps.services.user.models.user import UserID

from tests.helpers import generate_token, generate_uuid

from .helpers import assert_text, now


OCCURRED_AT = now()
BRAND_ID = BrandID('acmecon')
BRAND_TITLE = 'ACME Entertainment Convention'
BOARD_ID = BoardID(generate_token())
CATEGORY_1_ID = BoardCategoryID(generate_uuid())
CATEGORY_1_TITLE = 'Category 1'
CATEGORY_2_ID = BoardCategoryID(generate_uuid())
CATEGORY_2_TITLE = 'Category 2'
TOPIC_ID = TopicID(generate_uuid())
POSTING_ID = PostingID(generate_uuid())
MODERATOR_ID = UserID(generate_uuid())
MODERATOR_SCREEN_NAME = 'TheModerator'
USER_ID = UserID(generate_uuid())


def test_announce_topic_created(app: Flask, webhook_for_irc):
    expected_link = f'http://example.com/board/topics/{TOPIC_ID}'
    expected_text = (
        'TheShadow999 has created topic "Brötchen zum Frühstück" '
        f'in "ACME Entertainment Convention" board: {expected_link}'
    )

    event = BoardTopicCreatedEvent(
        occurred_at=OCCURRED_AT,
        initiator_id=USER_ID,
        initiator_screen_name='TheShadow999',
        brand_id=BRAND_ID,
        brand_title=BRAND_TITLE,
        board_id=BOARD_ID,
        topic_id=TOPIC_ID,
        topic_creator_id=USER_ID,
        topic_creator_screen_name='TheShadow999',
        topic_title='Brötchen zum Frühstück',
        url=expected_link,
    )

    actual = build_announcement_request(event, webhook_for_irc)

    assert_text(actual, expected_text)


def test_announce_topic_hidden(app: Flask, webhook_for_irc):
    expected_link = f'http://example.com/board/topics/{TOPIC_ID}'
    expected_text = (
        'TheModerator has hidden topic "Brötchen zum Frühstück" '
        'by TheShadow999 '
        f'in "ACME Entertainment Convention" board: {expected_link}'
    )

    event = BoardTopicHiddenEvent(
        occurred_at=OCCURRED_AT,
        initiator_id=MODERATOR_ID,
        initiator_screen_name=MODERATOR_SCREEN_NAME,
        brand_id=BRAND_ID,
        brand_title=BRAND_TITLE,
        board_id=BOARD_ID,
        topic_id=TOPIC_ID,
        topic_creator_id=USER_ID,
        topic_creator_screen_name='TheShadow999',
        topic_title='Brötchen zum Frühstück',
        moderator_id=MODERATOR_ID,
        moderator_screen_name=MODERATOR_SCREEN_NAME,
        url=expected_link,
    )

    actual = build_announcement_request(event, webhook_for_irc)

    assert_text(actual, expected_text)


def test_announce_topic_unhidden(app: Flask, webhook_for_irc):
    expected_link = f'http://example.com/board/topics/{TOPIC_ID}'
    expected_text = (
        'TheModerator has unhidden topic "Brötchen zum Frühstück" '
        'by TheShadow999 '
        f'in "ACME Entertainment Convention" board: {expected_link}'
    )

    event = BoardTopicUnhiddenEvent(
        occurred_at=OCCURRED_AT,
        initiator_id=MODERATOR_ID,
        initiator_screen_name=MODERATOR_SCREEN_NAME,
        brand_id=BRAND_ID,
        brand_title=BRAND_TITLE,
        board_id=BOARD_ID,
        topic_id=TOPIC_ID,
        topic_creator_id=USER_ID,
        topic_creator_screen_name='TheShadow999',
        topic_title='Brötchen zum Frühstück',
        moderator_id=MODERATOR_ID,
        moderator_screen_name=MODERATOR_SCREEN_NAME,
        url=expected_link,
    )

    actual = build_announcement_request(event, webhook_for_irc)

    assert_text(actual, expected_text)


def test_announce_topic_locked(app: Flask, webhook_for_irc):
    expected_link = f'http://example.com/board/topics/{TOPIC_ID}'
    expected_text = (
        'TheModerator has closed topic "Brötchen zum Frühstück" '
        'by TheShadow999 '
        f'in "ACME Entertainment Convention" board: {expected_link}'
    )

    event = BoardTopicLockedEvent(
        occurred_at=OCCURRED_AT,
        initiator_id=MODERATOR_ID,
        initiator_screen_name=MODERATOR_SCREEN_NAME,
        brand_id=BRAND_ID,
        brand_title=BRAND_TITLE,
        board_id=BOARD_ID,
        topic_id=TOPIC_ID,
        topic_creator_id=USER_ID,
        topic_creator_screen_name='TheShadow999',
        topic_title='Brötchen zum Frühstück',
        moderator_id=MODERATOR_ID,
        moderator_screen_name=MODERATOR_SCREEN_NAME,
        url=expected_link,
    )

    actual = build_announcement_request(event, webhook_for_irc)

    assert_text(actual, expected_text)


def test_announce_topic_unlocked(app: Flask, webhook_for_irc):
    expected_link = f'http://example.com/board/topics/{TOPIC_ID}'
    expected_text = (
        'TheModerator has reopened topic "Brötchen zum Frühstück" '
        'by TheShadow999 '
        f'in "ACME Entertainment Convention" board: {expected_link}'
    )

    event = BoardTopicUnlockedEvent(
        occurred_at=OCCURRED_AT,
        initiator_id=MODERATOR_ID,
        initiator_screen_name=MODERATOR_SCREEN_NAME,
        brand_id=BRAND_ID,
        brand_title=BRAND_TITLE,
        board_id=BOARD_ID,
        topic_id=TOPIC_ID,
        topic_creator_id=USER_ID,
        topic_creator_screen_name='TheShadow999',
        topic_title='Brötchen zum Frühstück',
        moderator_id=MODERATOR_ID,
        moderator_screen_name=MODERATOR_SCREEN_NAME,
        url=expected_link,
    )

    actual = build_announcement_request(event, webhook_for_irc)

    assert_text(actual, expected_text)


def test_announce_topic_pinned(app: Flask, webhook_for_irc):
    expected_link = f'http://example.com/board/topics/{TOPIC_ID}'
    expected_text = (
        'TheModerator has pinned topic "Brötchen zum Frühstück" '
        'by TheShadow999 '
        f'in "ACME Entertainment Convention" board: {expected_link}'
    )

    event = BoardTopicPinnedEvent(
        occurred_at=OCCURRED_AT,
        initiator_id=MODERATOR_ID,
        initiator_screen_name=MODERATOR_SCREEN_NAME,
        brand_id=BRAND_ID,
        brand_title=BRAND_TITLE,
        board_id=BOARD_ID,
        topic_id=TOPIC_ID,
        topic_creator_id=USER_ID,
        topic_creator_screen_name='TheShadow999',
        topic_title='Brötchen zum Frühstück',
        moderator_id=MODERATOR_ID,
        moderator_screen_name=MODERATOR_SCREEN_NAME,
        url=expected_link,
    )

    actual = build_announcement_request(event, webhook_for_irc)

    assert_text(actual, expected_text)


def test_announce_topic_unpinned(app: Flask, webhook_for_irc):
    expected_link = f'http://example.com/board/topics/{TOPIC_ID}'
    expected_text = (
        'TheModerator has unpinned topic "Brötchen zum Frühstück" '
        'by TheShadow999 '
        f'in "ACME Entertainment Convention" board: {expected_link}'
    )

    event = BoardTopicUnpinnedEvent(
        occurred_at=OCCURRED_AT,
        initiator_id=MODERATOR_ID,
        initiator_screen_name=MODERATOR_SCREEN_NAME,
        brand_id=BRAND_ID,
        brand_title=BRAND_TITLE,
        board_id=BOARD_ID,
        topic_id=TOPIC_ID,
        topic_creator_id=USER_ID,
        topic_creator_screen_name='TheShadow999',
        topic_title='Brötchen zum Frühstück',
        moderator_id=MODERATOR_ID,
        moderator_screen_name=MODERATOR_SCREEN_NAME,
        url=expected_link,
    )

    actual = build_announcement_request(event, webhook_for_irc)

    assert_text(actual, expected_text)


def test_announce_topic_moved(app: Flask, webhook_for_irc):
    expected_link = f'http://example.com/board/topics/{TOPIC_ID}'
    expected_text = (
        'TheModerator has moved topic "Brötchen zum Frühstück" '
        'by TheShadow999 '
        'from "Category 1" to "Category 2" '
        f'in "ACME Entertainment Convention" board: {expected_link}'
    )

    event = BoardTopicMovedEvent(
        occurred_at=OCCURRED_AT,
        initiator_id=MODERATOR_ID,
        initiator_screen_name=MODERATOR_SCREEN_NAME,
        brand_id=BRAND_ID,
        brand_title=BRAND_TITLE,
        board_id=BOARD_ID,
        topic_id=TOPIC_ID,
        topic_creator_id=USER_ID,
        topic_creator_screen_name='TheShadow999',
        topic_title='Brötchen zum Frühstück',
        old_category_id=CATEGORY_1_ID,
        old_category_title=CATEGORY_1_TITLE,
        new_category_id=CATEGORY_2_ID,
        new_category_title=CATEGORY_2_TITLE,
        moderator_id=MODERATOR_ID,
        moderator_screen_name=MODERATOR_SCREEN_NAME,
        url=expected_link,
    )

    actual = build_announcement_request(event, webhook_for_irc)

    assert_text(actual, expected_text)


def test_announce_posting_created(app: Flask, webhook_for_irc):
    expected_link = f'http://example.com/board/postings/{POSTING_ID}'
    expected_text = (
        'TheShadow999 replied in topic "Brötchen zum Frühstück" '
        f'in "ACME Entertainment Convention" board: {expected_link}'
    )

    event = BoardPostingCreatedEvent(
        occurred_at=OCCURRED_AT,
        initiator_id=USER_ID,
        initiator_screen_name='TheShadow999',
        brand_id=BRAND_ID,
        brand_title=BRAND_TITLE,
        board_id=BOARD_ID,
        posting_creator_id=USER_ID,
        posting_creator_screen_name='TheShadow999',
        posting_id=POSTING_ID,
        topic_id=TOPIC_ID,
        topic_title='Brötchen zum Frühstück',
        topic_muted=False,
        url=expected_link,
    )

    actual = build_announcement_request(event, webhook_for_irc)

    assert_text(actual, expected_text)


def test_announce_posting_created_on_muted_topic(app: Flask, webhook_for_irc):
    link = f'http://example.com/board/postings/{POSTING_ID}'

    event = BoardPostingCreatedEvent(
        occurred_at=OCCURRED_AT,
        initiator_id=USER_ID,
        initiator_screen_name='TheShadow999',
        brand_id=BRAND_ID,
        brand_title=BRAND_TITLE,
        board_id=BOARD_ID,
        posting_creator_id=USER_ID,
        posting_creator_screen_name='TheShadow999',
        posting_id=POSTING_ID,
        topic_id=TOPIC_ID,
        topic_title='Brötchen zum Frühstück',
        topic_muted=True,
        url=link,
    )

    actual = build_announcement_request(event, webhook_for_irc)

    assert actual is None


def test_announce_posting_hidden(app: Flask, webhook_for_irc):
    expected_link = f'http://example.com/board/postings/{POSTING_ID}'
    expected_text = (
        'TheModerator has hidden a reply by TheShadow999 in topic '
        '"Brötchen zum Frühstück" '
        f'in "ACME Entertainment Convention" board: {expected_link}'
    )

    event = BoardPostingHiddenEvent(
        occurred_at=OCCURRED_AT,
        initiator_id=MODERATOR_ID,
        initiator_screen_name=MODERATOR_SCREEN_NAME,
        brand_id=BRAND_ID,
        brand_title=BRAND_TITLE,
        board_id=BOARD_ID,
        posting_id=POSTING_ID,
        posting_creator_id=USER_ID,
        posting_creator_screen_name='TheShadow999',
        topic_id=TOPIC_ID,
        topic_title='Brötchen zum Frühstück',
        moderator_id=MODERATOR_ID,
        moderator_screen_name=MODERATOR_SCREEN_NAME,
        url=expected_link,
    )

    actual = build_announcement_request(event, webhook_for_irc)

    assert_text(actual, expected_text)


def test_announce_posting_unhidden(app: Flask, webhook_for_irc):
    expected_link = f'http://example.com/board/postings/{POSTING_ID}'
    expected_text = (
        'TheModerator has unhidden a reply by TheShadow999 in topic '
        '"Brötchen zum Frühstück" '
        f'in "ACME Entertainment Convention" board: {expected_link}'
    )

    event = BoardPostingUnhiddenEvent(
        occurred_at=OCCURRED_AT,
        initiator_id=MODERATOR_ID,
        initiator_screen_name=MODERATOR_SCREEN_NAME,
        brand_id=BRAND_ID,
        brand_title=BRAND_TITLE,
        board_id=BOARD_ID,
        posting_id=POSTING_ID,
        posting_creator_id=USER_ID,
        posting_creator_screen_name='TheShadow999',
        topic_id=TOPIC_ID,
        topic_title='Brötchen zum Frühstück',
        moderator_id=MODERATOR_ID,
        moderator_screen_name=MODERATOR_SCREEN_NAME,
        url=expected_link,
    )

    actual = build_announcement_request(event, webhook_for_irc)

    assert_text(actual, expected_text)
