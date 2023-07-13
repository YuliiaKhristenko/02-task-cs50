from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("wikipedia/error", views.error, name="error"),
    path("wikipedia/search", views.search, name="search"),
    path("wikipedia/add", views.add, name="add"),
    path("wikipedia/add/<str:title>", views.add, name="add"),
    path("wikipedia/edit", views.edit, name="edit"),
    path("wikipedia/edit/<str:title>", views.edit, name="edit"),
    path("wikipedia/random", views.random_entry, name="random"),
    path("wikipedia/<str:title>", views.entry, name="entry"),
    path("<str:title>", views.entry, name="e_entry")
]
