from django.apps import AppConfig

class BankConfig(AppConfig):
    name = 'bank'

    def ready(self):
        import bank.signals

class BankConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'bank'
