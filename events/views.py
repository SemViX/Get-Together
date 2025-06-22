from rest_framework.generics import ListAPIView, RetrieveUpdateDestroyAPIView, CreateAPIView, ListCreateAPIView
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from rest_framework.response import Response

from .models import Event, Category

from .serializers import EventSerializer, EventCreateSerializer, CategorySerializer

from django_filters.rest_framework import DjangoFilterBackend

from .permissions import IsOwnerOrReadOnly, isAuthor

from drf_spectacular.utils import extend_schema, OpenApiParameter

@extend_schema(
    tags=["Події"],
    description='''
    API для отримання списку подій та фільтарації

    Цей ендопінт дозволяє:

    -Отримувати список всіх подій
    -Фільтрувати події за назвою категорії та іменем автора
'''
)
class EventsApiView(ListAPIView):
    queryset = Event.objects.select_related("category", "creator").prefetch_related("participants").all()
    permission_classes = [IsAuthenticated]
    serializer_class = EventSerializer

    filter_backends = [DjangoFilterBackend]
    filterset_fileds = {
        "category__name": ['exact', 'icontains'],
        "creator__username": ["exact", 'icontains']
    }

    @extend_schema(
        summary="Отримати список подій",
        description="Повертає список всіх подій. Можна застосувати фільтрацію за категорією та автором",
        responses={
            200:EventSerializer(many=True),
            401: {'description': "Токен аутентифікації відсутній або недійсний."},
        },
        parameters=[
            OpenApiParameter(
                name="category__name",
                location=OpenApiParameter.QUERY,
                description="Фільтрування події за точною назвою категорії. (Наприклад, category__name=Спорт)",
                required=False
            ),
            OpenApiParameter(
                name="category__name_icontains",
                location=OpenApiParameter.QUERY,
                description="Фільтрування події за частиною назви категорії. (Наприклад, category__name__icontains=Спорт)",
                required=False
            ),
            OpenApiParameter(
                name="creator__name",
                location=OpenApiParameter.QUERY,
                description="Фільтрування події за точним іменем автора. (Наприклад, creator__username=Admin)",
                required=False
            ),
            OpenApiParameter(
                name="creator__name_icontains",
                location=OpenApiParameter.QUERY,
                description="Фільтрування події за частиною імені автора. (Наприклад, creator__name__icontains=Admin)",
                required=False
            ),
        ]
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

@extend_schema(
    tags=['Події'],
    description='''
    API для створення нових подій

    Цей ендопоінт дозволяє створювати нову подію, тільки авторизованим користувачам, які є авторами (is_creator=True)
'''
)
class CreateEventsApiView(CreateAPIView):
    queryset = Event.objects.select_related("category", "creator").prefetch_related("participants").all()
    permission_classes = [IsAuthenticated, isAuthor]
    serializer_class = EventCreateSerializer
    
    @extend_schema(
        summary="Ствоити подію",
        description="Створення нової події за наданими деталями. Доступ мають тільки авторизовані користувачі-автори",
        request=EventCreateSerializer,
        responses={
            201: EventSerializer,
            400: {"description":"Не правильні дані"},
            401: {'description': "Токен аутентифікації відсутній або недійсний."},
            403: {'description': "Доступ заборонено. У вас немає дозволу для створення подій."},
        }
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


@extend_schema(
    tags=["Події"],
    description='''
    API для отримання, редагування, видалення події за її назвою

    Цей ендопоінт дозволяє:

    -Отримувати дані про подію за її назовю
    -Оновлювати всі дані події
    -Частково оновлювати дані подї
    -Видалення події

    Доступ до цього ендпоінту має тільки автор події
'''
)
class UpdateDeleteEventsView(RetrieveUpdateDestroyAPIView):
    queryset = Event.objects.select_related("category", "creator").prefetch_related("participants").all()
    lookup_field = "title"
    serializer_class = EventCreateSerializer
    permission_classes = [IsOwnerOrReadOnly]

    @extend_schema(
        summary="Отримати подію",
        description="Повертає повну інформацію про подію, отриману за її назвою",
        responses={
            200:EventSerializer,
            403: {'description': "Доступ заборонено."},
            404: {'description': 'Подію з такою назвою не знайдено.'},
        },
        parameters=[
            OpenApiParameter(
                name="title",
                description="Назва події для пошуку (використовується як lookup_field).",
                required=True,
                location=OpenApiParameter.PATH
            )
        ]
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @extend_schema(
        summary="Повністю оновити подію",
        description="Оновляє повну інформацію про подію, отриману за її назвою",
        responses={
            200:EventSerializer,
            403: {'description': "Доступ заборонено."},
            404: {'description': 'Подію з такою назвою не знайдено.'},
        },
        parameters=[
            OpenApiParameter(
                name="title",
                description="Назва події для оновлення.",
                required=True,
                location=OpenApiParameter.PATH
            )
        ]
    )
    def put(self, request, *args, **kwargs):
        return super().put(request, *args, **kwargs)

    @extend_schema(
        summary="Частково оновити подію",
        description="Частково оновляє інформацію про подію, отриману за її назвою",
        responses={
            200:EventSerializer,
            403: {'description': "Доступ заборонено."},
            404: {'description': 'Подію з такою назвою не знайдено.'},
        },
        parameters=[
            OpenApiParameter(
                name="title",
                description="Назва події для оновлення.",
                required=True,
                location=OpenApiParameter.PATH
            )
        ]
    )
    def patch(self, request, *args, **kwargs):
        return super().patch(request, *args, **kwargs)
    
    @extend_schema(
        summary="Видалити подію",
        description="Видаляє подію, отриману за її назвою",
        responses={
            200:EventSerializer,
            403: {'description': "Доступ заборонено."},
            404: {'description': 'Подію з такою назвою не знайдено.'},
        },
        parameters=[
            OpenApiParameter(
                name="title",
                description="Назва події для видалення  .",
                required=True,
                location=OpenApiParameter.PATH
            )
        ]
    )
    def delete(self, request, *args, **kwargs):
        return super().delete(request, *args, **kwargs)

@extend_schema(
    tags=["Події"],
    description='''
    API для участі в події

    Цей ендопоінт дозволяє авторизованим користувачам взяти участь в події, за назвою цієї події
    
'''
)
class TakePartView(APIView):
    permission_classes = [IsAuthenticated]


    @extend_schema(
        summary="Взяти участь в події",
        description="Дозволяє авторизованим користувачам приєднатися до події",
        request=None,
        responses={
            200:{'description': "Ви успішно приєдналися до події"},
            400:{'description': "Ви вже є учасником події"},
            401:{'description': "Токен аутентифікації відсутній або недійсний."},
            404:{'description': "Події з такою назваою не існує"},
        },
        parameters=[
            OpenApiParameter(
                name='title',
                location=OpenApiParameter.PATH,
                description='Назва події, до якої потрібно приєднатися.',
                required=True
            )
        ]
    )
    def post(self, request, title):
        try:
            event = Event.objects.get(title=title)
        except Event.DoesNotExist:
            return Response({"detail":"Event not found"}, status=status.HTTP_404_NOT_FOUND)
        
        if request.user in event.participants.all():
            return Response({'detail':"You are already participated"}, status=status.HTTP_400_BAD_REQUEST)
        
        event.participants.add(request.user)
        return Response({"detail":"You have joined the event"}, status=status.HTTP_200_OK)

@extend_schema(
    tags=["Категорії"],
    description='''
    API для керування категоріями
    
    Цей ендопоінт довзволяє:

    -Отримати список всіх категорій
    -Створити нову категорію

    Доступ до ендопоінту мають тільки авторизовані користувачі
'''    
)
class CategoriesApiView(ListCreateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Отримати список категорій",
        description="Дозволяє отримати список всіх категорій",
        responses={
            201:CategorySerializer,
            401: {'description': "У користувача нема прав доступу"},
        }
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @extend_schema(
        summary="Створити нову категорію",
        description="Дозволяє створити нову категорію. Потрібно вказати лише назву категорії (name) ",
        request=CategorySerializer,
        responses={
            201:CategorySerializer,
            401: {'description': "У користувача нема прав доступу"},
        }
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)
