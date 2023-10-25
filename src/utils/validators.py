import re
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


def username_validator(value):
    pattern = r'^[a-zA-Z][\w\d_.]{3,28}[\w]$'
    if re.match(pattern, value):
        return value
    raise ValidationError(_('invalid username'), code='invalid')

def positive_amount_validator(value):
    if value <= 0:
        raise ValidationError(_("value must be positive"), code='invalid')
    return value