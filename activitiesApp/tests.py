from django.test import TestCase, Client
from django.urls import reverse
from .models import Place, PlaceImage
from django.core.files.uploadedfile import SimpleUploadedFile
import json
import os
from django.conf import settings


class PlaceModelTest(TestCase):
    """Тесты для модели Place"""
    
    def setUp(self):
        """Настройка тестовых данных"""
        self.place = Place.objects.create(
            title="Тестовое место",
            short_description="Короткое описание",
            long_description="<h1>Длинное описание</h1>",
            latitude=55.7558,
            longitude=37.6173
        )
    
    def test_place_creation(self):
        """Тест создания места"""
        self.assertEqual(self.place.title, "Тестовое место")
        self.assertEqual(self.place.latitude, 55.7558)
        self.assertEqual(self.place.longitude, 37.6173)
        self.assertTrue(isinstance(self.place, Place))
    
    def test_place_str_representation(self):
        """Тест строкового представления места"""
        self.assertEqual(str(self.place), "Тестовое место")


class PlaceImageModelTest(TestCase):
    """Тесты для модели PlaceImage"""
    
    def setUp(self):
        """Настройка тестовых данных"""
        self.place = Place.objects.create(
            title="Тестовое место для изображений",
            latitude=55.7558,
            longitude=37.6173
        )
        
        # Создаем тестовое изображение
        self.test_image = SimpleUploadedFile(
            "test_image.jpg",
            b"file_content",
            content_type="image/jpeg"
        )
        
        self.place_image = PlaceImage.objects.create(
            place=self.place,
            image=self.test_image,
            order=0
        )
    
    def test_place_image_creation(self):
        """Тест создания изображения места"""
        self.assertEqual(self.place_image.place, self.place)
        self.assertEqual(self.place_image.order, 0)
        self.assertTrue(self.place_image.image.name.startswith('places/test_image'))
    
    def test_place_image_str_representation(self):
        """Тест строкового представления изображения места"""
        expected_str = f"Фото для {self.place.title}"
        self.assertEqual(str(self.place_image), expected_str)
    
    def test_place_image_ordering(self):
        """Тест порядка сортировки изображений"""
        # Создаем второе изображение с большим порядком
        second_image = SimpleUploadedFile(
            "test_image2.jpg",
            b"file_content",
            content_type="image/jpeg"
        )
        
        PlaceImage.objects.create(
            place=self.place,
            image=second_image,
            order=1
        )
        
        images = PlaceImage.objects.filter(place=self.place)
        self.assertEqual(images[0].order, 0)
        self.assertEqual(images[1].order, 1)


class ViewsTest(TestCase):
    """Тесты для представлений"""
    
    def setUp(self):
        """Настройка тестовых данных"""
        self.client = Client()
        self.place = Place.objects.create(
            title="Тестовое место для представлений",
            short_description="Короткое описание",
            long_description="<p>Длинное описание</p>",
            latitude=55.7512,
            longitude=37.6288
        )
        
        # Создаем тестовое изображение
        self.test_image = SimpleUploadedFile(
            "view_test_image.jpg",
            b"file_content",
            content_type="image/jpeg"
        )
        
        self.place_image = PlaceImage.objects.create(
            place=self.place,
            image=self.test_image,
            order=0
        )
    
    def test_map_view(self):
        """Тест главной страницы с картой"""
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'index.html')
        self.assertContains(response, 'Куда пойти — Москва глазами Артёма')
    
    def test_places_geojson_view(self):
        """Тест API GeoJSON всех мест"""
        response = self.client.get(reverse('places_geojson'))
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.content)
        self.assertEqual(data['type'], 'FeatureCollection')
        self.assertIsInstance(data['features'], list)
        
        # Проверяем структуру GeoJSON
        feature = data['features'][0]
        self.assertEqual(feature['type'], 'Feature')
        self.assertEqual(feature['geometry']['type'], 'Point')
        self.assertEqual(feature['properties']['title'], self.place.title)
        self.assertEqual(feature['properties']['placeId'], self.place.id)
    
    def test_place_detail_view(self):
        """Тест API детальной информации о месте"""
        response = self.client.get(reverse('place_detail', args=[self.place.id]))
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.content)
        self.assertEqual(data['title'], self.place.title)
        self.assertEqual(data['description_short'], self.place.short_description)
        self.assertEqual(data['description_long'], self.place.long_description)
        self.assertIsInstance(data['imgs'], list)
    
    def test_place_detail_view_404(self):
        """Тест 404 ошибки для несуществующего места"""
        response = self.client.get(reverse('place_detail', args=[999]))
        self.assertEqual(response.status_code, 404)
    
    def test_places_geojson_empty(self):
        """Тест GeoJSON при отсутствии мест"""
        Place.objects.all().delete()
        
        response = self.client.get(reverse('places_geojson'))
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.content)
        self.assertEqual(data['type'], 'FeatureCollection')
        self.assertEqual(len(data['features']), 0)


