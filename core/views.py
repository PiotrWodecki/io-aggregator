import csv
import json
from io import StringIO

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.shortcuts import render
from django.views.decorators.csrf import csrf_protect

from ceneoscraper import bs4_scraper as scraper
from core.validators import validate_multi_search_files_row
from .forms import MultiSearchFrom
from .forms import SearchForm
from .models import User
from .models import Product
from .models import Cart


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
    if not request.session.session_key:
        request.session.save()

    # Google says a session lasts two weeks by default
    session_id = request.session.session_key

    cartstring = search_word["product"]

    cartjson = json.loads(cartstring.replace("'", '"'))

    cartjson["quantity"] = int(search_word["getNumber"])

    # Check if user is logged in
    if request.user.is_authenticated:
        user = User(request.user)
        # Move this to where registration is
        # So the cart is created at signing-up
        cart = Cart(user=user)

    # Hard to test, probably need refactoring
    # Chack if cart with X session exist
    elif len(Cart.objects.filter(session=session_id)) != 0:
        print("Here")
        cart = Cart.objects.filter(session=session_id)[0]

    # Save new cart otherwise
    else:
        cart = Cart(
            session=session_id,
        )
        cart.save()


    # To save data
    product = Product(
        cart=Cart.objects.filter(session=session_id)[0],
        url=cartjson["link"],
        image_url=cartjson["image"],
        name=cartjson["name"],
        price=cartjson["price"],
        quantity=cartjson["quantity"],
    )


    # Save selected product to DB
    product.save()

    # Example of query
    print(Product.objects.filter(cart=cart).values())

    # Stay on same site
    return redirect(request.META["HTTP_REFERER"])


# Here be function to select cart from database
def selectcart(request):
    search_login = request.POST
    # c = CartMemory.objects.filter(login=search_login["login"]).values()

    # I forgor what to return 💀
    return redirect(request.META["HTTP_REFERER"])
