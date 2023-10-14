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


class ItemCreate(LoginRequiredMixin, CreateView):
    model = Item
    fields = [
        "title",
        "description",
        "due_date",
    ]

    def get_initial(self):
        initial_data = super().get_initial()
        owner = self.request.user
        initial_data["owner"] = owner
        return initial_data

    def get_context_data(self):
        context = super().get_context_data()
        context["title"] = "Create a new item"
        return context

    def get_success_url(self):
        return reverse("list", args=[self.object.tag_id])


class ItemDetail(LoginRequiredMixin, DetailView):
    model = Item


class ItemList(LoginRequiredMixin, ListView):
    model = Item
    template_name = "tougdo/tag.html"

    def get_queryset(self):
        if "tag_id" in self.kwargs:
            return Item.objects.filter(
                tagged_item__tag__id=self.kwargs["tag_id"],
                owner=self.request.user,
            )
        else:
            return Item.objects.filter(owner=self.request.user)

    def get_context_data(self):
        context = super().get_context_data()
        if "tag_id" in self.kwargs:
            context["tag"] = Tag.objects.get(id=self.kwargs["tag_id"])
        return context


class ItemUpdate(LoginRequiredMixin, UpdateView):
    model = Item
    fields = [
        "title",
        "description",
        "due_date",
    ]

    def get_context_data(self):
        context = super().get_context_data()
        context["tag"] = self.object.tag
        context["title"] = "Edit item"
        return context

    def get_success_url(self):
        return reverse("list", args=[self.object.tag_id])


class ItemDelete(LoginRequiredMixin, DeleteView):
    model = Item

    def get_success_url(self):
        return reverse_lazy("list", args=[self.kwargs["list_id"]])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["tag"] = self.object.tag
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
    success_url = reverse_lazy("index")


class TagList(LoginRequiredMixin, ListView):
    model = Tag
    template_name = "tougdo/index.html"

    def get_queryset(self):
        return Tag.objects.filter(owner=self.request.user)
