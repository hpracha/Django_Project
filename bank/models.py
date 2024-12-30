from decimal import Decimal
from django.db import models
from django.contrib.auth.models import User
from django.forms import ValidationError
from django.conf import settings
import random
from django.db.models.signals import post_save
from django.dispatch import receiver

@receiver(post_save, sender=User)
def create_user_account(sender, instance, created, **kwargs):
    if created:
        Account.objects.create(user=instance, account_type='current')


class Account(models.Model):
    ACCOUNT_TYPES = [
        ('savings', 'Savings'),
        ('current', 'Current'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='accounts')  
    account_type = models.CharField(max_length=20, choices=ACCOUNT_TYPES)
    account_number = models.CharField(max_length=20, unique=True)
    balance = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))


    def random_account_generator(self):
        first_name = self.user.first_name.upper() if self.user.first_name else "FN"
        last_name = self.user.last_name.upper() if self.user.last_name else "LN"
        
        first_two_letters = first_name[:2]
        last_two_letters = last_name[-2:] 

        random_part = str(random.randint(1000, 9999))

        return f"{first_two_letters}{random_part}{last_two_letters}"


    def save(self, *args, **kwargs):
        if not self.account_number:
            self.account_number = self.random_account_generator()

            while Account.objects.filter(account_number=self.account_number).exists():
                self.account_number = self.random_account_generator()

        super().save(*args, **kwargs)


class Transaction(models.Model):
    TRANSACTION_TYPES = [
        ('deposit', 'Deposit'),
        ('withdrawal', 'Withdrawal'),
        ('transfer', 'Transfer'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE) 
    account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name="transactions")
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPES)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    recipient_account = models.ForeignKey(Account, null=True, blank=True, on_delete=models.CASCADE, related_name="received_transfers")
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.transaction_type.capitalize()} - {self.amount} - {self.user.username}"
    
    def get_sender_name(self):
        if self.transaction_type == 'transfer':
            if self.amount < 0:
                return self.user.get_full_name() or self.user.username
            elif self.amount > 0 and self.account:
                return self.account.user.get_full_name() or self.account.user.username
        return None

    def get_receiver_name(self):
        if self.transaction_type == 'transfer':
            if self.amount > 0:
                return self.user.get_full_name() or self.user.username
            elif self.amount < 0 and self.recipient_account:
                return self.recipient_account.user.get_full_name() or self.recipient_account.user.username
        return None


    def clean(self):
        if self.transaction_type == 'transfer':
            if not self.recipient_account:
                raise ValidationError("Transfer transactions must specify a recipient account.")
            if self.account == self.recipient_account:
                raise ValidationError("Sender and recipient accounts cannot be the same.")