from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),

    # Paths for login, logout and register account
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),

    # Paths to create listing page and saving new listing
    path("create", views.create, name="create"),
    path("new_listing", views.new_listing, name="new_listing"),

    # Paths for the listing page
    path("listing/<int:listing_id>", views.listing, name="listing"),
    path("add_watchlist/<int:listing_id>", views.add_watchlist, name="add_watchlist"),
    path("remove_watchlist/<int:listing_id>", views.remove_watchlist, name="remove_watchlist"),
    path("close_listing/<int:listing_id>", views.close_listing, name="close_listing"),
    path('listing/<int:listing_id>/bid', views.new_bid, name='new_bid'),
    path("listing/<int:listing_id>/comment", views.comment, name="comment"),

    # Path to watchlist page
    path("watchlist", views.watchlist, name="watchlist"),

    # Paths to categories page and search function
    path("categories", views.categories, name="categories"),
    path("listings_category/<str:category>", views.listings_category, name="listings_category"),


]
