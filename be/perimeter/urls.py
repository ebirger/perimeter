from django.contrib import admin
from django.urls import path, include, re_path
from rest_framework.routers import DefaultRouter
from devices.views import DeviceViewSet, GlobalSettingsViewSet
from django.views.generic import TemplateView
from django.views.decorators.csrf import csrf_exempt

router = DefaultRouter()
router.register(r'devices', DeviceViewSet)
router.register(r'global_settings', GlobalSettingsViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
    re_path(r'^.*$', TemplateView.as_view(template_name='index.html'),
            name="react-frontend"),
]
