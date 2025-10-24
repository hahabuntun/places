from django.contrib import admin
from .models import Place, PlaceImage
from django.utils.html import format_html
from django_summernote.admin import SummernoteModelAdmin

class PlaceImageInline(admin.TabularInline):
    """Встроенный класс для управления изображениями места в админке.
    
    Attrs:
        model (Model): Модель PlaceImage.
        extra (int): Количество дополнительных пустых форм (1).
        fields (tuple): Поля для отображения ('image', 'image_preview', 'order').
        readonly_fields (tuple): Только для чтения поле 'image_preview'.
    """
    model = PlaceImage
    extra = 1
    fields = ('image', 'image_preview', 'order')
    readonly_fields = ('image_preview',)
    verbose_name = "Фотография"
    verbose_name_plural = "Фотографии"

    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="100" height="100" style="object-fit: cover;" />', obj.image.url)
        return "Нет изображения"
    image_preview.short_description = "Предпросмотр"

@admin.register(Place)
class PlaceAdmin(SummernoteModelAdmin):
    """Класс админки для управления моделью Place.
    
    Attrs:
        list_display (tuple): Поля для отображения в списке ('title', 'latitude', 'longitude', 'image_preview').
        list_display_links (tuple): Поля, по которым можно перейти к редактированию ('title').
        search_fields (tuple): Поля для поиска ('title').
        inlines (list): Встроенные классы (PlaceImageInline).
    """
    list_display = ("title", "latitude", "longitude","image_preview")
    list_display_links = ("title",)
    search_fields = ("title",)
    inlines = [PlaceImageInline]
    fieldsets = (
        (None, {
            "fields": ("title", "short_description", "long_description")
        }),
        ("Координаты", {
            "fields": ("latitude", "longitude")
        }),
    )
    summernote_fields = ('long_description',)

    def image_preview(self, obj):
        """Генерирует HTML-предпросмотр первого изображения места.
        
        Args:
            obj (Place): Объект места.
        
        Returns:
            str: HTML-тег с изображением или сообщение "Нет фото".
        """
        first_image = obj.images.filter(order=0).first()
        if not first_image:
            first_image = obj.images.first()
        
        if first_image and first_image.image:
            return format_html(
                '<img src="{}" width="150" height="150" style="object-fit: cover; border-radius: 5px;" />', 
                first_image.image.url
            )
        return "Нет фото"
    image_preview.short_description = "Фото"
    image_preview.short_description = "📷"