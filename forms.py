from django.urls import reverse_lazy
from django import forms
from django.core.validators import EmailValidator
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError

from tougdo.models import (
    Item,
    Tag,
    TaggedItem,
)
from touglates.widgets import TouglateDateInput, TouglateDateTimeInput


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
            "priority",
            "done_date",
        ]
        widgets = {
            "due_date": TouglateDateInput(buttons=["today"]),
            "title": forms.TextInput(attrs={"style": "width:80%;"}),
        }


class TaggedItemForm(forms.ModelForm):
    class Meta:
        model = TaggedItem
        fields = [
            "tag",
            "item",
        ]


ItemTaggedItemFormSet = forms.inlineformset_factory(
    Item, TaggedItem, form=TaggedItemForm, extra=5, can_delete=True
)
