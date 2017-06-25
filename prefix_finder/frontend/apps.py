from django.apps import AppConfig

class FrontendConfig(AppConfig):
    name = 'frontend'

    def ready(self):print("READY!")
        
        refresh_data()
