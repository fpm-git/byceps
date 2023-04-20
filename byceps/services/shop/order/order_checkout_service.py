"""
byceps.services.shop.order.order_checkout_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from collections.abc import Iterator
from datetime import datetime
from typing import Optional

from moneyed import Currency
from sqlalchemy.exc import IntegrityError
import structlog

from byceps.database import db
from byceps.events.shop import ShopOrderPlaced
from byceps.services.shop.article import article_service
from byceps.services.shop.cart.models import Cart, CartItem
from byceps.services.shop.shop import shop_service
from byceps.services.shop.shop.models import ShopID
from byceps.services.shop.storefront import storefront_service
from byceps.services.shop.storefront.models import StorefrontID
from byceps.services.user import user_service
from byceps.util.result import Err, Ok, Result

from . import (
    order_log_service,
    order_sequence_service,
    order_service,
)
from .dbmodels.line_item import DbLineItem
from .dbmodels.order import DbOrder
from .models.number import OrderNumber
from .models.order import (
    Order,
    Orderer,
)


log = structlog.get_logger()


def place_order(
    storefront_id: StorefrontID,
    orderer: Orderer,
    cart: Cart,
    *,
    created_at: Optional[datetime] = None,
) -> Result[tuple[Order, ShopOrderPlaced], None]:
    """Place an order for one or more articles."""
    storefront = storefront_service.get_storefront(storefront_id)
    shop = shop_service.get_shop(storefront.shop_id)

    orderer_user = user_service.get_user(orderer.user_id)

    order_number_sequence = order_sequence_service.get_order_number_sequence(
        storefront.order_number_sequence_id
    )
    order_number = order_sequence_service.generate_order_number(
        order_number_sequence.id
    )

    cart_items = cart.get_items()

    if created_at is None:
        created_at = datetime.utcnow()

    db_order = _build_order(
        created_at, shop.id, storefront.id, order_number, orderer, shop.currency
    )
    db_line_items = list(_build_line_items(cart_items, db_order))
    db_order._total_amount = cart.calculate_total_amount().amount
    db_order.processing_required = any(
        db_line_item.processing_required for db_line_item in db_line_items
    )

    db.session.add(db_order)
    db.session.add_all(db_line_items)

    _reduce_article_stock(cart_items)

    try:
        db.session.commit()
    except IntegrityError as e:
        log.error('Order placement failed', order_number=order_number, exc=e)
        db.session.rollback()
        return Err(None)

    order = order_service._order_to_transfer_object(db_order)

    # Create log entry in separate step as order ID is not available earlier.
    log_entry_data = {'initiator_id': str(orderer_user.id)}
    order_log_service.create_entry('order-placed', order.id, log_entry_data)

    event = ShopOrderPlaced(
        occurred_at=order.created_at,
        initiator_id=orderer_user.id,
        initiator_screen_name=orderer_user.screen_name,
        order_id=order.id,
        order_number=order.order_number,
        orderer_id=orderer_user.id,
        orderer_screen_name=orderer_user.screen_name,
    )

    log.info('Order placed', shop_order_placed_event=event)

    return Ok((order, event))


def _build_order(
    created_at: datetime,
    shop_id: ShopID,
    storefront_id: StorefrontID,
    order_number: OrderNumber,
    orderer: Orderer,
    currency: Currency,
) -> DbOrder:
    """Build an order."""
    return DbOrder(
        created_at,
        shop_id,
        storefront_id,
        order_number,
        orderer.user_id,
        orderer.company,
        orderer.first_name,
        orderer.last_name,
        orderer.country,
        orderer.zip_code,
        orderer.city,
        orderer.street,
        currency,
    )


def _build_line_items(
    cart_items: list[CartItem], db_order: DbOrder
) -> Iterator[DbLineItem]:
    """Build line items from the cart's content."""
    for cart_item in cart_items:
        article = cart_item.article
        quantity = cart_item.quantity
        line_amount = cart_item.line_amount

        yield DbLineItem(
            db_order,
            article.id,
            article.item_number,
            article.type_,
            article.description,
            article.price.amount,
            article.tax_rate,
            quantity,
            line_amount.amount,
            article.processing_required,
        )


def _reduce_article_stock(cart_items: list[CartItem]) -> None:
    """Reduce article stock according to what is in the cart."""
    for cart_item in cart_items:
        article = cart_item.article
        quantity = cart_item.quantity

        article_service.decrease_quantity(article.id, quantity, commit=False)
