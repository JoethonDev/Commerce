from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.forms import ModelForm, TextInput, NumberInput, Textarea


from .models import *

import datetime
# Form 
class ListForm(ModelForm):
    class Meta:
        model = AuctionsListing
        fields = ['title', 'price', 'category', 'description']
        widgets = {
            'title' : TextInput(attrs={
                'class': "form-control",
                }),
            'price' : NumberInput(attrs={
                'class': "form-control",
                }),
            'category' : TextInput(attrs={
                'class': "form-control",
                }),
            'description' : Textarea(attrs={
                'class': "form-control",
                })
        }

# Functions
def StrDateTime(obj):
    for item in obj:
        dateTime =  datetime.datetime.fromisoformat(str(item.dateTime))
        item.dateTime = dateTime.strftime("%B, %d, %Y, %I:%M %p")

# Views
def index(request): 
    items = AuctionsListing.objects.all() 
    # Make Sure they are active! 
    StrDateTime(items)
    return render(request, "auctions/index.html", {
        'items' : items
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
            user = User.objects.get(username=request.user.username)
            request.session['watchlist'] = WatchList.objects.filter(user=user).count()
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

@login_required
def createListing(request):
    # Have GET && POST
    # GET Displays Form || POST submit Data must be valid 
    if request.method == 'GET':
        return render(request, 'auctions/createListing.html', {
            'form' : ListForm()
        })
    else:
        title = request.POST['title']
        price = request.POST['price']
        category = request.POST['category']
        description = request.POST['description']

        user = User.objects.get(username=request.user)
        AuctionsListing.objects.create(title=title, price=price, category=category, description=description, seller=user)
        return HttpResponseRedirect(reverse(index))
    
def listing(request, id):
    # Need to get Item Details First [Title - Description - Seller - Price(Changeable) - Category]
    # Send Item as new dictionary
    item = AuctionsListing.objects.get(pk=id)
    bids = Bids.objects.filter(item=item).order_by('-price')
    comments = Comments.objects.filter(item=item).order_by('-pk')
    StrDateTime(comments)
    # If no Bids Issue Find solution!!
    try:
        currentPrice = bids[0].price
        winner = bids[0].bidder.username
        item.price = currentPrice
    except IndexError:
        winner = None
        currentPrice = item.price
    
    message = None
    added = False

    if request.user.is_authenticated:
        # For WatchList Check
        user = User.objects.get(username=request.user.username)
        watchlist = WatchList.objects.filter(item=item, user=user).count()
        if watchlist:
            added = True

        # For Making Bid
        if request.method == 'POST' :
            try:
                price = float(request.POST['price'])
            except:
                return HttpResponseRedirect(reverse('listing', args=[id]))
            if price < currentPrice or price == currentPrice:
                message = 'Sorry Your Bid is not accepted! Bid more than current one...'
            else:
                Bids.objects.create(item=item, bidder=user, price=price)
                return HttpResponseRedirect(reverse('listing', args=[id]))
    
    return render(request, 'auctions/listing.html' , {
        'item' : item,
        'count' : len(bids),
        'message' : message,
        'added' : added,
        'winner' : winner,
        'comments' : comments
    }) 

def watchlist(request, id):
    user = User.objects.get(username=request.user)
    watchlist = WatchList.objects.filter(user=user)

    if request.method == 'GET':
        return render(request, 'auctions/watchlist.html', {
            'watchlist' : watchlist
        })
    elif request.user.is_authenticated and request.method == 'POST':
        # For WatchList Check
        item = AuctionsListing.objects.get(pk=id)
        watchlist.filter(item=item)
        if watchlist.count():
            watchlist.delete()
        else :
            WatchList.objects.create(item=item, user=user)

        request.session['watchlist'] = WatchList.objects.filter(user=user).count()
        return HttpResponseRedirect(reverse('listing', args=[id]))

def close(request, id):
    item = AuctionsListing.objects.get(pk=id)
    if item.ended:
        item.ended = False
    else :
        item.ended = True

    item.save()
    return HttpResponseRedirect(reverse('listing', args=[id]))

def comment(request, id):
    comment = request.POST['comment']
    item = AuctionsListing.objects.get(pk=id)
    user = User.objects.get(username=request.user.username)
    Comments.objects.create(comment=comment, commenter=user, item=item)
    return HttpResponseRedirect(reverse('listing', args=[id]))

def categories(request):
    # Get all categories as List
    categoriesList = AuctionsListing.objects.all().values('category')
    return render(request, 'auctions/categories.html',{
        'categories' : categoriesList
    })
    pass
    
def category(request, category):
    items = AuctionsListing.objects.filter(category=category, ended=False)
    StrDateTime(items)
    return render(request, 'auctions/category.html',{
        'items' : items
    })
    pass