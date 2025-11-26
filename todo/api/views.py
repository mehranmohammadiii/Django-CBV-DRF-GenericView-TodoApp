import requests
from todo.models import Task
from .serializers import TaskSerializer
from rest_framework import permissions
from rest_framework import generics
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.http import JsonResponse
from django.core.cache import cache
from django.views.decorators.cache import cache_page
from rest_framework.response import Response
from django.conf import settings
class TodoListView(generics.ListCreateAPIView):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="لیست تمام کارها برای کاربر فعلی",
        responses={200: TaskSerializer(many=True)},
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    # -----------------------------------
    @swagger_auto_schema(
        operation_summary="ایجاد یک کار جدید",
        request_body=TaskSerializer,
        responses={
            201: openapi.Response("مورد با موفقیت ایجاد شد", TaskSerializer),
            400: "اطلاعات ارسالی نامعتبر است",
        },
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)

    # -----------------------------------
    def get_queryset(self, *args, **kwargs):
        return super().get_queryset(*args, **kwargs).filter(user=self.request.user)

    # -----------------------------------
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


# -------------------------------------------------------------------------------------------------------------------------------------
class TodoDetailApiView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = [permissions.IsAuthenticated]

    # lookup_field = "todo_id"
    # -----------------------------------
    @swagger_auto_schema(
        operation_summary="دریافت جزئیات یک کار خاص",
        responses={200: TaskSerializer, 404: "موردی با این شناسه یافت نشد"},
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    # -----------------------------------
    @swagger_auto_schema(
        operation_summary="بروزرسانی کامل یک کار",
        request_body=TaskSerializer,
        responses={
            200: TaskSerializer,
            400: "اطلاعات ارسالی نامعتبر است",
            404: "موردی با این شناسه یافت نشد",
        },
    )
    def put(self, request, *args, **kwargs):
        return super().put(request, *args, **kwargs)

    # -----------------------------------
    @swagger_auto_schema(
        operation_summary="بروزرسانی بخشی از یک کار",
        request_body=TaskSerializer,
        responses={
            200: TaskSerializer,
            400: "اطلاعات ارسالی نامعتبر است",
            404: "موردی با این شناسه یافت نشد",
        },
    )
    def patch(self, request, *args, **kwargs):
        return super().patch(request, *args, **kwargs)

    # -----------------------------------
    @swagger_auto_schema(
        operation_summary="حذف یک کار",
        responses={
            204: "مورد با موفقیت حذف شد (No Content)",
            404: "موردی با این شناسه یافت نشد",
        },
    )
    def delete(self, request, *args, **kwargs):
        return super().delete(request, *args, **kwargs)

    # -----------------------------------
    def get_queryset(self):
        """
        This view should return a list of all the tasks
        for the currently authenticated user.
        """
        return Task.objects.filter(user=self.request.user)

    # -----------------------------------
    def perform_update(self, serializer):
        """Ensure the user of the task remains the same on update."""
        serializer.save(user=self.request.user)


# -----------------------------------
# def delete(self, request, *args, **kwargs):
#     object = self.get_object()
#     object.delete()
#     return Response({"detail": "successfully removed"})
# -----------------------------------
# def post(self, request, *args, **kwargs):
#     object = self.get_object()
#     serializer = TaskSerializer(
#         data=request.data, instance=object, many=False
#     )
#     if serializer.is_valid():
#         serializer.save()
#     return Response(serializer.data)
# -------------------------------------------------------------------------------------------------------------------------------------------

# redis caching example

# def redis_cashe(request):
#     if cache.get('api_delay') is None :
#         response = requests.get('https://postman-echo.com/delay/10')
#         cache.set('api_delay', response.json(), timeout=120)  # Cache for 120 seconds
#     return JsonResponse({'status': 'success', 'data': cache.get('api_delay')})


@cache_page(60 * 1)
def redis_cashe(request):

    response = requests.get("https://postman-echo.com/delay/10")
    return JsonResponse({"status": "success", "data": response.json()})
# ---------------------------------------------------------------------------------------------------------------
class WeatherApi(generics.GenericAPIView):

    """
    Get weather information for a city with Redis caching
    Usage: GET /api/weather/?city=Tehran
    """
    
    def get(self, request, *args, **kwargs):
        city = request.GET.get('city', 'Tehran')
        
        cache_key = f'weather_{city}'
        weather_data = cache.get(cache_key)

        if weather_data:
            return Response({
                "source": "Redis Cache ⚡", 
                "city": city,
                "data": weather_data,
                "cached": True
            })
        
        api_key = getattr(settings, 'OPENWEATHER_API_KEY', None)
        if not api_key:
            return Response(
                {"error": "API Key not configured"}, 
                status=500
            )
        
        url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"

        try:
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()

                clean_data = {
                    "city": data.get("name", "Unknown"),
                    "temp": data.get("main", {}).get("temp", 0),
                    "feels_like": data.get("main", {}).get("feels_like", 0),
                    "description": data.get("weather", [{}])[0].get("description", "Unknown"),
                    "humidity": data.get("main", {}).get("humidity", 0),
                    "wind_speed": data.get("wind", {}).get("speed", 0)
                }
                
                cache.set(cache_key, clean_data, timeout=1200)

                return Response({
                    "source": "OpenWeatherMap API 🌍",
                    "data": clean_data,
                    "cached": False
                })
            
            elif response.status_code == 404:
                return Response(
                    {"error": f"City '{city}' not found"}, 
                    status=404
                )
            else:
                return Response(
                    {"error": "Weather API error"}, 
                    status=response.status_code
                )

        except requests.Timeout:
            return Response(
                {"error": "API request timeout"}, 
                status=504
            )
        except requests.RequestException as e:
            return Response(
                {"error": f"Service unavailable: {str(e)}"}, 
                status=503
            )
# ---------------------------------------------------------------------------------------------------------------
