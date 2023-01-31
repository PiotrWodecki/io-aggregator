import csv
import ast

from decimal import Decimal
from typing import List

from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.shortcuts import render
from django.contrib import messages
from io import StringIO, BytesIO
from django.views.decorators.csrf import csrf_protect

from ceneoscraper import bs4_scraper as scraper
from .aggregators import (
    aggregate_products_minimize_shops,
    fill_product_offers,
    group_offers_deliveries_prices_by_shop,
)
from core.validators import validate_multi_search_files_row
from .models import Product, ProductOffer, Delivery, User, Cart
from .forms import MultiSearchFrom, SearchForm


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
            list_of_products = request.FILES["file"]
            rendered = []
            csvfile = list_of_products.read().decode("utf-8")
            spam_ereader = csv.reader(StringIO(csvfile), delimiter=",")

            counter = 0
            for line in spam_ereader:
                if len(line) == 0:
                    continue
                counter += 1
                if counter > 10:
                    messages.error(request, "Lista zakupów jest zbyt długa")
                    form = MultiSearchFrom()
                    return render(request, "shopping/search.html", {"form": form})
                validator = validate_multi_search_files_row(line)
                if not validator[0]:
                    messages.error(request, str(validator[1]))
                    form = MultiSearchFrom()
                    return render(request, "shopping/multi_search.html", {"form": form})

            spam_ereader = csv.reader(StringIO(csvfile), delimiter=",")
            count = 0
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
                        "quantity": quantity,
                    },
                )
                count += 1
            # it is used to load products list after add any product to cart
            request.session["multi-search-rendered"] = str(rendered)
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


@csrf_protect
def add_product(request):
    search_word = request.POST
    if not search_word:
        messages.error(request, "Produkt nie został sprecyzowany.")
        return redirect("/", messages)
    if not request.session.session_key:
        request.session.save()
    # Google says a session lasts two weeks by default
    session_id = request.session.session_key
    cart_string = search_word["product"]
    cart_json = ast.literal_eval(cart_string)
    cart_json["quantity"] = int(search_word["getNumber"])

    if not 0 < cart_json["quantity"] <= 10:
        messages.error(request, "Błędna ilość produktu.")
        return redirect(request.META["HTTP_REFERER"], messages)
    # Check if user is logged in
    if request.user.is_authenticated:
        user = User.objects.get(id=request.user.id)
        if len(Cart.objects.filter(user=user)) != 0:
            cart = Cart.objects.get(user=user)
        else:
            cart = Cart(user=user)
    # Check if cart with X session exist
    elif len(Cart.objects.filter(session=session_id)) != 0:
        cart = Cart.objects.get(session=session_id)
    else:
        cart = Cart(session=session_id)
    # limit 10 products in cart
    if len(Product.objects.filter(cart=cart)) >= 10:
        messages.error(request, "Koszyk jest pełny.")
        return redirect("/shopping_cart", messages)
    # To save data
    if len(Product.objects.filter(cart=cart, url=cart_json["link"])) == 0:
        product = Product(
            cart=cart,
            url=cart_json["link"],
            image_url=cart_json["image"],
            name=cart_json["name"],
            price=cart_json["price"],
            quantity=cart_json["quantity"],
            shop_url=cart_json["shop_url"],
        )
    else:
        product = Product.objects.filter(cart=cart, url=cart_json["link"])[0]
        product.quantity = cart_json["quantity"]
    cart.save()
    product.save()

    # if add_product was called in search
    if "/?q=" in request.META["HTTP_REFERER"]:
        return redirect(request.META["HTTP_REFERER"])

    # if add_product was called in multi_search
    try:
        context = str(request.session.get("multi-search-rendered"))
    except (Exception,):
        # Stay on the same site
        return redirect(request.META["HTTP_REFERER"])
    if len(context) > 0:
        # read products from multi_search page from which it was called
        # change to dict from string
        rendered = ast.literal_eval(context)
        product_to_remove = None
        counter = 0
        for record in rendered:
            for element in record["products"]:
                if element["name"] == cart_json["name"]:
                    product_to_remove = counter
                    break
            if product_to_remove is not None:
                break
            counter += 1
        # removing product which was added to cart
        try:
            del rendered[product_to_remove]
        except TypeError:
            # TypeError can be trigger when user went back in web browser and click add to cart
            # something what already is in cart (deleting wants trigger at product which is not in list)
            pass
        # and save it in session variable
        request.session["multi-search-rendered"] = str(rendered)
        form = MultiSearchFrom()
        return render(
            request,
            "shopping/multi_search.html",
            {"rendered": rendered, "form": form},
        )
    messages.error(request, "Nieznany problem, spróbuj jeszcze raz.")
    return redirect(request.META["HTTP_REFERER"], messages)


@csrf_protect
def shopping_cart(request):
    session_id = request.session.session_key
    if request.user.is_authenticated:
        cart = Cart.objects.filter(user_id=request.user.id)
    else:
        cart = Cart.objects.filter(session=session_id)
    products = Product.objects.filter(cart_id__in=cart)
    total_prices = [product.price * product.quantity for product in products]
    content = zip(products, total_prices)
    return render(request, "shopping/shopping_cart.html", {"content": content})


@csrf_protect
def cart_delete(request):
    if request.user.is_authenticated:
        cart = Cart.objects.filter(user_id=request.user.id)
    else:
        cart = Cart.objects.filter(session=request.session.session_key)
    if request.method == "POST":
        carry = request.POST
        url = carry["delete"]
        product = Product.objects.filter(cart_id__in=cart, url=url)
        product.delete()
    return redirect("shopping_cart")
