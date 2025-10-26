# from django.urls import path
# from .views import index, about_us, contact_us,buy

# urlpatterns = [
#     path('', index, name='index'),
#     path('about-us/', about_us, name='about_us'),
#     path('contact-us/', contact_us, name='contact_us'),
#     path('buy/', buy, name='buy' )
# ]


from django.urls import path
from .views import index, about_us, contact_us, buy

urlpatterns = [
    path('', index, name='index'),
    path('about-us/', about_us, name='about_us'),
    path('contact-us/', contact_us, name='contact_us'),
    path('buy/', buy, name='buy'),
]
