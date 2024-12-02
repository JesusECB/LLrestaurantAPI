from django.db import models
from django.contrib.auth.models import User


class MenuItem(models.Model):
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=5, decimal_places=2)
    description = models.TextField()  # Asegúrate de que este campo esté definido

    def __str__(self):
        return self.name


class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='cart_items')
    menu_item = models.ForeignKey('MenuItem', on_delete=models.CASCADE)  # Usa cadena para evitar circular import
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.menu_item.name} x {self.quantity}"


class Order(models.Model):
    STATUS_CHOICES = [
        (0, 'Out for delivery'),
        (1, 'Delivered'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    delivery_crew = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='delivery_orders')
    status = models.IntegerField(choices=STATUS_CHOICES, default=0)
    total = models.DecimalField(max_digits=6, decimal_places=2, default=0.00)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order {self.id} - {self.user.username}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    menu_item = models.ForeignKey('MenuItem', on_delete=models.CASCADE)  # Usa cadena para evitar circular import
    quantity = models.PositiveIntegerField(default=1)
    unit_price = models.DecimalField(max_digits=6, decimal_places=2)
    price = models.DecimalField(max_digits=6, decimal_places=2)

    def __str__(self):
        return f"{self.quantity}x {self.menu_item.name} (Order {self.order.id})"
