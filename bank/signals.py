import logging
from django.apps import apps
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User

logger = logging.getLogger(__name__)

@receiver(post_save, sender=User)
def create_user_account(sender, instance, created, **kwargs):
    if created:
        try:
            Account = apps.get_model('bank', 'Account')
            account = Account(user=instance, account_type='savings')
            account.account_number = account.random_account_generator()
            account.save()
            logger.info(f"Account created for user {instance.username}")
        except Exception as e:
            logger.error(f"Error creating account for user {instance.username}: {e}")
