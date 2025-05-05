from django.urls import path
from .views import image_list, upload_and_filter_image, predict_image

urlpatterns = [
    path('images/', image_list),
    path('process_image/', upload_and_filter_image),
    path('predict/', predict_image),
]
