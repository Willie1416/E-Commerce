from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.db.models import Max
from django.contrib.auth.decorators import login_required

from .models import User, Listing, Bid, Watchlist, Comment


def index(request):
    return render(request, "auctions/index.html",{
        "listings" : Listing.objects.all(),
    })


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")


def create(request):
    return render(request, "auctions/create.html")


def new_listing(request):

    # Get all the specifics for the new listing
    if request.method == "POST":
        name = request.POST['name']
        description = request.POST['description']
        price = request.POST['price']
        image = request.POST.get('image', '')
        category = request.POST['category']

        # Create a new database entry with details
        new_listing = Listing(
            user=request.user,
            name=name.capitalize(),
            description=description.capitalize(),
            price=price,
            image=image,
            category=category.capitalize()
        )
        new_listing.save()
        return HttpResponseRedirect(reverse("listing", args=[new_listing.id]))

    return render(request, "auctions/listing.html")


def listing(request, listing_id):
    # Set up variables if user not logged in
    is_in_watchlist = False
    user_has_highest_bid = False

    # Retrieve the lisitng, and comment objects from database
    listing = Listing.objects.get(pk=listing_id)
    comments = Comment.objects.filter(listing=listing)

    # Get the number of bids and the highest bid,
    bids = listing.bids.count()
    highest_bid = listing.bids.aggregate(Max('bid'))['bid__max'] or listing.price

    # If user is logged in retrieve their watchlist or create a new
    if request.user.is_authenticated:
        watchlist, created = Watchlist.objects.get_or_create(user=request.user)

        # Check if they have highest bid and if the listing is in their watchlist
        user_has_highest_bid = listing.bids.filter(bid=highest_bid, user=request.user).exists()
        is_in_watchlist = watchlist.listing.filter(pk=listing_id).exists()

    return render(request, "auctions/listing.html",{
        "listing": listing,
        "watchlist": is_in_watchlist,
        "bids": bids,
        "highest_bid": highest_bid,
        "user_highest_bid": user_has_highest_bid,
        "comments": comments,
        "user": request.user 
    })


@login_required
def add_watchlist(request, listing_id):
    listing = Listing.objects.get(pk=listing_id)

    # Get the watchlist to add the new listing
    if request.method == "POST":
        watchlist, created = Watchlist.objects.get_or_create(user=request.user)

        # Verify the listining is not already in watchlist
        if listing not in watchlist.listing.all():
            watchlist.listing.add(listing)
            watchlist.save()
            print("Listing added to watchlist.")
        else:
            print('Listing is already in your watchlist.')

        
        return HttpResponseRedirect(reverse('listing', args=[listing_id]))
    
    return render(request, "auctions/listing.html")


def remove_watchlist(request, listing_id):
    listing = Listing.objects.get(pk=listing_id)

    # Get watchlist to remove the nw listing
    if request.method == "POST":
        watchlist = Watchlist.objects.get(user=request.user)

        # Verify the listining is in the users watchlist
        if listing in watchlist.listing.all():
            watchlist.listing.remove(listing)
            watchlist.save()
            print("Listing removed from watchlist")
        else:
            print("Listing not in watchlist")

        return HttpResponseRedirect(reverse('listing', args=[listing_id]))
    
    return render(request, "auctions/listing.html")


def close_listing(request, listing_id):
    # Retrieve listing, its bids, and highest bid
    listing = Listing.objects.get(pk=listing_id)
    bids = listing.bids.count()
    highest_bid = listing.bids.aggregate(Max('bid'))['bid__max'] or listing.price

    # Verify the listing is not closed already
    if listing.status != "closed":
        # Change the listing status to closed
        listing.status = "closed"
        listing.save()

        return render(request, "auctions/listing.html",{
            "listing": listing,
            "bids": bids,
            "highest_bid": highest_bid,
            "user": request.user 
        })
    else:
        return render(request, "auctions/listing.html",{
            "listing": listing,
            "bids": bids,
            "highest_bid": highest_bid,
            "user": request.user,
            "error_message" : "You already closed this listing"
        })


@login_required
def new_bid(request, listing_id):
    listing = Listing.objects.get(pk=listing_id)

    if request.method == "POST":

        # Get the new bid, the current highest, and number of bids
        new_bid = float(request.POST['bid'])
        highest_bid = listing.bids.aggregate(Max('bid'))['bid__max'] or listing.price
        bids = listing.bids.count()

        # Verify listing is still open
        if listing.status == "closed":
            return render(request, "auctions/listing.html", {
                "listing": listing,
                "bids": bids,
                "highest_bid": highest_bid,
                "error_message": "This listing is already closed"
            })
            
        
        if bids == 0:
            # If there are no bids, new bid should be greater than or equal to the starting price
            if new_bid >= listing.price:
                listing.price = new_bid
                listing.save()
                
                new_bid = Bid(
                    listing=listing,
                    user=request.user,
                    bid=new_bid
                )
                new_bid.save()

                return HttpResponseRedirect(reverse('listing', args=[listing_id]))
            else:
                return render(request, "auctions/listing.html", {
                    "listing": listing,
                    "bids": bids,
                    "highest_bid": listing.price,
                    "error_message": "Your bid must be at least the starting price."
                })
        else:
            # If there are existing bids, new bid should be higher than the current highest bid
            if new_bid > highest_bid:
                listing.price = new_bid
                listing.save()

                new_bid = Bid(
                    listing=listing,
                    user=request.user,
                    bid=new_bid
                )
                new_bid.save()

                return HttpResponseRedirect(reverse('listing', args=[listing_id]))
            
        return render(request, "auctions/listing.html", {
            "listing": listing,
            "highest_bid": highest_bid,
            "bids": bids,
            "error_message": "Your bid must be higher than the current highest bid."
        })
    
    return render(request, "auctions/listing.html")


@login_required
def comment(request, listing_id):
    listing = Listing.objects.get(pk=listing_id)

    if request.method == "POST":
        
        # Retrieve the comment
        comment = str(request.POST['comment'])

        # Create a new database entry for the comment
        new_comment = Comment(
            listing=listing,
            user=request.user,
            comment=comment
        )
        new_comment.save()

        return HttpResponseRedirect(reverse('listing', args=[listing_id]))
    
    return render(request, "auctions/listing.html")


@login_required
def watchlist(request):
    watchlist, created = Watchlist.objects.get_or_create(user=request.user)

    # Render users watchlist page with all listings
    return render(request, "auctions/watchlist.html",{
        "listings" : watchlist.listing.all(),
    })


# Redirects to search page for categoires
def categories(request):
    categories = Listing.objects.values_list('category', flat=True).distinct()

    print(categories)

    return render(request, "auctions/categories.html", {
                "categories": categories,
            })


def listings_category(request, category):
    listings = Listing.objects.filter(category=category)

    return render(request, "auctions/categories_listing.html", {
        "listings" : listings,
        "category" : category
    })
