from django.urls import reverse, reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin

from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
    UpdateView,
    DeleteView,
)
from .models import Item, Tag
from .forms import ItemForm


class ItemCreate(LoginRequiredMixin, CreateView):
    model = Item
    fields = [
        "title",
        "description",
        "due_date",
    ]

    def get_context_data(self):
        context = super().get_context_data()
        context["title"] = "Create a new item"
        return context

    def form_valid(self, form):
        form_saved = form.save(commit=False)
        form_saved.owner = self.request.user
        form_saved.save()
        return super().form_valid(form_saved)

    def get_success_url(self):
        return reverse("tougdo:items")


class ItemDetail(LoginRequiredMixin, DetailView):
    model = Item


class ItemList(LoginRequiredMixin, ListView):
    model = Item
    template_name = "tougdo/index.html"

    def get_queryset(self):
        filter_args = {"owner": self.request.user}

        if "tagslug" in self.kwargs and self.kwargs.get("tagslug") > "":
            filter_args["tagslug"] = self.kwargs.get("tagslug")
        if not ("all" in self.kwargs and self.kwargs.get("all")):
            filter_args["done_date__isnull"] = True

        return Item.objects.filter(**filter_args)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if "tag_id" in self.kwargs:
            context["tag"] = Tag.objects.get(id=self.kwargs["tag_id"])
        return context


class ItemUpdate(LoginRequiredMixin, UpdateView):
    model = Item
    template_name = "tougdo/item_form.html"
    form_class = ItemForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Edit item"
        return context

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
    fields = ["title"]

    def get_context_data(self):
        context = super().get_context_data()
        context["title"] = "Add a new list"
        return context


class TagUpdate(LoginRequiredMixin, UpdateView):
    model = Tag


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
