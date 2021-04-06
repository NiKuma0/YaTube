from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render
from django.urls.base import reverse

from .forms import PostForm, CommentForm
from .models import Comment, Group, Post, User, Follow


def index(request):
    posts = Post.objects.all()
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(request, 'index.html', {
        'page': page,
    })


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    posts = group.posts.all()
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(request, 'group.html', {
        'page': page,
        'group': group,
    })


@login_required
def new_post(request):
    author_post = Post(author=request.user)
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=author_post
    )
    if not form.is_valid():
        return render(request, 'new_post.html', {'form': form})
    form.save()
    return redirect('index')


@login_required
def post_edit(request, username, post_id):
    post = get_object_or_404(Post, id=post_id, author__username=username)
    if request.user.username != username:
        return redirect(reverse('post', args=(username, post_id)))
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post
    )
    if form.is_valid():
        form.save()
        return redirect(reverse('post', args=(username, post_id)))
    return render(request, 'new_post.html', {
        'form': form,
        'post': post,
    })


def profile(request, username):
    author = get_object_or_404(User, username=username)
    if request.user.is_authenticated:
        following = Follow.objects.filter(
            user=request.user, author=author).exists()
    else:
        following = False
    posts = author.posts.all()
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(request, 'profile.html', {
        'author': author,
        'page': page,
        'following': following
    })


def post_view(request, username, post_id):
    post = get_object_or_404(Post, id=post_id, author__username=username)
    comments = post.comments.all()
    form = CommentForm(
        request.POST or None,
    )
    return render(request, 'post.html', {
        'post': post,
        'author': post.author,
        'form': form,
        'comments': comments
    })


@login_required
def add_comment(request, username, post_id):
    post = get_object_or_404(Post, id=post_id, author__username=username)
    author_comment = Comment(author=request.user, post=post)
    form = CommentForm(
        request.POST or None,
        instance=author_comment
    )
    if form.is_valid():
        form.save()
    return redirect(reverse('post', args=(username, post_id)))


def page_not_found(request, exception):
    return render(
        request,
        'misc/404.html',
        {'path': request.path},
        status=404
    )


def server_error(request):
    return render(request, 'misc/500.html', status=500)


@login_required
def follow_index(request):
    authors = [
        obj.author for obj in Follow.objects.filter(user=request.user).all()
    ]
    posts = Post.objects.filter(author__in=authors).all()
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(request, 'follow.html', {
        'page': page,
        'paginator': paginator
    })


@login_required
def profile_follow(request, username):
    author = User.objects.get(username=username)
    follow_obj = Follow.objects.filter(author=author, user=request.user)
    if author != request.user and not follow_obj.exists():
        Follow.objects.create(user=request.user, author=author).save()
    return redirect(reverse('profile', args=(username,)))


@login_required
def profile_unfollow(request, username):
    author = User.objects.get(username=username)
    Follow.objects.get(user=request.user, author=author).delete()
    return redirect(reverse('profile', args=(username,)))
