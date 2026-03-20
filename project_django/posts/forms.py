from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Post

class postforms(forms.ModelForm):
  class Meta:
    model=Post
    fields=['title','content','photo']

class UserRegistrationForm(UserCreationForm):
  email=forms.EmailField(required=True)
  class Meta:
    model = User
    fields = ('username', 'email', 'password1', 'password2')
