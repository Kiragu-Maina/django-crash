from django.db import models
from django.contrib.auth.models import User
# Create your models here.
class Transactions(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    bet = models.IntegerField()
    won = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return str(self.user)