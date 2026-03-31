from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
# Create your models here.

class CustomUser(AbstractUser):
    username=models.CharField(max_length=150, blank=True, null=True)
    email=models.EmailField(unique=True)
    bio=models.TextField(blank=True, null=True)
    profile_picture=models.ImageField(upload_to='profile_pictures/', blank=True, null=True)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']
 

class Post(models.Model):
    author = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    content = models.TextField()
    photo = models.ImageField(upload_to='photos/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=['author', '-created_at']),
        ]

    def __str__(self):
        return f"{self.author.username} - {self.title}"

class Comment(models.Model):
    author = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    post=models.ForeignKey(Post , on_delete=models.SET_NULL, null=True)
    body=models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=['author', '-created_at']),
            models.Index(fields=['post', '-created_at']),
        ]

    def __str__(self):
        return f"{self.body[:50]} - {self.author.username}"

