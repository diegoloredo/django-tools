# coding: utf-8

"""
    static path selection
    ~~~~~~~~~~~~~~~~~~~~
    
    TODO: Made this generic and don't use settings.STATIC_ROOT direct, let it
    be set as a argument to widget/fields etc.
    
     * model field
     * form field
     * widget

    :copyleft: 2012 by the django-tools team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

import os

if __name__ == "__main__":
    # For doctest only
    os.environ["DJANGO_SETTINGS_MODULE"] = "django.conf.global_settings"

from django import forms
from django.db import models
from django.conf import settings

from django_tools.utils.messages import failsafe_message


def directory_walk(path):
    """
    Directory tree generator
    similar to os.walk, except:
      - yield only directories
      - sorted list case-insensitive
      - follow links (os.walk can do this since python 2.6)
    """
    dirs = []
    for name in os.listdir(path):
        if os.path.isdir(os.path.join(path, name)):
            dirs.append(name)

    yield path

    # Sort case-insensitive
    dirs.sort(cmp=lambda x, y: cmp(x.lower(), y.lower()))

    for dir in dirs:
        sub_path = os.path.join(path, dir)
        for x in directory_walk(sub_path):
            yield x




class StaticPathWidget(forms.Select):
    """
    Select a sub directory in settings.STATIC_ROOT
    
    >>> import os, django_tools
    >>> settings.STATIC_ROOT = os.path.dirname(os.path.abspath(django_tools.__file__))
    >>> StaticPathWidget().choices # doctest: +ELLIPSIS
    [('auto_update_cache', 'auto_update_cache'), ..., ('views', 'views')]
    """
    def __init__(self, attrs=None):
        super(StaticPathWidget, self).__init__(attrs)

        self._base_path = os.path.abspath(os.path.normpath(settings.STATIC_ROOT))

        try:
            self.choices = self._get_path_choices()
        except OSError, err:
            self.choices = []
            if settings.DEBUG:
                failsafe_message("Can't read STATIC_ROOT: %s" % err)

    def _get_path_choices(self):
        Static_dirs_choices = []
        cut_pos = len(self._base_path)
        for root in directory_walk(self._base_path):
            rel_dir = root[cut_pos:].strip(os.sep)
            if rel_dir:
                Static_dirs_choices.append((rel_dir, rel_dir))
        return Static_dirs_choices


class StaticPathModelField(models.TextField):
    """
    Model field for select a sub directory in settings.STATIC_ROOT
    """
    __metaclass__ = models.SubfieldBase

#    def __init__(self, separator=",", strip_items=True, skip_empty=True, *args, **kwargs):
#        self.separator = separator
#        self.strip_items = strip_items
#        self.skip_empty = skip_empty
#        super(StaticPathModelField, self).__init__(*args, **kwargs)

    def formfield(self, **kwargs):
        """ Use always own widget and form field. """
        kwargs["widget"] = StaticPathWidget
#        kwargs["form_class"] = SignSeparatedFormField
        return super(StaticPathModelField, self).formfield(**kwargs)


if __name__ == "__main__":
    import doctest
    print doctest.testmod(
#        verbose=True
        verbose=False
    )
    print "DocTest end."
