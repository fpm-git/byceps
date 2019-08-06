"""
:Copyright: 2006-2019 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from byceps.services.authentication.session import service as session_service

from tests.base import AbstractAppTestCase
from tests.helpers import create_brand, create_party, create_site, \
    create_user, http_client


class CurrentUserTestCase(AbstractAppTestCase):

    def setUp(self):
        super().setUp()

        brand = create_brand()
        party = create_party(brand.id)
        create_site(party.id)

    def test_when_logged_in(self):
        user = create_user('McFly')
        session_service.create_session_token(user.id)

        response = self.send_request(user_id=user.id)

        assert response.status_code == 200
        assert response.mimetype == 'text/html'

    def test_when_not_logged_in(self):
        response = self.send_request()

        assert response.status_code == 302
        assert 'Location' in response.headers

    # helpers

    def send_request(self, *, user_id=None):
        url = '/users/me'
        with http_client(self.app, user_id=user_id) as client:
            return client.get(url)
