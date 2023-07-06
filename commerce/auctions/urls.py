from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("createlist", views.createListing, name="createList"),
    path("listing/<int:id>", views.listing, name="listing"),
    path("watchlist/<int:id>", views.watchlist, name="watchlist"),
    path("close/<int:id>", views.close, name="close"),
    path("comment/<int:id>", views.comment, name="comment"),
    path("categories", views.categories, name="categories"),
    path("category/<str:category>/", views.category, name="category")
]
