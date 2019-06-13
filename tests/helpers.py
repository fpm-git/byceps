"""
tests.helpers
~~~~~~~~~~~~~

:Copyright: 2006-2019 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from contextlib import contextmanager

from flask import appcontext_pushed, g

from byceps.application import create_app
from byceps.database import db
from byceps.services.authorization import service as authorization_service

from testfixtures.authentication import create_session_token \
    as _create_session_token
from testfixtures.brand import create_brand as _create_brand
from testfixtures.user import create_user as _create_user, \
    create_user_with_detail as _create_user_with_detail

from .base import CONFIG_FILENAME_TEST_PARTY


@contextmanager
def app_context(*, config_filename=CONFIG_FILENAME_TEST_PARTY):
    app = create_app(config_filename)

    with app.app_context():
        yield app


@contextmanager
def current_party_set(app, party):
    def handler(sender, **kwargs):
        g.party_id = party.id
        g.brand_id = party.brand_id

    with appcontext_pushed.connected_to(handler, app):
        yield


@contextmanager
def current_user_set(app, user):
    def handler(sender, **kwargs):
        g.current_user = user

    with appcontext_pushed.connected_to(handler, app):
        yield


def create_user(*args, **kwargs):
    user = _create_user(*args, **kwargs)

    db.session.add(user)
    db.session.commit()

    return user


def create_user_with_detail(*args, **kwargs):
    user = _create_user_with_detail(*args, **kwargs)

    db.session.add(user)
    db.session.commit()

    return user


def assign_permissions_to_user(user_id, role_id, permission_ids,
                               *, initiator_id=None):
    """Create the role and permissions, assign the permissions to the
    role, and assign the role to the user.
    """
    role = authorization_service.create_role(role_id, role_id)

    for permission_id in permission_ids:
        permission = authorization_service.create_permission(permission_id,
                                                             permission_id)
        authorization_service.assign_permission_to_role(permission.id, role.id)

    authorization_service.assign_role_to_user(user_id, role.id,
                                              initiator_id=initiator_id)


def create_session_token(user_id):
    session_token = _create_session_token(user_id)

    db.session.add(session_token)
    db.session.commit()


def create_brand(brand_id, title):
    brand = _create_brand(id=brand_id, title=title)

    db.session.add(brand)
    db.session.commit()

    return brand
