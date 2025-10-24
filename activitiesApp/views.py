from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404
from .models import Place

def map_view(request):
    """Отображает главную страницу с интерактивной картой.
    
    Args:
        request (HttpRequest): Запрос от клиента.
    
    Returns:
        HttpResponse: Отрендеренный шаблон 'index.html'.
    """
    return render(request, "index.html")

def places_geojson(request):
    """Возвращает данные о всех местах в формате GeoJSON через API.
    
    Args:
        request (HttpRequest): Запрос от клиента.
    
    Returns:
        JsonResponse: Объект GeoJSON с массивом объектов типа Feature.
    """
    features = []
    for place in Place.objects.all():
        features.append({
            "type": "Feature",
            "geometry": {"type": "Point", "coordinates": [place.longitude, place.latitude]},
            "properties": {
                "title": place.title,
                "placeId": place.id,
                "detailsUrl": f"/api/places/{place.id}/",
            },
        })
    return JsonResponse({"type": "FeatureCollection", "features": features})

def place_detail(request, pk):
    """Возвращает подробную информацию о конкретном месте через API.
    
    Args:
        request (HttpRequest): Запрос от клиента.
        pk (int): Первичный ключ места.
    
    Returns:
        JsonResponse: Данные места, включая название, изображения и описания.
    
    Raises:
        Http404: Если место с указанным pk не найдено.
    """
    place = get_object_or_404(Place, pk=pk)
    
    images = [request.build_absolute_uri(img.image.url) for img in place.images.all().order_by('order')]
    
    return JsonResponse({
        "title": place.title,
        "imgs": images,
        "description_short": place.short_description,
        "description_long": place.long_description,
    })