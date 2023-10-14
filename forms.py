from django.urls import reverse_lazy
from django import forms
from django.core.validators import EmailValidator
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError

from tougdo.models import (
    Item,
    ToDoList,
    ToDoMember,
)
from touglates.widgets import TouglateDateInput


def validate_blank(value):
    if value == "":
        return
    else:
        raise ValidationError(
            _("%(value)s failed"),
            params={"value": value},
        )


class ItemForm(forms.ModelForm):
    class Meta:
        model = Item
        fields = [
            "title",
            "description",
            "due_date",
        ]


class ToDoMemberForm(forms.ModelForm):
    class Meta:
        model = ToDoMember
        fields = [
            "tag",
            "item",
        ]


ItemToDoMemberFormSet = forms.inlineformset_factory(
    ToDoMember, Item, form=ToDoMemberForm, extra=5, can_delete=True
)
