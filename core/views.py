from django.shortcuts import render
from django.shortcuts import redirect
from .forms import SearchForm
from ceneoscraper import bs4_scraper as scraper


def home(request):
    return render(request, "base.html")


def search(request):
    if request.method == "POST":
        item_to_search = request.POST.get("search_item")
        allegro_option = request.POST.get("options")
        context = {"name": item_to_search, "option": allegro_option}
        ready_link = scraper.prepare_link(context.get("name"), "")
        proposals = scraper.get_products(ready_link)
        return render(request, "base.html", {"proposals": proposals})
    else:
        form = SearchForm()
        context = {"form": form}
        return render(request, "shopping/search.html", context)
