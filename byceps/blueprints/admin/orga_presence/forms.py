"""
byceps.blueprints.admin.orga_presence.forms
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

import dataclasses
from datetime import datetime

from flask_babel import gettext, lazy_gettext, to_user_timezone, to_utc
from wtforms import DateField, TimeField
from wtforms.validators import InputRequired

from byceps.util.datetime.range import DateTimeRange
from byceps.util.l10n import LocalizedForm


def build_presence_create_form(dt_range_utc: DateTimeRange):
    dt_range_local = dataclasses.replace(
        dt_range_utc,
        start=to_user_timezone(dt_range_utc.start).replace(tzinfo=None),
        end=to_user_timezone(dt_range_utc.end).replace(tzinfo=None),
    )

    class CreateForm(LocalizedForm):
        starts_on = DateField(
            lazy_gettext('Start date'),
            default=dt_range_local.start.date,
            validators=[InputRequired()],
        )
        starts_at = TimeField(
            lazy_gettext('Start time'),
            default=dt_range_local.start.time,
            validators=[InputRequired()],
        )
        ends_on = DateField(
            lazy_gettext('End date'),
            default=dt_range_local.end.date,
            validators=[InputRequired()],
        )
        ends_at = TimeField(
            lazy_gettext('End time'),
            default=dt_range_local.end.time,
            validators=[InputRequired()],
        )

        def validate(self) -> bool:
            if not super().validate():
                return False

            valid = True

            starts_at = to_utc(
                datetime.combine(self.starts_on.data, self.starts_at.data)
            )
            ends_at = to_utc(
                datetime.combine(self.ends_on.data, self.ends_at.data)
            )

            def append_date_time_error(field_date, field_time):
                for field in field_date, field_time:
                    field.errors.append(
                        gettext('Value must be in valid range.')
                    )

            if not (dt_range_utc.start <= starts_at < dt_range_utc.end):
                append_date_time_error(self.starts_on, self.starts_at)
                valid = False

            # As the presence end timestamp is exclusive, it may match
            # the date range's end, which is exclusive, too.
            if not (dt_range_utc.start <= ends_at <= dt_range_utc.end):
                append_date_time_error(self.ends_on, self.ends_at)
                valid = False

            if starts_at >= ends_at:
                self.form_errors.append(
                    gettext('Start value must be before end value.')
                )
                valid = False

            return valid

    return CreateForm
