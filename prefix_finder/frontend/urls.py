from django.urls import include, path
from django.views.generic import TemplateView
from django.views.generic.base import RedirectView

from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('results', views.results, name='results'),
    path('_update_lists', views.update_lists, name='update_lists'),
    path('_preview_branch/([A-Za-z0-9-]+)', views.preview_branch, name='preview_branch'),
    path('terms', TemplateView.as_view(template_name='terms.html'), name='terms'),
    path('about', TemplateView.as_view(template_name='about.html'), name='about'),
    path('list/<prefix>', views.list_details, name='list'),
    path('download', RedirectView.as_view(url='/results', permanent=False), name='download'),
    path('download.json', views.json_download, name='json_download'),
    path('download.csv', views.csv_download, name='csv_download'),
    path('download.xml', views.xml_download, name='xml_download'),
]
