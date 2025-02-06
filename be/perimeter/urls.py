from django.contrib import admin
from django.urls import path, include, re_path
from django.views.generic import TemplateView
from devices.views import DeviceViewSet, GlobalSettingsViewSet
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'devices', DeviceViewSet)
router.register(r'global_settings', GlobalSettingsViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
    re_path(r'^.*$', TemplateView.as_view(template_name='index.html'),
            name="react-frontend"),
]
