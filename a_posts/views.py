from django.shortcuts import render, redirect
from .models import *
from django import forms
from django.forms import ModelForm
from bs4 import BeautifulSoup
import requests


def home_view(request):
    posts = Post.objects.all()
    return render(request, 'a_posts/home.html', {'posts': posts})


class PostCreateForm(ModelForm):
    class Meta:
        model = Post
        fields = ['url', 'body']
        labels = {
            'body': 'Caption',
        }
        widgets = {
            'body': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Add a caption...', 'class': 'font1 text-4xl'}),
            'url': forms.TextInput(attrs={'placeholder': 'Add url...'}),
        }


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
