from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Task

from tasks.serializers import TaskSerializer


TASK_URL = reverse('task:task-list')


def register_user(**params):
    return get_user_model().objects.create_user(**params)


def sample_task(user, **params):
    """Create and return a sample task"""
    defaults = {
        'task_id':'1',
        'title':'Create a Django Rest API',
        'description':'Django API for the user',
        'task_status':'A',
    }
    defaults.update(params)

    return Task.objects.create(user=user, **defaults)


class PublicTaskApiTests(TestCase):
    """Test unauthenticated task API access"""

    def setUp(self):
        self.client = APIClient()

    def test_required_auth(self):
        """Test the authenticaiton is required"""
        res = self.client.get(TASK_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateRecipeApiTests(TestCase):
    """Test authenticated task API access"""

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            'test@testing.com',
            'testpass',
            'Test',
            'User'
        )
        self.client.force_authenticate(self.user)

    def test_retrieve_tasks(self):
        """Test retrieving list of tasks"""
        payload = {
            'task_id':'2',
            'title':'Create another Django Rest API',
            'description':'Django API for the server',
            'task_status':'A'
        }
        sample_task(user=self.user, **payload)
        sample_task(user=self.user)

        res = self.client.get(TASK_URL)

        tasks = Task.objects.all().order_by('-task_id')
        serializer = TaskSerializer(tasks, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_tasks_limited_to_user(self):
        """Test retrieving tasks for user"""
        user2 = get_user_model().objects.create_user(
            'other@testing.com',
            'password123',
            'other',
            'user'
        )
        payload = {
            'task_id':'2',
            'title':'Create another Django Rest API',
            'description':'Django API for the server',
            'task_status':'A'
        }
        sample_task(user=user2, **payload)
        sample_task(user=self.user)

        res = self.client.get(TASK_URL)

        tasks = Task.objects.filter(user=self.user)
        serializer = TaskSerializer(tasks, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data, serializer.data)

    def test_create_task(self):
        """Test creating task"""
        payload = {
            'task_id':'2',
            'title':'Create another Django Rest API',
            'description':'Django API for the server',
            'task_status':'A'
        }
        res = self.client.post(TASK_URL, payload)
        
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        task = Task.objects.get(id=res.data['task_id'])
        for key in payload.keys():
            self.assertEqual(payload[key], getattr(task, key))


    # def test_partial_update_recipe(self):
    #     """Test updating a recipe with patch"""
    #     recipe = sample_recipe(user=self.user)
    #     recipe.tags.add(sample_tag(user=self.user))
    #     new_tag = sample_tag(user=self.user, name='Curry')

    #     payload = {'title': 'Chicken tikka', 'tags': [new_tag.id]}
    #     url = detail_url(recipe.id)
    #     self.client.patch(url, payload)

    #     recipe.refresh_from_db()
    #     self.assertEqual(recipe.title, payload['title'])
    #     tags = recipe.tags.all()
    #     self.assertEqual(len(tags), 1)
    #     self.assertIn(new_tag, tags)

    # def test_full_update_recipe(self):
    #     """Test updating a recipe with put"""
    #     recipe = sample_recipe(user=self.user)
    #     recipe.tags.add(sample_tag(user=self.user))

    #     payload = {
    #             'title': 'Spaghetti carbonara',
    #             'time_minutes': 25,
    #             'price': 5.00
    #         }
    #     url = detail_url(recipe.id)
    #     self.client.put(url, payload)

    #     recipe.refresh_from_db()
    #     self.assertEqual(recipe.title, payload['title'])
    #     self.assertEqual(recipe.time_minutes, payload['time_minutes'])
    #     self.assertEqual(recipe.price, payload['price'])
    #     tags = recipe.tags.all()
    #     self.assertEqual(len(tags), 0)
