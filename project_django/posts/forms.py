from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Post,Comments
from .models import Post

class postforms(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['title', 'content', 'photo']

        widgets = {
            'title': forms.TextInput(attrs={
                'placeholder': 'Title...',
                'class': 'form-input'
            }),

            'content': forms.Textarea(attrs={
                'placeholder': 'What’s on your mind?',
                'class': 'form-textarea',
                'rows': 4
            }),

            'photo': forms.FileInput(attrs={
                'class': 'form-file'
            }),
        }


class UserRegistrationForm(UserCreationForm):
  email=forms.EmailField(required=True)
  class Meta:
    model = User
    fields = ('username', 'email', 'password1', 'password2')

class commentForm(forms.ModelForm):
  class Meta:
    model = Comments
    fields=['body']
