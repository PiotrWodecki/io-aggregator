from django.shortcuts import render

from .forms import SearchForm
from ceneoscraper import bs4_scraper as scraper
from django.contrib import messages
from .forms import MultiSearchFrom


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
        # try:
        products = scraper.get_products(search_url)
        # except (Exception,):
        #     messages.error(request, "Wystąpił błąd podczas wyszukiwania produktu")
        #     return render(request, "shopping/search.html", {"form": form})
        if products is None:
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
            for row in file.readlines():
                line = row.rstrip().decode("utf-8").split(",")
                product_query = line[0]
                shop_selection = line[1]
                category = line[2]
                quantity = line[3]
                print(
                    "q="
                    + product_query
                    + "\nshop="
                    + shop_selection
                    + "\ncategory="
                    + category
                    + "\nquantity="
                    + quantity
                    + "\n"
                )
                search_url = scraper.prepare_link(product_query, category)
                products = scraper.get_products(search_url)
                if products is None:
                    messages.error(request, "Brak wyników wyszukiwania")
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
    return render(request, "shopping/search.html", {"form": form})
