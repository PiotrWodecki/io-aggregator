from django.db import models


class CartMemory(models.Model):
    userId = models.CharField(max_length=30)
    session = models.CharField(max_length=255)
    link = models.CharField(max_length=255)
    price = models.FloatField()
    quantity = models.IntegerField()


class Product(models.Model):
    class Category(models.IntegerChoices):
        Medicine = 0
        Cosmetics = 1

    url = models.URLField(max_length=2048, primary_key=True)
    shop_url = models.URLField(max_length=200)
    image_url = models.URLField(max_length=200)
    name = models.CharField(max_length=100)
    quantity = models.IntegerField()
    price = models.DecimalField(max_digits=100, decimal_places=2)

    def __str__(self):
        return self.name


class Seller(models.Model):
    url = models.URLField(max_length=200, primary_key=True)
    name = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.name} at {self.url}"


class ProductOffer(models.Model):
    product_buy_url = models.URLField(max_length=2048, primary_key=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    seller = models.ForeignKey(Seller, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.product} offered by {self.seller}"


class Delivery(models.Model):
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=100, decimal_places=2)
    product_offer = models.ForeignKey(ProductOffer, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.name} for {self.price}"
