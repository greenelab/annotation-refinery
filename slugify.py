"""
This is a slugify function based largely on Django's slugify function.
Django website - https://www.djangoproject.com/

The version this was based on can be found here:  https://github.com/django/
django/blob/92053acbb9160862c3e743a99ed8ccff8d4f8fd6/django/utils/text.py
"""

import re
import unicodedata


def slugify(value, allow_unicode=False):
    """
    Convert to ASCII if 'allow_unicode' is False. Convert spaces to hyphens.
    Remove characters that aren't alphanumerics, underscores, or hyphens.
    Convert to lowercase. Also strip leading and trailing whitespace.
    """
    if allow_unicode:
        value = unicodedata.normalize('NFKC', value)
        value = re.sub('[^\w\s-]', '', value, flags=re.U).strip().lower()

    value = re.sub('[^\w\s-]', '', value).strip().lower()
    value = re.sub('[-\s]+', '-', value)
    return value
