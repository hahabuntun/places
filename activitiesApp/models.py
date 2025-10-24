from django.db import models

class Place(models.Model):
    """Модель для представления места на интерактивной карте Москвы.
    
    Attrs:
        title (str): Название места (максимум 200 символов).
        short_description (str): Краткое описание места (опционально).
        long_description (str): Подробное описание места (опционально).
        latitude (float): Широта географических координат места.
        longitude (float): Долгота географических координат места.
    """
    title = models.CharField("Название", max_length=200)
    short_description = models.TextField("Короткое описание", blank=True)
    long_description = models.TextField("Полное описание", blank=True)
    latitude = models.FloatField("Широта")
    longitude = models.FloatField("Долгота")

    class Meta:
        verbose_name = "Место"
        verbose_name_plural = "Места"

    def __str__(self):
        return self.title

class PlaceImage(models.Model):
    """Модель для представления изображения, связанного с местом.
    
    Attrs:
        place (ForeignKey): Ссылка на связанное место.
        image (ImageField): Поле для загрузки изображения (сохраняется в 'places/').
        order (int): Порядок отображения изображения (по умолчанию 0).
    """
    place = models.ForeignKey(Place, on_delete=models.CASCADE, related_name="images", verbose_name="Место")
    image = models.ImageField("Фотография", upload_to="places/")
    order = models.PositiveIntegerField("Порядок", default=0)

    class Meta:
        verbose_name = "Фотография"
        verbose_name_plural = "Фотографии"
        ordering = ["order"]

    def __str__(self):
        return f"Фото для {self.place.title}"