import csv
import json
from django.contrib.auth.decorators import login_required

from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_protect
from django.shortcuts import render
from django.contrib import messages
from io import StringIO

from ceneoscraper import bs4_scraper as scraper
from .forms import SearchForm
from .forms import MultiSearchFrom
from core.validators import validate_multi_search_files_row

from .models import CartMemory


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
            products = scraper.get_products(search_url)
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
            if spam_ereader.line_num > 10:
                messages.error(request, "Lista zakupów jest zbyt długa")
                form = MultiSearchFrom()
                return render(request, "shopping/search.html", {"form": form})
            for line in spam_ereader:
                if len(line) == 0:
                    continue
                if not validate_multi_search_files_row(line):
                    messages.error(request, "Błąd w liście zakupów")
                    form = MultiSearchFrom()
                    return render(request, "shopping/multi_search.html", {"form": form})
                product_query = line[0]
                shop_selection = line[1]
                category = line[2]
                quantity = line[3]
                search_url = scraper.prepare_link(product_query, category)
                products = scraper.get_products(search_url)
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


@login_required
def shopping_history(request):
    return render(request, "shopping/shopping_history.html")


@csrf_protect
def add_product(request):
    search_word = request.POST
    s = search_word["product"]

    early_product = json.loads(s.replace("'", '"'))

    early_product["quantity"] = int(search_word["getNumber"])

    # To save data
    product = CartMemory(
        login="testlogin",
        session="21372",
        link=early_product["link"],
        price=early_product["price"],
        quantity=early_product["quantity"],
    )

    product.save()

    # Stay on same side
    return redirect(request.META["HTTP_REFERER"])


# Here be function to select cart from database
def selectCart(request):
    search_login = request.POST
    c = CartMemory.objects.filter(login=search_login["login"]).values()

    # I forgor what to return 💀
    return redirect(request.META["HTTP_REFERER"])
