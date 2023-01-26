import operator
import time
from decimal import Decimal
from typing import List
from django.db.models import Count, Q

from ceneoscraper.bs4_scraper import get_offers
from core.models import Product, ProductOffer, Seller, Delivery


def fill_product_offers(products: List[Product]) -> None:
    for product in products:
        if "https://ceneo.pl//Click/Offer/?e" in product.url:
            continue
        try:
            offers = get_offers(product.url)
        except (Exception,):
            continue
        for offer in offers:
            try:
                seller, created = Seller.objects.get_or_create(
                    url=offer["shop_url"], image=offer["shop_image"]
                )
                product_offer_model = ProductOffer.objects.create(
                    product=product,
                    product_buy_url=offer["link"],
                    seller=seller,
                    price=offer["price"],
                )
            except (Exception):
                continue

            for delivery in offer["delivery"]:
                delivery_model = Delivery.objects.create(
                    name=delivery["delivery_name"],
                    price=delivery["delivery_cost"],
                    product_offer=product_offer_model,
                )

                delivery_model.save()
            seller.save()
            product_offer_model.save()
        time.sleep(10)


def aggregate_products_minimize_shops(
    products: List[Product],
) -> (List[ProductOffer], List[Delivery], List[Decimal]):
    # This is an NP-hard problem. For details see:
    # https://en.wikipedia.org/wiki/Set_cover_problem
    selected_product_offers: List[ProductOffer] = []
    selected_deliveries: List[Delivery] = []
    total_prices: List[Decimal] = []
    for seller in (
        Seller.objects.filter(productoffer__product__in=products)
        .annotate(
            count=Count(
                "productoffer__product_buy_url",
                filter=operator.invert(
                    Q(productoffer__product_id__in=[selected_product_offers])
                ),
            )
        )
        .distinct()
        .order_by("-count")
    ):
        offers = ProductOffer.objects.filter(
            product__in=products, seller=seller
        ).order_by("product__price")
        for offer in offers:
            if offer.product_id not in [
                offer.product_id for offer in selected_product_offers
            ]:
                try:
                    lowest_price_delivery = (
                        Delivery.objects.filter(product_offer=offer)
                        .order_by("price")
                        .first()
                    )
                except IndexError:
                    lowest_price_delivery = Delivery.objects.create(
                        name="Nieznana dostawa", price=0, product_offer=offer
                    )
                selected_deliveries.append(lowest_price_delivery)
                selected_product_offers.append(
                    ProductOffer(
                        product_buy_url=offer.product_buy_url,
                        price=offer.product.price,
                        seller=offer.seller,
                        product=offer.product,
                    )
                )
                total_prices.append(offer.price * offer.product.quantity)
    for product in products:
        if (
            product.shop_url != ""
            and ProductOffer.objects.filter(product=product).count() == 0
        ):
            selected_product_offers.append(
                ProductOffer(
                    product_buy_url=product.url,
                    price=product.lowest_price,
                    product=product,
                )
            )
            selected_deliveries.append(
                Delivery(
                    name="Nieznana dostawa",
                    price=0,
                    product_offer=selected_product_offers[-1],
                )
            )
            total_prices.append(product.lowest_price * product.quantity)
    return selected_product_offers, selected_deliveries, total_prices


def group_offers_deliveries_prices_by_shop(
    offers: List[ProductOffer], deliveries: List[Delivery], prices: List[Decimal]
) -> dict[Seller, tuple[list[ProductOffer], list[Delivery], list[Decimal]]]:
    grouped_offers = {}
    for offer, delivery, price in zip(offers, deliveries, prices):
        if offer.seller not in grouped_offers:
            grouped_offers[offer.seller] = ([offer], [delivery], [price])
        else:
            grouped_offers[offer.seller][0].append(offer)
            grouped_offers[offer.seller][1].append(delivery)
            grouped_offers[offer.seller][2].append(price)

    return {seller: tuple(zip(*offers)) for seller, offers in grouped_offers.items()}
