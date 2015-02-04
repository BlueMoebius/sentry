"""
sentry.rules.conditions.group_event
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:copyright: (c) 2010-2014 by the Sentry Team, see AUTHORS for more details.
:license: BSD, see LICENSE for more details.
"""

from __future__ import absolute_import

from django import forms

from sentry.rules.conditions.base import EventCondition


class MatchType(object):
    EQUAL = 'eq'
    NOT_EQUAL = 'ne'

class GroupEventForm(forms.Form):
    match = forms.ChoiceField(choices=(
        (MatchType.EQUAL, 'equals'),
        (MatchType.NOT_EQUAL, 'does not equal'),
    ))
#     group = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'group id'}))
    group = forms.IntegerField(widget=forms.NumberInput(attrs={'placeholder':'group'}))


class GroupEventCondition(EventCondition):
    form_cls = GroupEventForm
    label = 'An events group is {match} {group}'

    def passes(self, event, state, **kwargs):
        match = self.get_option('match')
        group = self.get_option('group')

        if not (match and group):
            return False

        if match == MatchType.EQUAL:
            if int(event.group_id) == int(group):
                return True
            else:
                return False

        if match == MatchType.NOT_EQUAL:
            if int(event.group_id) != int(group):
                return True
            else:
                return False


