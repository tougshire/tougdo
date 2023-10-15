from django.urls import path
from tougdo import views

app_name = "tougdo"

urlpatterns = [
    # CRUD patterns for Items
    path("", views.ItemList.as_view(), name="items"),
    path("items/tag/<slug:tagslug>/", views.ItemList.as_view(), name="items"),
    path(
        "items/all/<int:all>/",
        views.ItemList.as_view(),
        name="items",
    ),
    path(
        "items/tag/<slug:tagslug>/all/<int:all>/",
        views.ItemList.as_view(),
        name="items",
    ),
    path(
        "item/add/",
        views.ItemCreate.as_view(),
        name="item-add",
    ),
    path(
        "item/<int:pk>/detail/",
        views.ItemDetail.as_view(),
        name="item-detail",
    ),
    path(
        "item/<int:pk>/delete/",
        views.ItemDelete.as_view(),
        name="item-delete",
    ),
    path(
        "item/<int:pk>/update/",
        views.ItemUpdate.as_view(),
        name="item-update",
    ),
    path("tag", views.TagList.as_view(), name="tags"),
    path("tag/<int:tag_id>/", views.TagDetail.as_view(), name="tag"),
    # CRUD patterns for tags
    path("tag/add/", views.TagCreate.as_view(), name="tag-add"),
    path("tag/<int:pk>/delete/", views.TagDelete.as_view(), name="tag-delete"),
]
