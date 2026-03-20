from django.shortcuts import render
from .models import Post
from .forms import postforms, UserRegistrationForm
from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login

# Create your views here.

def index(request):
    return render(request, 'index.html')

def all_posts(request):
    posts=Post.objects.all().order_by('-created_at')
    return render(request, 'posts.html', {'posts': posts})

@login_required

def new_post(request): 
    if request.method=='POST':
        form=postforms(request.POST, request.FILES)
        if form.is_valid():
            form=form.save( commit =False)
            form.author=request.user
            form.save()
            return redirect('all_posts')
    else:
        form=postforms()
    return render(request, 'new_post.html', {'form': form})

@login_required
def edit_post(request, post_id):
    post=get_object_or_404(Post, pk=post_id, author=request.user)

    if  request.method=='POST':
        form=postforms(request.POST, request.FILES, instance=post)
        if form.is_valid():
            form=form.save( commit =False)
            form.author=request.user
            form.save()
            return redirect('all_posts')
    else:
        form=postforms(instance=post)
    return render(request, 'new_post.html', {'form': form})

@login_required
def delete_post(request, post_id):
    post=get_object_or_404(Post, pk=post_id, author=request.user)
    if request.method=='POST':
        post.delete()
        return redirect('all_posts')
    return render(request, 'delete_post.html', {'post': post})

def register(request):
    if request.method=='POST':
        form=UserRegistrationForm(request.POST)
        if form.is_valid():
            user=form.save(commit=False)
            user.set_password(form.cleaned_data['password1'])
            user.save()
            login(request, user)
            return redirect('all_posts')
        pass
    else:
        form=UserRegistrationForm()
    return render(request, 'registration/register.html', {'form': form})

    