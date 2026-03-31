from django import forms
from django.contrib.auth.forms import UserCreationForm ,UserChangeForm
# from django.contrib.auth.models import User
from .models import Post,Comment,CustomUser

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

    def clean_photo(self):
        photo = self.cleaned_data.get('photo')
        if photo:
            if not photo.content_type in ['image/jpeg', 'image/png', 'image/gif', 'image/webp']:
                raise forms.ValidationError('Only JPEG, PNG, GIF, WebP images allowed.')
            if photo.size > 5*1024*1024:  # 5MB
                raise forms.ValidationError('Image size should not exceed 5MB.')
        return photo

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

  def clean_profile_picture(self):
        profile_picture = self.cleaned_data.get('profile_picture')
        if profile_picture:
            if not profile_picture.content_type in ['image/jpeg', 'image/png', 'image/gif', 'image/webp']:
                raise forms.ValidationError('Only JPEG, PNG, GIF, WebP images allowed.')
            if profile_picture.size > 5*1024*1024:  # 5MB
                raise forms.ValidationError('Image size should not exceed 5MB.')
        return profile_picture

class commentForm(forms.ModelForm):
  class Meta:
    model = Comment
    fields=['body']
    
  def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['body'].widget.attrs.update({
            'class': 'textarea',
            'placeholder': 'Add a comment...'
        })
