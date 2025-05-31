from django.urls import path
from django.contrib.auth.views import LoginView, LogoutView
from .views import custom_login, register, home, public_voting, anonymous_suggestion, anonymous_entry, raise_issue
from . import views

urlpatterns = [
    path('register/', register, name='register'),
    # path('login/', LoginView.as_view(template_name='core/login.html'), name='login'),
    path('login/', custom_login, name='login'),
    path('register/', views.register, name='register'),
    path('logout/', LogoutView.as_view(next_page='login'), name='logout'),
    path('user/home/', views.user_home, name='user_home'),
    path('user/raise-issue/', raise_issue, name='raise_issue'),
    path('supervisor/home/', views.supervisor_home, name='supervisor_home'),
    path('', home, name='home'),
    path('public/', public_voting, name='public_voting'),
    path('anonymous-suggestion/', anonymous_suggestion, name='anonymous_suggestion'),
    path('anonymous-entry/', anonymous_entry, name='anonymous_entry'),
    path('supervisor/vote-topics/', views.manage_vote_topics, name='manage_vote_topics'),

]
