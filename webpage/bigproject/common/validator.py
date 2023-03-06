from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _

class LengthValidator:
    def __init__(self):
        self.min_length = 10
        self.max_length = 16

    def validate(self, password, user=None):
        if len(password) < self.min_length or len(password) > self.max_length:
            raise ValidationError(
                _("This password must contain at least %(min_length)d characters."),
                code='password_too_short',
                params={'min_length': self.min_length},
            )

    def get_help_text(self):
        return _(
            "Your password must contain at least %(min_length)d characters."
            % {'min_length': self.min_length}
        )
