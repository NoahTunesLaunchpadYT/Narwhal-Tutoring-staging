from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("tutor_register", views.tutor_register, name="tutor_register"),
    path("about", views.about, name="about"),
    path("contact", views.contact, name="contact"),
    path("tutors", views.tutors, name='tutors'),
    path("tos", views.tos, name="tos"),
    path("dashboard", views.dashboard, name="dashboard"),
    path("tutor/<int:tutor_id>", views.tutor, name='tutor'),
    path("select_lesson_times/<int:tutor_id>", views.select_lesson_times, name='select_lesson_times'),
    path('update_availability/', views.update_availability, name='update_availability'),
    path('save_availability/', views.save_availability, name='save_availability'),
    path('delete_availability/<int:event_id>/', views.delete_availability, name='delete_availability'),
    path('get_client_calendar', views.get_client_calendar, name='get_client_calendar'),
    path('get_calendar/<int:tutor_id>', views.get_calendar, name='get_calendar'),
    path('get_availability/<int:tutor_id>', views.get_availability, name='get_availability'),
    path('get_availability_and_lessons/<int:tutor_id>', views.get_availability_and_lessons, name='get_availability_and_lessons'),
    path('create-checkout-session/', views.create_checkout_session, name='create-checkout-session'),
    path('cancel/', views.cancel, name='cancel'),
    path('success/<int:cart_id>', views.success, name='success'),
    path('save-lessons-to-cart/', views.save_lessons_to_cart, name='save-lessons-to-cart'),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)