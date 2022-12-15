from django.shortcuts import render
from django.shortcuts import redirect
from .forms import SearchForm


def home(request):
    return render(request, "base.html")


def search(request):
    context = {'form': SearchForm()}
    return render(request, 'shopping/search.html', context)
