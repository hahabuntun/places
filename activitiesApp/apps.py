from django.apps import AppConfig


class ActivitiesappConfig(AppConfig):
    """Конфигурация приложения activitiesApp.
    
    Attrs:
        default_auto_field (str): Тип первичного ключа по умолчанию.
        name (str): Имя приложения.
        verbose_name (str): Отображаемое название приложения в админке.
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'activitiesApp'
    verbose_name = ("Места")
