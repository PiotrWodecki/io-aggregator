from django.shortcuts import render
from django.shortcuts import redirect
from .forms import SearchForm
from core.models import Product


def home(request):
    return render(request, "base.html")


def search(request):
    if request.method == "POST":
        item_to_search = request.POST.get("search_item")
        allegro_option = request.POST.get("options")
        context = {
            "name": item_to_search,
            "option": allegro_option
        }
        return render(request, "base.html", {"context": context})
    else:
        form = SearchForm()
        context = {"form": form}
        return render(request, "shopping/search.html", context)
