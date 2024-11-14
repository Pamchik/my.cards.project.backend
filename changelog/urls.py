from rest_framework import routers


from .views import ChangeLogsSet

router = routers.DefaultRouter()

router.register('history', ChangeLogsSet, basename='history')

urlpatterns = []
urlpatterns += router.urls
