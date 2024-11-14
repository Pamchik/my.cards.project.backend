from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings
from backend_api.views import index

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', index),
    path('api/', include('backend_api.api.urls')),
    path('api/changelog/', include('changelog.urls')),
    path('api/auth/', include('user_api.urls')),
    # path('orders/', index),
    # path('projects/', index),
    # path('offers', index),
    # path('contract-annexes/', index),
    # path('purchase-orders/', index),
    # path('key-exchange/', index),
    # path('testing-cards/', index),
    # path('dictionary/', index),                            
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)