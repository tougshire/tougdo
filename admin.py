from django.contrib import admin
from tougdo.models import Item, Tag, TaggedItem

admin.site.register(Item)
admin.site.register(Tag)
admin.site.register(TaggedItem)
