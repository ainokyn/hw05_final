from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render

from .forms import CommentForm, PostForm
from .models import Follow, Group, Post, User


def index(request):
    """Function for handling a request to the main page."""
    posts = Post.objects.all()
    paginator = Paginator(posts, settings.NUM_POSTS_ON_PAGE)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    template = 'posts/index.html'
    сontext: dict = {
        'page_obj': page_obj,
    }
    return render(request, template, сontext)


def group_posts(request, slug):
    """Function for processing a request to a group page."""
    group = get_object_or_404(Group, slug=slug)
    post = group.posts.all()
    paginator = Paginator(post, settings.NUM_POSTS_ON_PAGE)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context: dict = {
        'group': group,
        'page_obj': page_obj,
    }
    return render(request, 'posts/group_list.html', context)


def profile(request, username):
    author = get_object_or_404(User, username=username)
    posts = author.posts.all()
    paginator = Paginator(posts, settings.NUM_POSTS_ON_PAGE)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    num_post = posts.count()
    following = False
    if request.user.is_authenticated and author.following.filter(
            user=request.user):
        following = True
    context = {
        'author': author,
        'page_obj': page_obj,
        'num_post': num_post,
        'following': following,
    }
    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    num = post.author.posts.count()
    form = CommentForm()
    comments = post.comments.filter(post_id=post_id)
    context = {
        'post': post,
        'num': num,
        'form': form,
        'comments': comments,
    }
    return render(request, 'posts/post_detail.html', context)


@login_required
def post_create(request):
    if request.method == "POST":
        form = PostForm(request.POST,
                        files=request.FILES or None)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return redirect('post:profile', username=request.user.username)
    else:
        form = PostForm()
    return render(request, 'posts/create_post.html', {'form': form})


@login_required
def post_edit(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    form = PostForm(request.POST or None,
                    files=request.FILES or None,
                    instance=post)
    if post.author != request.user:
        return redirect('post:post_detail', post_id=post.id)
    if form.is_valid():
        post.save()
        return redirect('post:post_detail', post_id=post.id)
    return render(request,
                  'posts/create_post.html', {'form': form, 'is_edit': True})


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('post:post_detail', post_id=post_id)


@login_required
def follow_index(request):
    posts = Post.objects.filter(author__following__user=request.user).all()
    paginator = Paginator(posts, settings.NUM_POSTS_ON_PAGE)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {'page_obj': page_obj, }
    return render(request, 'posts/follow.html', context)


@login_required
def profile_follow(request, username):
    author = get_object_or_404(User, username=username)
    if not Follow.objects.filter(user=request.user, author=author).exists():
        if author != request.user:
            Follow.objects.create(user=request.user, author=author)
            return redirect('post:follow_index')
    return redirect('post:profile', username=username)


@login_required
def profile_unfollow(request, username):
    author = get_object_or_404(User, username=username)
    if Follow.objects.filter(user=request.user, author=author).exists():
        Follow.objects.filter(user=request.user, author=author).delete()
        return redirect('post:follow_index')
    return redirect('post:profile', username=username)
