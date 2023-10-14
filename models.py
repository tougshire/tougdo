from django.conf import settings
from django.utils import timezone

from django.db import models
from django.urls import reverse


def one_week_hence():
    return timezone.now() + timezone.timedelta(days=7)


class Tag(models.Model):
    title = models.SlugField(max_length=50, unique=True)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    def get_absolute_url(self):
        return reverse("tag", args=[self.id])

    def __str__(self):
        return self.title


class Item(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField(null=True, blank=True)
    created_date = models.DateTimeField(auto_now_add=True)
    due_date = models.DateTimeField(default=one_week_hence)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    def get_absolute_url(self):
        return reverse("item-update", self.pk)

    def __str__(self):
        return f"{self.title}: due {self.due_date}"

    class Meta:
        ordering = ["due_date"]


class TaggedItem(models.Model):
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.tag}: > {self.item}"

    class Meta:
        ordering = ["item"]
