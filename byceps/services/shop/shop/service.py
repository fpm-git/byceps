"""
byceps.services.shop.shop.service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from typing import List, Optional, Set

from ....database import db

from .models import Shop as DbShop
from .transfer.models import Shop, ShopID


class UnknownShopId(ValueError):
    pass


def create_shop(shop_id: ShopID, title: str, email_config_id: str) -> Shop:
    """Create a shop."""
    shop = DbShop(shop_id, title, email_config_id)

    db.session.add(shop)
    db.session.commit()

    return _db_entity_to_shop(shop)


def find_shop(shop_id: ShopID) -> Optional[Shop]:
    """Return the shop with that id, or `None` if not found."""
    shop = _find_db_shop(shop_id)

    if shop is None:
        return None

    return _db_entity_to_shop(shop)


def _find_db_shop(shop_id: ShopID) -> Optional[Shop]:
    """Return the database entity for the shop with that id, or `None`
    if not found.
    """
    return DbShop.query.get(shop_id)


def get_shop(shop_id: ShopID) -> Shop:
    """Return the shop with that id, or raise an exception."""
    shop = find_shop(shop_id)

    if shop is None:
        raise UnknownShopId(shop_id)

    return shop


def _get_db_shop(shop_id: ShopID) -> Shop:
    """Return the database entity for the shop with that id.

    Raise an exception if not found.
    """
    shop = _find_db_shop(shop_id)

    if shop is None:
        raise UnknownShopId(shop_id)

    return shop


def find_shops(shop_ids: Set[ShopID]) -> List[Shop]:
    """Return the shops with those IDs."""
    if not shop_ids:
        return []

    shops = DbShop.query \
        .filter(DbShop.id.in_(shop_ids)) \
        .all()

    return [_db_entity_to_shop(shop) for shop in shops]


def get_all_shops() -> List[Shop]:
    """Return all shops."""
    shops = DbShop.query.all()

    return [_db_entity_to_shop(shop) for shop in shops]


def get_active_shops() -> List[Shop]:
    """Return all shops that are not archived."""
    shops = DbShop.query \
        .filter_by(archived=False) \
        .all()

    return [_db_entity_to_shop(shop) for shop in shops]


def set_extra_setting(shop_id: ShopID, key: str, value: str) -> None:
    """Set a value for a key in the shop's extra settings."""
    shop = _get_db_shop(shop_id)

    if shop.extra_settings is None:
        shop.extra_settings = {}

    shop.extra_settings[key] = value

    db.session.commit()


def remove_extra_setting(shop_id: ShopID, key: str) -> None:
    """Remove the entry with that key from the shop's extra settings."""
    shop = _get_db_shop(shop_id)

    if (shop.extra_settings is None) or (key not in shop.extra_settings):
        return

    del shop.extra_settings[key]

    db.session.commit()


def _db_entity_to_shop(shop: DbShop) -> Shop:
    return Shop(
        shop.id,
        shop.title,
        shop.email_config_id,
        shop.closed,
        shop.archived,
        shop.extra_settings,
    )
