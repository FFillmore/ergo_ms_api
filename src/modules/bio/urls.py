from django.urls import path, include
from src.modules.bio.views import (
    ModelCacheView,
)

urlpatterns = [
    path('models/cache/', ModelCacheView.as_view(), name='model-cache'),
    # Submodules
    path('geobotany/', include('src.modules.bio.geobotany.urls')),
    path('zoology/', include('src.modules.bio.zoology.urls')),
    path('ecoprofiles/', include('src.modules.bio.ecoprofiles.urls')),
    path('interactions/', include('src.modules.bio.interactions.urls')),
    path('successions/', include('src.modules.bio.successions.urls')),
    path('paleobotany/', include('src.modules.bio.paleobotany.urls')),
    path('geomorphology/', include('src.modules.bio.geomorphology.urls')),
    path('floristics/', include('src.modules.bio.floristics.urls')),
]