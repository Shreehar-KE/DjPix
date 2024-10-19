from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import *
from django.contrib import messages
from bs4 import BeautifulSoup
import requests
from .forms import *


def home_view(request, tag=None):
    if tag:
        posts = Post.objects.filter(tags__slug=tag)
        tag = get_object_or_404(Tag, slug=tag)
    else:
        posts = Post.objects.all()

    categories = Tag.objects.all()
    context = {
        'posts': posts,
        'tag': tag,
        'categories': categories,
    }

    return render(request, 'a_posts/home.html', context)


@login_required
def post_create_view(request):
    form = PostCreateForm()

    if request.method == 'POST':
        form = PostCreateForm(request.POST)

        if form.is_valid():
            post = form.save(commit=False)

            website = requests.get(form.data['url'])
            sourceode = BeautifulSoup(website.text, 'html.parser')

            find_image = sourceode.select(
                'meta[content^="https://live.staticflickr.com/"]')
            image = find_image[0]['content']
            post.image = image

            find_title = sourceode.select('h1.photo-title')
            title = find_title[0].text.strip()
            post.title = title

            find_artist = sourceode.select('a.owner-name')
            artist = find_artist[0].text.strip()
            post.artist = artist

            post.author = request.user

            post.save()
            form.save_m2m()
            return redirect('home')

    return render(request, 'a_posts/post_create.html', {'form': form})


@login_required
def post_delete_view(request, pk):
    post = get_object_or_404(Post, id=pk, author=request.user)

    if request.method == 'POST':
        post.delete()
        messages.success(request, 'Post deleted')
        return redirect('home')

    return render(request, 'a_posts/post_delete.html', {'post': post})


@login_required
def post_edit_view(request, pk):
    post = get_object_or_404(Post, id=pk, author=request.user)

    form = PostEditForm(instance=post)
    if request.method == 'POST':
        form = PostEditForm(request.POST, instance=post)

        if form.is_valid:
            form.save()
            messages.success(request, 'Post updated')
            return redirect('home')
    context = {
        'post': post,
        'form': form
    }
    return render(request, 'a_posts/post_edit.html', context)


def post_page_view(request, pk):
    post = get_object_or_404(Post, id=pk)

    commentform = CommentCreateForm()
    replyform = ReplyCreateForm()
    context = {
        'post': post,
        'commentform': commentform,
        'replyform': replyform,
    }

    return render(request, 'a_posts/post_page.html', context)


@login_required
def comment_sent(request, pk):
    post = get_object_or_404(Post, id=pk)

    if request.method == 'POST':
        form = CommentCreateForm(request.POST)
        if form.is_valid:
            comment = form.save(commit=False)
            comment.author = request.user
            comment.parent_post = post
            comment.save()

    return redirect('post', post.id)


@login_required
def reply_sent(request, pk):
    comment = get_object_or_404(Comment, id=pk)

    if request.method == 'POST':
        form = ReplyCreateForm(request.POST)
        if form.is_valid:
            reply = form.save(commit=False)
            reply.author = request.user
            reply.parent_comment = comment
            reply.save()

    return redirect('post', comment.parent_post.id)


@login_required
def comment_delete_view(request, pk):
    comment = get_object_or_404(Comment, id=pk, author=request.user)

    if request.method == 'POST':
        comment.delete()
        messages.success(request, 'Comment deleted')
        return redirect('post', comment.parent_post.id)

    return render(request, 'a_posts/comment_delete.html', {'comment': comment})


@login_required
def reply_delete_view(request, pk):
    reply = get_object_or_404(Reply, id=pk, author=request.user)

    if request.method == 'POST':
        reply.delete()
        messages.success(request, 'Reply deleted')
        return redirect('post', reply.parent_comment.parent_post.id)

    return render(request, 'a_posts/reply_delete.html', {'reply': reply})


def like_toggle(model):
    def inner_func(func):
        def wrapper(request, *args, **kwargs):
            object = get_object_or_404(model, id=kwargs.get('pk'))
            user_exists = object.likes.filter(
                username=request.user.username).exists()

            if object.author != request.user:
                if user_exists:
                    object.likes.remove(request.user)
                else:
                    object.likes.add(request.user)
            return func(request, object)
        return wrapper
    return inner_func


@login_required
@like_toggle(Post)
def like_post(request, post):
    return render(request, 'snippets/likes.html', {'post': post})


@login_required
@like_toggle(Comment)
def like_comment(request, comment):
    return render(request, 'snippets/likes_comment.html', {'comment': comment})


@login_required
@like_toggle(Reply)
def like_reply(request, reply):
    return render(request, 'snippets/likes_reply.html', {'reply': reply})
