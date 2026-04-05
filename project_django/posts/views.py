from django.shortcuts import render
from .models import Post , Comment, CustomUser
from .forms import postforms, UserRegistrationForm ,UserEditForm, commentForm
from django.shortcuts import get_object_or_404, redirect
from django.http import HttpResponseForbidden
from django.contrib.auth.decorators import login_required, cache_page
from django.contrib.auth import login ,logout, authenticate
from django.db.models import Q, Prefetch
# from django.contrib.auth.models import User NOT USING DEFAULT MODEL
from django.db.models import Exists, OuterRef
from django.core.paginator import Paginator
from django.contrib import messages
from django.core.cache import cache
from functools import lru_cache


def get_cache_key(cache_type, identifier):
    """Get versioned cache key for better invalidation control"""
    version = cache.get(f'{cache_type}_version', 1)
    return f'{cache_type}_v{version}_{identifier}'


def invalidate_cache_version(cache_type):
    """Increment cache version to invalidate all keys of this type"""
    current_version = cache.get(f'{cache_type}_version', 1)
    cache.set(f'{cache_type}_version', current_version + 1, None)  # No expiration


def bulk_invalidate_cache(*cache_types):
    """Invalidate multiple cache types at once"""
    for cache_type in cache_types:
        invalidate_cache_version(cache_type)


def get_cached_user(user_id, timeout=3600):
    """Cache User object to avoid repeated DB lookups"""
    cache_key = get_cache_key('user_obj', user_id)
    return cache.get_or_set(cache_key,
        lambda: CustomUser.objects.get(id=user_id),
        timeout)


# Database Query Caching Functions
def get_cached_user_posts(user_id, timeout=1800):
    """Cache expensive user posts query with optimized db lookups"""
    cache_key = get_cache_key('query_user_posts', user_id)
    return cache.get_or_set(cache_key, 
        lambda: list(Post.objects.select_related('author').filter(
            author_id=user_id
        ).order_by('-created_at')),
        timeout)


def get_cached_user_comments(user_id, timeout=1800):
    """Cache expensive user comments query with optimized db lookups"""
    cache_key = get_cache_key('query_user_comments', user_id)
    return cache.get_or_set(cache_key,
        lambda: list(Comment.objects.select_related('author', 'post').filter(
            author_id=user_id
        ).annotate(
            post_exists=Exists(Post.objects.filter(pk=OuterRef('post_id')))
        ).order_by('-created_at')),
        timeout)


def get_cached_posts_search(query='', timeout=300):
    """Cache expensive posts search query"""
    cache_key = get_cache_key('query_posts_search', query or 'all')
    return cache.get_or_set(cache_key,
        lambda: list(
            Post.objects.select_related('author').filter(
                Q(title__icontains=query) | Q(content__icontains=query)
            ).order_by('-created_at') if query and query.strip()
            else Post.objects.select_related('author').all().order_by('-created_at')
        ),
        timeout)


def get_cached_post_comments(post_id, timeout=600):
    """Cache expensive post comments query with optimized db lookups"""
    cache_key = get_cache_key('query_post_comments', post_id)
    return cache.get_or_set(cache_key,
        lambda: list(Comment.objects.select_related('author').filter(
            post_id=post_id
        ).order_by('-created_at')),
        timeout)


def get_cached_recent_comments(limit=5, timeout=300):
    """Cache expensive recent comments query"""
    cache_key = get_cache_key('query_recent_comments', f'limit_{limit}')
    return cache.get_or_set(cache_key,
        lambda: list(Comment.objects.select_related('author').annotate(
            post_exists=Exists(Post.objects.filter(pk=OuterRef('post_id')))
        ).order_by('-created_at')[:limit]),
        timeout)


def user_profile(request, username):
    cache_key = get_cache_key('user_profile', username)
    user_data = cache.get(cache_key)
    if user_data is None:
        user = get_object_or_404(CustomUser, username=username)
        
        # Use cached queries
        posts = get_cached_user_posts(user.id)
        comments = get_cached_user_comments(user.id)
        user_profile_picture = user.profile_picture.url if user.profile_picture else None

        user_data = {
            'profile_user': user,
            'posts': posts,
            'comments': comments,
            'user_profile_picture': user_profile_picture
        }

        # Cache for 30 minutes
        cache.set(cache_key, user_data, 1800)

    return render(request, 'profile.html', user_data)

@login_required
def edit_user(request,username):
    user = get_object_or_404(CustomUser, username=username)
    if user != request.user:
        return HttpResponseForbidden("You can only edit your own profile.")
    if request.method=='POST':
        form=UserEditForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            # Bulk invalidate all user-related caches
            bulk_invalidate_cache('user_profile', 'query_user_posts', 
                                 'query_user_comments', 'user_obj')
            return redirect('user_profile', username=username)
    else:
        form=UserEditForm(instance=user)
    return render(request, 'edit_profile.html', {'form': form})


def home(request):   
    q = request.GET.get('q', '')
    posts = None
    
    # Only cache searches with 3+ characters
    if len(q) > 2:
        cache_key = get_cache_key('posts', f'search_{q}')
        posts = cache.get(cache_key)
        
        if posts is None:
            posts = get_cached_posts_search(q)
            cache.set(cache_key, posts, 300)
    else:
        # Use cached query for all posts
        posts = get_cached_posts_search('')
    
    paginator = Paginator(posts, 15)  # 15 posts per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Use cached recent comments
    comments = get_cached_recent_comments(5)
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
            # Bulk invalidate related caches
            bulk_invalidate_cache('posts', 'query_posts_search', 'query_user_posts')
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
            # Bulk invalidate related caches
            bulk_invalidate_cache('posts', 'query_posts_search', 'query_user_posts')
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
        # Bulk invalidate related caches
        bulk_invalidate_cache('posts', 'query_posts_search', 'query_user_posts')
        return redirect('home')
    return render(request, 'delete_post.html', {'post': post})


def post(request,post_id):
    cache_key = get_cache_key('post_detail', post_id)
    cached_data = cache.get(cache_key)
    if cached_data is None:
        post_obj = get_object_or_404(Post, pk=post_id)
        # Use cached query for comments
        comments = get_cached_post_comments(post_id)
        cached_data = {
            'post': post_obj,
            'comments': comments
        }
        # Cache for 10 minutes
        cache.set(cache_key, cached_data, 600)
    else:
        post_obj = cached_data['post']
        comments = cached_data['comments']

    if request.method == 'POST':
        form = commentForm(request.POST)
        if form.is_valid():
            new_comment = form.save(commit=False)
            new_comment.author = request.user
            new_comment.post = post_obj
            new_comment.save()
            messages.success(request, 'Comment added successfully!')
            # Bulk invalidate all relevant caches
            bulk_invalidate_cache('post_detail', 'query_post_comments', 
                                 'query_user_comments', 'query_recent_comments')
            return redirect('post', post_id=post_id)
    else:
        form = commentForm()

    return render(request, 'post.html', {'post': post_obj, 'comments': comments, 'form': form})


@login_required
def delete_comment(request, comment_id):
    comment = get_object_or_404(Comment, pk=comment_id, author=request.user)
    post = comment.post
    if request.method == 'POST':
        comment.delete()
        messages.success(request, 'Comment deleted successfully!')
        # Bulk invalidate all relevant caches
        bulk_invalidate_cache('post_detail', 'query_post_comments',
                             'query_user_comments', 'query_recent_comments')
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
            # Bulk invalidate all relevant caches
            bulk_invalidate_cache('post_detail', 'query_post_comments',
                                 'query_user_comments', 'query_recent_comments')
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

    