import pytest
from django.urls import reverse
from django.test import Client
from gallery.models import Category, Image
from datetime import date

@pytest.fixture
def client():
    return Client()

@pytest.fixture
def setup_categories():
    category1 = Category.objects.create(name="Природа")
    category2 = Category.objects.create(name="Місто")
    image1 = Image.objects.create(
        title="Тестове зображення 1",
        image="gallery_images/test1.jpg",
        created_date=date(2025, 5, 23),
        age_limit=18
    )
    image1.categories.add(category1)
    image2 = Image.objects.create(
        title="Тестове зображення 2",
        image="gallery_images/test2.jpg",
        created_date=date(2025, 5, 23),
        age_limit=16
    )
    image2.categories.add(category2)
    return category1, category2

@pytest.mark.django_db
def test_gallery_view_status_code(client, setup_categories):
    """Перевіряє, чи повертає gallery_view статус 200"""
    response = client.get(reverse('gallery:gallery'))
    assert response.status_code == 200

@pytest.mark.django_db
def test_gallery_view_template(client, setup_categories):
    """Перевіряє, чи використовується правильний шаблон gallery.html"""
    response = client.get(reverse('gallery:gallery'))
    assert 'gallery.html' in [t.name for t in response.templates]

@pytest.mark.django_db
def test_gallery_view_context(client, setup_categories):
    """Перевіряє, чи передаються всі категорії в контексті"""
    response = client.get(reverse('gallery:gallery'))
    assert 'categories' in response.context
    categories = response.context['categories']
    assert len(categories) == 2
    assert categories[0].name == "Природа"
    assert categories[1].name == "Місто"
    assert categories[0].image_set.count() == 1
    assert categories[1].image_set.count() == 1

@pytest.mark.django_db
def test_gallery_view_empty_categories(client):
    """Перевіряє поведінку, коли немає категорій"""
    Category.objects.all().delete()
    response = client.get(reverse('gallery:gallery'))
    assert response.status_code == 200
    assert 'categories' in response.context
    assert len(response.context['categories']) == 0

@pytest.mark.django_db
def test_image_detail_view(client, setup_categories):
    image = Image.objects.get(title="Тестове зображення 1")
    response = client.get(reverse('gallery:image_detail', args=[image.id]))
    assert response.status_code == 200
    assert 'image_detail.html' in [t.name for t in response.templates]
    assert 'image' in response.context
    assert response.context['image'].title == "Тестове зображення 1"
    assert response.context['image'].age_limit == 18

@pytest.mark.django_db
def test_image_detail_view_not_found(client):
    response = client.get(reverse('gallery:image_detail', args=[999]))
    assert response.status_code == 404