class APIIntegrationTest(TestCase):
    """Интеграционные тесты API"""
    
    def setUp(self):
        """Настройка тестовых данных"""
        self.client = Client()
        
        self.place1 = Place.objects.create(
            title="Первое тестовое место",
            short_description="Описание первого места",
            latitude=55.7539,
            longitude=37.6208
        )
        
        self.place2 = Place.objects.create(
            title="Второе тестовое место", 
            short_description="Описание второго места",
            latitude=55.7604,
            longitude=37.6252
        )
    
    def test_geojson_structure(self):
        """Тест структуры GeoJSON ответа"""
        response = self.client.get(reverse('places_geojson'))
        data = json.loads(response.content)
        
        self.assertIn('type', data)
        self.assertIn('features', data)
        self.assertEqual(data['type'], 'FeatureCollection')
        
        for feature in data['features']:
            self.assertIn('type', feature)
            self.assertIn('geometry', feature)
            self.assertIn('properties', feature)
            self.assertIn('title', feature['properties'])
            self.assertIn('placeId', feature['properties'])
            self.assertIn('detailsUrl', feature['properties'])
    
    def test_multiple_places_in_geojson(self):
        """Тест наличия нескольких мест в GeoJSON"""
        response = self.client.get(reverse('places_geojson'))
        data = json.loads(response.content)
        
        self.assertEqual(len(data['features']), 2)
        
        places_titles = [feature['properties']['title'] for feature in data['features']]
        self.assertIn("Первое тестовое место", places_titles)
        self.assertIn("Второе тестовое место", places_titles)


class AdminTest(TestCase):
    """Тесты админ-панели"""
    
    def setUp(self):
        """Настройка тестовых данных"""
        from django.contrib.auth import get_user_model
        User = get_user_model()
        
        self.admin_user = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='password123'
        )
        
        self.client = Client()
        self.client.login(username='admin', password='password123')
        
        self.place = Place.objects.create(
            title="Админ тестовое место",
            latitude=55.7539,
            longitude=37.6208
        )
    
    def test_admin_place_list(self):
        """Тест отображения списка мест в админке"""
        response = self.client.get('/admin/activitiesApp/place/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Админ тестовое место')
    
    def test_admin_place_add(self):
        """Тест добавления нового места через админку"""
        response = self.client.get('/admin/activitiesApp/place/add/')
        self.assertEqual(response.status_code, 200)
    
    def test_admin_place_change(self):
        """Тест редактирования места через админку"""
        response = self.client.get(f'/admin/activitiesApp/place/{self.place.id}/change/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.place.title)


class MediaFilesTest(TestCase):
    """Тесты для работы с медиафайлами"""
    
    def setUp(self):
        """Настройка тестовых данных"""
        self.place = Place.objects.create(
            title="Место с изображениями",
            latitude=55.7539,
            longitude=37.6208
        )
    
    def test_image_upload(self):
        """Тест загрузки изображения"""
        test_image = SimpleUploadedFile(
            "upload_test.jpg",
            b"file_content",
            content_type="image/jpeg"
        )
        
        place_image = PlaceImage.objects.create(
            place=self.place,
            image=test_image,
            order=0
        )
        
        self.assertTrue(place_image.image)
        self.assertTrue(place_image.image.name.startswith('places/upload_test'))
        
        image_path = os.path.join(settings.MEDIA_ROOT, place_image.image.name)
        self.assertTrue(os.path.exists(image_path))