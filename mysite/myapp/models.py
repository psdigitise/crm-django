from django.db import models

class Payment(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=15)
    plan = models.CharField(max_length=100)
    amount = models.FloatField()
    order_id = models.CharField(max_length=200, unique=True,)
    payment_id = models.CharField(max_length=200, blank=True, null=True)
    status = models.CharField(max_length=20, default='created')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.status}"
