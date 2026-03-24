from django.shortcuts import render
from .models import Post , Comments
from .forms import postforms, UserRegistrationForm , commentForm
from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.db.models import Q
from django.contrib.auth.models import User
from django.db.models import Exists, OuterRef


def user_profile(request, username):
    user = get_object_or_404(User, username=username)
    posts = Post.objects.filter(author=user).order_by('-created_at')
    comments = Comments.objects.filter(author=user).annotate(
        post_exists=Exists(Post.objects.filter(pk=OuterRef('post_id')))
    ).order_by('-created_at')
    return render(request, 'profile.html', {
        'profile_user': user,
        'posts': posts,
        'comments': comments
    })


def home(request):   
    q=request.GET.get('q', '') 
    if q and q.strip():
        posts = Post.objects.filter(Q(title__icontains=q) | Q(content__icontains=q))
    else:
        posts = Post.objects.all().order_by('-created_at')    #read data

    comments = Comments.objects.annotate(
        post_exists=Exists(Post.objects.filter(pk=OuterRef('post_id')))
    ).order_by('-created_at')
    
    return render(request, 'home.html', {'posts': posts,'q': q, 'comments': comments})

@login_required
def new_post(request):         #CREATE DATA
    if request.method=='POST':
        form=postforms(request.POST, request.FILES)
        if form.is_valid():
            form=form.save( commit =False)
            form.author=request.user
            form.save()
            return redirect('home')
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
            return redirect('home')
    else:
        form=postforms(instance=post)
    return render(request, 'new_post.html', {'form': form})

@login_required
def delete_post(request, post_id):
    post=get_object_or_404(Post, pk=post_id, author=request.user)
    if request.method=='POST':
        post.delete()
        return redirect('home')
    return render(request, 'delete_post.html', {'post': post})


def post(request,post_id):
    post=get_object_or_404(Post,pk=post_id)
    comments=Comments.objects.filter(post=post).order_by('-created_at')
    if request.method=='POST':
        form=commentForm(request.POST)
        if form.is_valid():
            new_comment=form.save(commit=False)
            new_comment.author=request.user
            new_comment.post=post
            new_comment.save()
            return redirect('post', post_id=post_id)
    else:
        form=commentForm()

    return render(request, 'post.html', {'post': post, 'comments': comments, 'form': form})


@login_required
def delete_comment(request, comment_id):
    comment = get_object_or_404(Comments, pk=comment_id, author=request.user)
    post = comment.post
    if request.method == 'POST':
        comment.delete()
        return redirect('post', post_id=post.id)
    return redirect('post', post_id=post.id)



def register(request):
    if request.method=='POST':
        form=UserRegistrationForm(request.POST)
        if form.is_valid():
            user=form.save(commit=False)
            user.set_password(form.cleaned_data['password1'])
            user.save()
            login(request, user)
            return redirect('home')
        
    else:
        form=UserRegistrationForm()
    return render(request, 'registration/register.html', {'form': form})

    