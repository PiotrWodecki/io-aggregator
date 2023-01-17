from django.db import models


class Product(models.Model):
    class Category(models.IntegerChoices):
        Medicine = 0
        Cosmetics = 1

    url = models.URLField(max_length=2048, primary_key=True)
    shop_url = models.URLField(max_length=200)
    image_url = models.URLField(max_length=200)
    name = models.CharField(max_length=100)
    quantity = models.IntegerField()
    lowest_price = models.DecimalField(max_digits=100, decimal_places=2)

    def __str__(self):
        return self.name


class Seller(models.Model):
    url = models.URLField(max_length=200, primary_key=True)
    image = models.URLField(max_length=200)

    def __str__(self):
        return f"{self.url}"


class ProductOffer(models.Model):
    product_buy_url = models.URLField(max_length=2048, primary_key=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=100, decimal_places=2)
    seller = models.ForeignKey(Seller, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.product} offered by {self.seller.url}"


class Delivery(models.Model):
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=100, decimal_places=2)
    product_offer = models.ForeignKey(ProductOffer, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.name} for {self.price}"
