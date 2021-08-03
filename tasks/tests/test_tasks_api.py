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


def detail_url(task_id):
    """Return task detail URL"""
    return reverse('task:task-detail', args=[task_id])


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

    def test_retrieve_all_task_to_superuser(self):
        "Test checking all tasks are retrieved to super user"
        self.client = APIClient()
        self.admin_user = get_user_model().objects.create_superuser(
            'admin@testing.com',
            'password123',
            'admin',
            'user'
        )
        self.client.force_authenticate(self.admin_user)

        # creating a task by sample user 
        sample_task(user=self.user)
        
        res = self.client.get(TASK_URL)
        admin_id = self.admin_user.id
        self.assertNotIn(admin_id, res.data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)

    def test_create_task(self):
        """Test creating task"""
        payload = {
            'task_id': 2,
            'title':'Create another Django Rest API',
            'description':'Django API for the server',
            'task_status':'A'
        }
        res = self.client.post(TASK_URL, payload)
        
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        task = Task.objects.get(task_id=res.data['task_id'])
        for key in payload.keys():
            self.assertEqual(payload[key], getattr(task, key))

    def test_partial_update_tasks(self):
        """Test updating a task with patch"""
        task = sample_task(user=self.user)
        payload = {
            'task_id':'1',
            'title':'Updating Sample task',
            'description':'Django API for the user',
            'task_status':'A',
        }

        url = detail_url(task.task_id)
        self.client.patch(url, payload)

        task.refresh_from_db()
        self.assertEqual(task.title, payload['title'])

    def test_full_update_task(self):
        """Test updating a task with put"""
        task = sample_task(user=self.user)
        payload = {
            'task_id':'1',
            'title':'Updating Sample task',
            'description':'Hello World',
            'task_status':'C',
        }

        url = detail_url(task.task_id)
        self.client.put(url, payload)

        task.refresh_from_db()
        self.assertEqual(task.title, payload['title'])
        self.assertEqual(task.description, payload['description'])
        self.assertEqual(task.task_status, payload['task_status'])
