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
    path("tags", views.TagList.as_view(), name="tags"),
    path("tag/<int:pk>/", views.TagDetail.as_view(), name="tag"),
    path("tag/add/", views.TagCreate.as_view(), name="tag-add"),
    path(
        "tag/popup/add/",
        views.TagCreate.as_view(),
        name="tag-popup-add",
        kwargs={"popup": True},
    ),
    path("tag/<int:pk>/delete/", views.TagDelete.as_view(), name="tag-delete"),
]
