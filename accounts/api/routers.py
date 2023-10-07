from rest_framework.routers import DefaultRouter
from accounts.api.viewsets import AccountViewSet, AdvisorViewSet


router = DefaultRouter()

router.register(r'accounts', AccountViewSet, basename='accounts')
router.register(r'advisors', AdvisorViewSet, basename='advisors')