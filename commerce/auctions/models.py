from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass


class AuctionsListing(models.Model):
    title = models.CharField(max_length=64, blank=False)
    price = models.FloatField(blank=False)
    category = models.CharField(max_length=64, blank=True)
    description = models.TextField(blank=True)
    dateTime = models.DateTimeField(auto_now=True)
    ended = models.BooleanField(default=True)
    seller = models.ForeignKey('User', models.CASCADE, related_name='seller')
    watchListUsers = models.ManyToManyField('User' , through='WatchList', related_name='watchListItems')
    biddingItem = models.ManyToManyField('User' , through='Bids', related_name='bidder')
    comment = models.ManyToManyField('User' , through='Comments', related_name='userComment')
    # img ===> TODO
    # models.ManyToManyField()


class Bids(models.Model):
    item = models.ForeignKey('AuctionsListing', models.CASCADE)
    bidder = models.ForeignKey('User', models.CASCADE)
    price = models.FloatField()
    dateTime = models.DateTimeField(auto_now=True)


class Comments(models.Model):
    item = models.ForeignKey('AuctionsListing', models.CASCADE)
    commenter = models.ForeignKey('User', models.CASCADE)
    comment = models.CharField(max_length=1024)
    dateTime = models.DateTimeField(auto_now=True) 

class WatchList(models.Model):
    item = models.ForeignKey('AuctionsListing', models.CASCADE)
    user = models.ForeignKey('User', models.CASCADE)
    
    class Meta:
        unique_together = ('item', 'user')

