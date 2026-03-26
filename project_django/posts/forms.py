from django import forms
from django.contrib.auth.forms import UserCreationForm ,UserChangeForm
# from django.contrib.auth.models import User
from .models import Post,Comments,CustomUser
from .models import Post

class postforms(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['title', 'content', 'photo']
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['title'].widget.attrs.update({
            'class': 'input',
            'placeholder': 'Title...'
        })

        self.fields['content'].widget.attrs.update({
            'class': 'textarea',
            'placeholder': "What's on your mind?"
        })

class UserRegistrationForm(UserCreationForm):
  email=forms.EmailField(required=True)
  class Meta:
    model = CustomUser
    fields = ('username', 'email', 'password1', 'password2')

class UserEditForm(forms.ModelForm):
  class Meta:
    model = CustomUser
    fields = ('username', 'email','bio','profile_picture')
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['bio'].widget.attrs.update({
            'class': 'input',
            'placeholder': 'Bio...'
        })

class commentForm(forms.ModelForm):
  class Meta:
    model = Comments
    fields=['body']
