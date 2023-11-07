from typing import Any
from urllib.parse import urlencode
from django.forms.models import BaseModelForm
from django.http import HttpResponse, QueryDict
from django.urls import reverse, reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.utils.text import slugify

from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
    UpdateView,
    DeleteView,
)
from .models import Item, Tag
from .forms import ItemForm, ItemTaggedItemFormSet
from tougshire_vistas.models import Vista
from tougshire_vistas.views import (
    get_vista_queryset,
    make_vista_fields,
    vista_context_data,
)


class ItemCreate(LoginRequiredMixin, CreateView):
    model = Item
    form_class = ItemForm

    def form_valid(self, form):
        form_saved = form.save(commit=False)
        form_saved.owner = self.request.user
        form_saved.save()
        return super().form_valid(form_saved)

    def get_success_url(self):
        return reverse("tougdo:items")

    def get_context_data(self, **kwargs: Any):
        context_data = super().get_context_data(**kwargs)
        if self.request.POST:
            context_data["taggeditems"] = ItemTaggedItemFormSet(self.request.POST)
        else:
            context_data["taggeditems"] = ItemTaggedItemFormSet()

        return context_data


class ItemDetail(LoginRequiredMixin, DetailView):
    model = Item


class ItemList(LoginRequiredMixin, ListView):
    model = Item
    template_name = "tougdo/index.html"

    def setup(self, request, *args, **kwargs):
        self.vista_settings = {
            "max_search_keys": 5,
            "fields": [],
        }

        self.vista_settings["fields"] = make_vista_fields(
            Item,
            field_names=[
                "title",
                "description",
                "priority",
                "due_date",
                "created_date",
                "owner",
                "done_date",
            ],
        )

        self.vista_settings["fields"]["priority"]["operators"] = [
            ("lte", "at most"),
            ("exact", "is"),
            ("gte", "at least"),
        ]

        if "by_value" in kwargs and "by_parameter" in kwargs:
            self.vista_get_by = QueryDict(
                urlencode(
                    [
                        ("filter__fieldname__0", [kwargs.get("by_parameter")]),
                        ("filter__op__0", ["exact"]),
                        ("filter__value__0", [kwargs.get("by_value")]),
                        (
                            "order_by",
                            [
                                "due_date",
                                "priority",
                            ],
                        ),
                        ("paginate_by", self.paginate_by),
                    ],
                    doseq=True,
                )
            )

        self.vista_defaults = QueryDict(
            urlencode(
                [
                    ("filter__fieldname__0", ["done_date"]),
                    ("filter__op__0", ["exact"]),
                    ("filter__value__0", None),
                    (
                        "order_by",
                        [
                            "due_date",
                            "priority",
                        ],
                    ),
                    ("paginate_by", self.paginate_by),
                ],
                doseq=True,
            ),
            mutable=True,
        )

        return super().setup(request, *args, **kwargs)

    def get_queryset(self):
        base_queryset = super().get_queryset()

        self.vistaobj = {"querydict": QueryDict(), "queryset": base_queryset}

        vista_queryset = get_vista_queryset(self)
        queryset = vista_queryset.filter(owner=self.request.user)
        return queryset

    def post(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def get_paginate_by(self, queryset):
        if "paginate_by" in self.vistaobj["querydict"] and isinstance(
            self.vistaobj["querydict"]["paginate_by"], int
        ):
            return self.vistaobj["querydict"]["paginate_by"]

        return super().get_paginate_by(queryset)

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)

        vista_data = vista_context_data(self.vista_settings, self.vistaobj["querydict"])

        context_data = {**context_data, **vista_data}
        context_data["vista_default"] = dict(self.vista_defaults)

        if self.request.user.is_authenticated:
            context_data["vistas"] = Vista.objects.filter(
                user=self.request.user, model_name="sdcpeople.Article"
            ).all()  # for choosing saved vistas

        if self.request.POST.get("vista_name"):
            context_data["vista_name"] = self.request.POST.get("vista_name")

        context_data["count"] = self.object_list.count()

        return context_data


class ItemUpdate(LoginRequiredMixin, UpdateView):
    model = Item
    template_name = "tougdo/item_form.html"
    form_class = ItemForm

    def get_success_url(self):
        return reverse("tougdo:items")


class ItemDelete(LoginRequiredMixin, DeleteView):
    model = Item

    def get_success_url(self):
        return reverse_lazy("tougdo:items")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


class TagCreate(LoginRequiredMixin, CreateView):
    model = Tag
    fields = ["slug"]

    def form_valid(self, form):
        tag = form.save(commit=False)
        tag.owner = self.request.user
        tag.save()
        return super().form_valid(form)

    def get_success_url(self):
        print("tp23an725", self.kwargs)
        if "popup" in self.kwargs and self.kwargs.get("popup"):
            print("tp23an723")
            return reverse_lazy(
                "touglates:popup_closer",
                kwargs={
                    "app_name": "tougdo",
                    "model_name": "Tag",
                    "pk": self.object.pk,
                },
            )
        else:
            return super().get_success_url()


class TagUpdate(LoginRequiredMixin, UpdateView):
    model = Tag
    fields = ["slug"]


class TagDetail(LoginRequiredMixin, DeleteView):
    model = Tag


class TagDelete(LoginRequiredMixin, DeleteView):
    model = Tag
    # You have to use reverse_lazy() instead of reverse(),
    # as the urls are not loaded when the file is imported.
    success_url = reverse_lazy("tougdo:index")


class TagList(LoginRequiredMixin, ListView):
    model = Tag
    template_name = "tougdo/index.html"

    def get_queryset(self):
        return Tag.objects.filter(owner=self.request.user)
