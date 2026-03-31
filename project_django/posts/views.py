from django.shortcuts import render
from .models import Post , Comment, CustomUser
from .forms import postforms, UserRegistrationForm ,UserEditForm, commentForm
from django.shortcuts import get_object_or_404, redirect
from django.http import HttpResponseForbidden
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login ,logout, authenticate
from django.db.models import Q
# from django.contrib.auth.models import User
from django.db.models import Exists, OuterRef
from django.core.paginator import Paginator
from django.contrib import messages


def user_profile(request, username):
    user = get_object_or_404(CustomUser, username=username)
    posts = Post.objects.filter(author=user).order_by('-created_at')
    comments = Comment.objects.filter(author=user).annotate(
        post_exists=Exists(Post.objects.filter(pk=OuterRef('post_id')))
    ).order_by('-created_at')
    user_profile_picture = user.profile_picture.url if user.profile_picture else None
    return render(request, 'profile.html', {
        'profile_user': user,
        'posts': posts,
        'comments': comments,
        'user_profile_picture': user_profile_picture
    })

@login_required
def edit_user(request,username):
    user = get_object_or_404(CustomUser, username=username)
    if user != request.user:
        return HttpResponseForbidden("You can only edit your own profile.")
    form=UserEditForm(instance=user)
    if request.method=='POST':
        form=UserEditForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('user_profile', username=username)
    else:
        form=UserEditForm(instance=user)
    return render(request, 'edit_profile.html', {'form': form})


def home(request):   
    q=request.GET.get('q', '') 
    if q and q.strip():
        posts = Post.objects.select_related('author').filter(Q(title__icontains=q) | Q(content__icontains=q)).order_by('-created_at')
    else:
        posts = Post.objects.select_related('author').all().order_by('-created_at')    #read data

    paginator = Paginator(posts, 15)  # 15 posts per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    comments = Comment.objects.select_related('author').annotate(
        post_exists=Exists(Post.objects.filter(pk=OuterRef('post_id')))
    ).order_by('-created_at')[:5]
    return render(request, 'home.html', {'page_obj': page_obj,'q': q, 'comments': comments})

@login_required
def new_post(request):         #CREATE DATA
    if request.method=='POST':
        form=postforms(request.POST, request.FILES)
        if form.is_valid():
            form=form.save( commit =False)
            form.author=request.user
            form.save()
            messages.success(request, 'Post created successfully!')
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
            messages.success(request, 'Post updated successfully!')
            return redirect('home')
    else:
        form=postforms(instance=post)
    return render(request, 'new_post.html', {'form': form})

@login_required
def delete_post(request, post_id):
    post=get_object_or_404(Post, pk=post_id, author=request.user)
    if request.method=='POST':
        post.delete()
        messages.success(request, 'Post deleted successfully!')
        return redirect('home')
    return render(request, 'delete_post.html', {'post': post})


def post(request,post_id):
    post=get_object_or_404(Post,pk=post_id)
    comments=Comment.objects.filter(post=post).order_by('-created_at')
    if request.method=='POST':
        form=commentForm(request.POST)
        if form.is_valid():
            new_comment=form.save(commit=False)
            new_comment.author=request.user
            new_comment.post=post
            new_comment.save()           
            messages.success(request, 'Comment added successfully!')   
            return redirect('post', post_id=post_id)
    else:
        form=commentForm()

    return render(request, 'post.html', {'post': post, 'comments': comments, 'form': form})


@login_required
def delete_comment(request, comment_id):
    comment = get_object_or_404(Comment, pk=comment_id, author=request.user)
    post = comment.post
    if request.method == 'POST':
        comment.delete()        
        messages.success(request, 'Comment deleted successfully!')     
        return redirect('post', post_id=post.id)
    return redirect('post', post_id=post.id)

@login_required
def edit_comment(request, comment_id):
    comment = get_object_or_404(Comment, pk=comment_id, author=request.user)
    if request.method == 'POST':
        form = commentForm(request.POST, instance=comment)
        if form.is_valid():
            form.save()
            messages.success(request, 'Comment updated successfully!')
            return redirect('post', post_id=comment.post.id)
    else:
        form = commentForm(instance=comment)
    return render(request, 'edit_comment.html', {'form': form, 'comment': comment})

def login_view(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']
        user = authenticate(request, email=email, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, 'Logged in successfully!')
            return redirect('home')
        else:
            messages.error(request, 'Invalid email or password')
            return render(request, 'registration/login.html')
    return render(request, 'registration/login.html')

@login_required
def logout_view(request):
    logout(request)
    return redirect('home')  

def register(request):
    if request.method=='POST':
        form=UserRegistrationForm(request.POST)
        if form.is_valid():
            user=form.save(commit=False)
            user.set_password(form.cleaned_data['password1'])
            user.save()
            login(request, user)
            messages.success(request, 'Account created successfully!')
            return redirect('home')
        
    else:
        form=UserRegistrationForm()
    return render(request, 'registration/register.html', {'form': form})

    