from django.db import models


class Product(models.Model):
    class Category(models.IntegerChoices):
        Medicine = 0
        Cosmetics = 1

    url = models.URLField(max_length=200, primary_key=True)
    name = models.CharField(max_length=100)
    description = models.TextField()
    category = models.CharField(max_length=20, choices=Category.choices)

    def __str__(self):
        return self.name


class Seller(models.Model):
    url = models.URLField(max_length=200, primary_key=True)
    name = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.name} at {self.url}"


class ProductOffer(models.Model):
    product_buy_url = models.URLField(max_length=200, primary_key=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    seller = models.ForeignKey(Seller, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.product} offered by {self.seller}"


class Delivery(models.Model):
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    product_offer = models.ForeignKey(ProductOffer, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.name} for {self.price}"


class CartMemory(models.Model):
    login = models.CharField(max_length=30)
    link = models.CharField(max_length=255)
    thumbnail = models.URLField(max_length=200)
    price = models.FloatField()
    quantity = models.IntegerField()
