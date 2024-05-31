from django.apps import AppConfig


class MainConfig(AppConfig):
    name = 'home'

    def ready(self):
        from . import updaters
        updaters.start()
