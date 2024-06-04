from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass

class Listing(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="listings")
    name = models.CharField(max_length=128)
    category = models.CharField(max_length=128)
    image = models.URLField(blank=True, null=True)
    price = models.FloatField()
    description = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=[('active', 'Active'), ('closed', 'Closed')], default='active')


    def __str__(self) -> str:
        return f'{self.user.username} created a {self.name} listing'

class Bid(models.Model):
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="bids")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="bids")
    bid = models.FloatField()
    
    def __str__(self) -> str:
        return f'{self.user.username} bid on {self.listing.name}'

class Comment(models.Model):
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="comments")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="comments")
    comment = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)


    def __str__(self):
        return f'Comment by {self.user.username} on {self.listing.name}'
    

class Watchlist(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    listing = models.ManyToManyField(Listing, related_name="watchlists")

    def __str__(self):
        return f'USername {self.user.username} watchlist'

