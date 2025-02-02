"""
byceps.application.blueprints.common.blueprints
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from __future__ import annotations

from byceps.util.framework.blueprint import BlueprintReg


def get_common_blueprints(
    *, style_guide_enabled: bool = False
) -> list[BlueprintReg]:
    blueprints = [
        ('common.authn.password', '/authentication/password'),
        ('common.core', None),
        ('common.guest_server', None),
        ('common.locale', '/locale'),
        ('monitoring.healthcheck', '/health'),
    ]

    if style_guide_enabled:
        blueprints.append(('common.style_guide', '/style_guide'))

    return blueprints
