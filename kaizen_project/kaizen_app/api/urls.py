# kaizen_app/api/urls.py
from rest_framework.routers import DefaultRouter
from .views import KaizenSheetViewSet

router = DefaultRouter()
router.register('kaizen-sheets', KaizenSheetViewSet)

urlpatterns = router.urls