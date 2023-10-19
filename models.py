from django.conf import settings
from django.utils import timezone
from datetime import date, timedelta
from django.db import models
from django.urls import reverse


def one_week_hence():
    return date.today() + timedelta(days=7)


class Tag(models.Model):
    title = models.SlugField(max_length=50, unique=True)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    slug = models.SlugField("slug", blank=True, null=True)

    def get_absolute_url(self):
        return reverse("tougdo:tag", args=[self.id])

    def __str__(self):
        return self.title


class Priority(models.Model):
    label = models.CharField(max_length=20)
    description = models.TextField(blank=True)
    number = models.IntegerField()

    def __str__(self):
        return f"{self.number}: {self.label}"

    class Meta:
        ordering = [
            "number",
        ]


class Item(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField(null=True, blank=True)
    created_date = models.DateTimeField(auto_now_add=True)
    due_date = models.DateField(default=one_week_hence)
    priority = models.ForeignKey(Priority, on_delete=models.SET_NULL, null=True)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    done_date = models.DateField("is done", blank=True, null=True)

    def get_absolute_url(self):
        return reverse("tougdo:item-update", self.pk)

    def __str__(self):
        return f"{self.title}: due {self.due_date}"

    class Meta:
        ordering = ["due_date", "priority"]


class TaggedItem(models.Model):
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.tag}: > {self.item}"

    class Meta:
        ordering = ["item"]
