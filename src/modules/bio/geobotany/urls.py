from django.urls import path, include
from rest_framework.routers import DefaultRouter

from src.modules.bio.geobotany.views.species import SpeciesViewSet
from src.modules.bio.geobotany.views.sites import SiteViewSet, SiteBulkDeleteView
from src.modules.bio.geobotany.views.descriptions import (
    DescriptionView,
    DescriptionDetailView,
    DescriptionBulkDeleteView,
)
from src.modules.bio.geobotany.views.analytics import (
    SiteMeansView,
    CustomSiteMeansView,
    SiteDistributionView,
    CustomSiteDistributionView,
    SiteClassificationView,
    CustomSiteClassificationView,
    SiteComparisonView,
    SiteCustomAnalysisView,
)


router = DefaultRouter()
router.register(r'species', SpeciesViewSet, basename='species')
router.register(r'sites', SiteViewSet, basename='sites')


urlpatterns = [
    path('sites/<int:site_number>/<str:zone_type>/', SiteViewSet.as_view({'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'}), name='site-detail'),
    path('sites/<int:site_number>/<str:zone_type>/descriptions/', DescriptionView.as_view(), name='description-list'),
    path('descriptions/<int:description_id>/', DescriptionDetailView.as_view(), name='description-detail'),
    path('descriptions/bulk-delete/', DescriptionBulkDeleteView.as_view(), name='description-bulk-delete'),
    path('sites/<int:site_number>/<str:zone_type>/means/', SiteMeansView.as_view(), name='site-means'),
    path('sites/custom-means/', CustomSiteMeansView.as_view(), name='site-custom-means'),
    path('sites/<int:site_number>/<str:zone_type>/distribution/', SiteDistributionView.as_view(), name='site-distribution'),
    path('sites/custom-distribution/', CustomSiteDistributionView.as_view(), name='site-custom-distribution'),
    path('sites/<int:site_number>/<str:zone_type>/classification/', SiteClassificationView.as_view(), name='site-classification'),
    path('sites/custom-classification/', CustomSiteClassificationView.as_view(), name='site-custom-classification'),
    path('sites/bulk-delete/', SiteBulkDeleteView.as_view(), name='site-bulk-delete'),
    path('sites/comparison/', SiteComparisonView.as_view(), name='site-comparison'),
    path('sites/custom-analysis/', SiteCustomAnalysisView.as_view(), name='custom-analysis'),
    path('', include(router.urls)),
]


