from django.shortcuts import render, redirect, get_object_or_404
from .models import *
from django.contrib import messages
from bs4 import BeautifulSoup
import requests
from .forms import *


def home_view(request):
    posts = Post.objects.all()
    return render(request, 'a_posts/home.html', {'posts': posts})


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
            post.artitst = artist

            post.save()
            return redirect('home')

    return render(request, 'a_posts/post_create.html', {'form': form})


def post_delete_view(request, pk):
    post = get_object_or_404(Post, id=pk)

    if request.method == 'POST':
        post.delete()
        messages.success(request, 'Post deleted')
        return redirect('home')

    return render(request, 'a_posts/post_delete.html', {'post': post})


def post_edit_view(request, pk):
    post = get_object_or_404(Post, id=pk)

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
    return render(request, 'a_posts/post_page.html', {'post': post})
