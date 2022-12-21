from django.shortcuts import render

from .forms import SearchForm
from ceneoscraper import bs4_scraper as scraper


def search(request):
    form = SearchForm()
    return render(request, "shopping/search.html", {"form": form})


def select_product(request):
    product_query = request.GET.get("q")
    shop_selection = request.GET.get("shop")
    return render(
        request,
        "shopping/select_product.html",
        {"product_query": product_query, "shop_selection": shop_selection},
    )
