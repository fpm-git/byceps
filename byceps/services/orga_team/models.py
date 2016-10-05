# -*- coding: utf-8 -*-

"""
byceps.services.orga_team.models
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2016 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from ...blueprints.user.models.user import User
from ...database import BaseQuery, db, generate_uuid
from ...util.instances import ReprBuilder

from ..party.models import Party


class OrgaTeam(db.Model):
    """A group of organizers for a single party."""
    __tablename__ = 'orga_teams'
    __table_args__ = (
        db.UniqueConstraint('party_id', 'title'),
    )

    id = db.Column(db.Uuid, default=generate_uuid, primary_key=True)
    party_id = db.Column(db.Unicode(20), db.ForeignKey('parties.id'), index=True, nullable=False)
    party = db.relationship(Party)
    title = db.Column(db.Unicode(40), nullable=False)

    def __init__(self, party_id, title_id):
        self.party_id = party_id
        self.title_id = title_id

    def __repr__(self):
        return ReprBuilder(self) \
            .add_with_lookup('id') \
            .add_with_lookup('party_id') \
            .add_with_lookup('title') \
            .add_custom('{:d} members'.format(len(self.memberships))) \
            .build()


class MembershipQuery(BaseQuery):

    def for_party_id(self, party_id):
        return self.join(OrgaTeam).filter_by(party_id=party_id)


class Membership(db.Model):
    """The assignment of a user to an organizer team."""
    __tablename__ = 'orga_team_memberships'
    __table_args__ = (
        db.UniqueConstraint('orga_team_id', 'user_id'),
    )
    query_class = MembershipQuery

    id = db.Column(db.Uuid, default=generate_uuid, primary_key=True)
    orga_team_id = db.Column(db.Uuid, db.ForeignKey('orga_teams.id'), index=True, nullable=False)
    orga_team = db.relationship(OrgaTeam, collection_class=set, backref='memberships')
    user_id = db.Column(db.Uuid, db.ForeignKey('users.id'), index=True, nullable=False)
    user = db.relationship(User, collection_class=set, backref='orga_team_memberships')
    duties = db.Column(db.Unicode(40))

    def __init__(self, orga_team_id, user_id):
        self.orga_team_id = orga_team_id
        self.user_id = user_id

    def __repr__(self):
        return ReprBuilder(self) \
            .add_with_lookup('id') \
            .add_with_lookup('orga_team') \
            .add_with_lookup('user') \
            .build()
