from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (WatchListAV, WatchDetailAV, ReviewList, ReviewDetail,
                    ReviewCreate, StreamPlatformViewSet)

router = DefaultRouter()
router.register('stream', StreamPlatformViewSet, basename='stream_platform')

urlpatterns = [
    path('list/', WatchListAV.as_view(), name='movie_list'),
    path('<int:pk>/', WatchDetailAV.as_view(), name='movie_detail'),
    path('', include(router.urls)),
    path('<int:pk>/reviews/', ReviewList.as_view(), name='review_list'),
    path('<int:pk>/review-create/', ReviewCreate.as_view(), name='review_create'),
    path('reviews/<int:pk>/', ReviewDetail.as_view(), name='review_detail'),
]
