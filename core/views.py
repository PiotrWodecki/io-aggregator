from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_protect

from .forms import SearchForm
from ceneoscraper import bs4_scraper as scraper
from django.contrib import messages

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


@login_required
def shopping_history(request):
    return render(request, "shopping/shopping_history.html")


@csrf_protect
def add_product(request):
    search_word = request.POST
    s = str(search_word['product'])
    s = s.replace("{", "")
    finalstring = s.replace("}, ", "")
    # print(finalstring)

    # Splitting the string based on , we get key value pairs
    lista = finalstring.split(",")
    dictionary = {}
    for i in lista:
        # Get Key Value pairs separately to store in dictionary
        keyvalue = i.split(": ")
        # Replacing the single quotes in the leading.
        m = keyvalue[0].strip("'").strip(" '")
        dictionary[m] = keyvalue[1].strip("'")

    dictionary['price'] = dictionary['price'].replace('}', '')

    dictionary['quantity'] = int(search_word['getNumber'])

    print(dictionary)

    # To save data
    b = CartMemory(login="testlogin", session="21372", link=dictionary['link'],
                   price=dictionary['price'], quantity=dictionary['quantity'])
    print(b)
    # b.save()

    # Example to get specific row from memory
    # c = CartMemory.objects.filter(login="testlogin").values()
    # It return nice .json
    # for x in c:
    #  print(x)

    # Stay on same side
    return redirect(request.META['HTTP_REFERER'])
