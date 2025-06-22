from .models import User
from .serializers import UserSerializer, RegisterUserSerializer
from rest_framework import permissions
from rest_framework.generics import CreateAPIView, RetrieveUpdateDestroyAPIView
from drf_spectacular.utils import extend_schema

@extend_schema(
    tags=["Користувачі"], 
    description='''
    Це API для керування окремими користувачами
    
    Цей ендопоінт дозволяє:

    -Отримувати дані користувача за іменем
    -Оновлюти дані існуючого користувача
    -Видаляти користувача

    Доступ до ендопоінту мають лише авторизовані користувачі

    '''
)
class UserApiView(RetrieveUpdateDestroyAPIView):
    queryset = User.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = UserSerializer
    lookup_field="username"

    @extend_schema(
        summary="Отримати дані користувача",
        description="Дозволяє отримати всі дані про користувача за його іменем",
        responses={
            201:UserSerializer,
            401: {'description': "У користувача нема прав доступу"},
            404: {'description': "Користувача з таким іменем не знайдено"}
        },
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @extend_schema(
        summary="Оновити дані користувача",
        description="Дозволяє оновити всі дані про користувача за його іменем",
        responses={
            200:UserSerializer,
            401: {'description': "У користувача нема прав доступу"},
            404: {'description': "Користувача з таким іменем не знайдено"}
        },
    )
    def put(self, request, *args, **kwargs):
        return super().patch(request, *args, **kwargs)
    
    @extend_schema(
        summary="Частково оновити дані користувача",
        description="Дозволяє частково оновити дані про користувача за його іменем",
        responses={
            200:UserSerializer,
            401: {'description': "У користувача нема прав доступу"},
            404: {'description': "Користувача з таким іменем не знайдено"}
        },
    )
    def patch(self, request, *args, **kwargs):
        return super().patch(request, *args, **kwargs)
    
    @extend_schema(
        summary="Видалення користувавча",
        description="Дозволяє видалити користувача за його іменем",
        responses={
            200:UserSerializer,
            401: {'description': "У користувача нема прав доступу"},
            404: {'description': "Користувача з таким іменем не знайдено"}
        },
    )
    def delete(self, request, *args, **kwargs):
        return super().delete(request, *args, **kwargs)


@extend_schema(
    tags=["Авторизація"],
    description='''
    API для авторизації та реєстарації користувачів
    
    Цей ендопоінт дозволяє реєструвати користувачів
    '''
)
class CreateUserView(CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterUserSerializer
    permission_classes = [permissions.AllowAny]


    @extend_schema(
        summary="Створення користувачів",
        description="Створює новий обліковий запис користувача з наданими даними (username, email, password, etc.)",
        request=RegisterUserSerializer,
        responses={
            201: UserSerializer,
            400: {'description': "Неправильний запит. Наприклад, ім\'я користувача або email вже використовуються, або паролі не співпадають."}
        }
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)
    

