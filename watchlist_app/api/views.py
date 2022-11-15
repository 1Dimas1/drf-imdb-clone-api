from django.http import Http404
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.throttling import ScopedRateThrottle
from rest_framework import status
from rest_framework.views import APIView
from rest_framework import generics
from rest_framework import viewsets
from rest_framework import filters
from django_filters.rest_framework import DjangoFilterBackend

from .pagination import WatchListCurPagination
from .permissions import IsReviewAuthorOrReadOnly, IsAdminOrReadOnly
from .throttling import ReviewCreateThrottle
from ..models import WatchList, StreamPlatform, Review
from .serializers import WatchListSerializer, StreamPlatformSerializer, ReviewSerializer


class ReviewDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [IsReviewAuthorOrReadOnly]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = 'review-detail'


class ReviewCreate(generics.CreateAPIView):
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticated]
    throttle_classes = [ReviewCreateThrottle]

    def get_queryset(self):
        return Review.objects.all()

    def perform_create(self, serializer):
        pk = self.kwargs.get('pk')
        movie = WatchList.objects.get(pk=pk)

        author = self.request.user
        review_queryset = Review.objects.filter(watchlist=movie, author=author)

        if review_queryset.exists():
            raise ValidationError('You have already reviewed this movie')

        if movie.rating_number == 0:
            movie.avg_rating = serializer.validated_data['rating']
        else:
            movie.avg_rating = (movie.avg_rating + serializer.validated_data['rating']) / 2
        movie.rating_number += 1
        movie.save()

        serializer.save(watchlist=movie, author=author)


class ReviewList(generics.ListAPIView):
    serializer_class = ReviewSerializer
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['rating']

    def get_queryset(self):
        pk = self.kwargs['pk']
        return Review.objects.filter(watchlist=pk)


class StreamPlatformViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAdminOrReadOnly]
    queryset = StreamPlatform.objects.all()
    serializer_class = StreamPlatformSerializer


class WatchListAV(generics.ListAPIView):
    queryset = WatchList.objects.all()
    serializer_class = WatchListSerializer
    permission_classes = [IsAdminOrReadOnly]
    pagination_class = WatchListCurPagination


class WatchDetailAV(APIView):
    permission_classes = [IsAdminOrReadOnly]

    def get_object(self, pk):
        try:
            return WatchList.objects.get(pk=pk)
        except WatchList.DoesNotExist:
            raise Http404

    def get(self, request, pk):
        movie = self.get_object(pk)
        serializer = WatchListSerializer(movie)
        return Response(serializer.data)

    def put(self, request, pk):
        movie = self.get_object(pk)
        serializer = WatchListSerializer(movie, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        movie = self.get_object(pk)
        movie.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


