from django.conf.urls import url
from django.views.generic import TemplateView

from . import views

urlpatterns = [
    url(r'^$', views.home, name='home'),
    url(r'^_update_lists$', views.update_lists, name='update_lists'),
    url(r'^terms', TemplateView.as_view(template_name='terms.html'), name='terms'),
    url(r'^about', TemplateView.as_view(template_name='about.html'), name='about'),
    url(r'^list/([A-Z]{2}-[A-Z]{3})$', TemplateView.as_view(template_name='list.html'), name='list'),
]
