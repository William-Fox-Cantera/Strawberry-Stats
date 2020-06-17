from django.apps import AppConfig


class PlantsConfig(AppConfig):
    name = 'plants'

    def ready(self):
        import plants.signals
