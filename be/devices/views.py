from rest_framework import viewsets, status, filters
from rest_framework.response import Response
from filters.mixins import FiltersMixin
from .models import Device, GlobalSettings
from .serializers import DeviceSerializer, GlobalSettingsSerializer


class DeviceViewSet(FiltersMixin, viewsets.ModelViewSet):
    queryset = Device.objects.all()  # pylint: disable=no-member
    serializer_class = DeviceSerializer
    filter_backends = (filters.OrderingFilter,)

    filter_mappings = {
        'mac_address': 'mac_address',
    }

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data,
                                         partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)


class GlobalSettingsViewSet(viewsets.ModelViewSet):
    queryset = GlobalSettings.objects.all()  # pylint: disable=no-member
    serializer_class = GlobalSettingsSerializer

    def update(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance, data=request.data)
        except BaseException:  # pylint: disable=broad-exception-caught
            serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)
