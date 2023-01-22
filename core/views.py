import csv
from decimal import Decimal
from typing import List

from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.contrib import messages
from io import StringIO, BytesIO

from ceneoscraper import bs4_scraper as scraper
from .aggregators import (
    aggregate_products_minimize_shops,
    fill_product_offers,
    group_offers_deliveries_prices_by_shop,
)
from .forms import SearchForm
from .forms import MultiSearchFrom
from core.validators import validate_multi_search_files_row
from .models import Product, ProductOffer, Delivery


def search(request):
    form = SearchForm()
    return render(request, "shopping/search.html", {"form": form})


def select_product(request):
    form = SearchForm(request.GET)
    if form.is_valid():
        product_query = form.cleaned_data["q"]
        shop_selection = form.cleaned_data["shop"]
        category = form.cleaned_data["category"]
        search_url = scraper.prepare_link(product_query, category)
        # product lookup can fail for various reasons
        # to combat this we will capture all exceptions
        # and display a simple message to the user
        try:
            products = []
            if int(shop_selection) in [1, 2, 3]:
                products = scraper.get_products(search_url, int(shop_selection))
        except (Exception,):
            messages.error(request, "Wystąpił błąd podczas wyszukiwania produktu")
            return render(request, "shopping/search.html", {"form": form})
        if products is None or len(products) == 0:
            messages.error(request, "Brak wyników wyszukiwania")
        return render(
            request,
            "shopping/select_product.html",
            {
                "product_query": product_query,
                "shop_selection": shop_selection,
                "products": products,
                "form": form,
            },
        )
    return render(request, "shopping/search.html", {"form": form})


def multi_product(request):
    if request.method == "POST":
        form = MultiSearchFrom(request.POST, request.FILES)
        if form.is_valid():
            file = request.FILES["file"]
            count = 0
            rendered = []
            csvfile = file.read().decode("utf-8")
            spam_ereader = csv.reader(StringIO(csvfile), delimiter=",")

            if len(list(spam_ereader)) > 10:
                messages.error(request, "Lista zakupów jest zbyt długa")
                form = MultiSearchFrom()
                return render(request, "shopping/search.html", {"form": form})

            for line in spam_ereader:
                if len(line) == 0:
                    continue
                validator = validate_multi_search_files_row(line)
                if not validator[0]:
                    messages.error(request, str(validator[1]))
                    form = MultiSearchFrom()
                    return render(request, "shopping/multi_search.html", {"form": form})

            spam_ereader = csv.reader(StringIO(csvfile), delimiter=",")
            for line in spam_ereader:
                if len(line) == 0:
                    continue
                product_query = line[0]
                shop_selection = int(line[1])
                category = line[2].strip()
                quantity = int(line[3])
                search_url = scraper.prepare_link(product_query, category)
                products = scraper.get_products(search_url, shop_selection)
                rendered.append(
                    {
                        "id": count,
                        "product_query": product_query,
                        "shop_selection": shop_selection,
                        "products": products,
                    },
                )
                count += 1
            return render(
                request,
                "shopping/multi_search.html",
                {"rendered": rendered, "form": form},
            )
    else:
        form = MultiSearchFrom()
    return render(request, "shopping/multi_search.html", {"form": form})


def aggregate_cart(request):
    products = Product.objects.all()
    fill_product_offers(products)

    aggregated_offers: List[ProductOffer]
    aggregated_deliveries: List[Delivery]
    total_prices: List[Decimal]

    (
        aggregated_offers,
        aggregated_deliveries,
        total_prices,
    ) = aggregate_products_minimize_shops(products)
    grouped_offers_deliveries_prices = group_offers_deliveries_prices_by_shop(
        aggregated_offers, aggregated_deliveries, total_prices
    )

    return render(
        request,
        "shopping/aggregate_cart.html",
        {"grouped_offers_deliveries_prices": grouped_offers_deliveries_prices},
    )


@login_required
def shopping_history(request):
    return render(request, "shopping/shopping_history.html")


def shopping_cart(request):
    return render(request, "shopping/shopping_cart.html")
