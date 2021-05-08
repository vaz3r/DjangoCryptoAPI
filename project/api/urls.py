from django.conf.urls import url 
from api import views 
 
urlpatterns = [ 
    url(r'^api/v1/quotes$', views.coin_info)
]