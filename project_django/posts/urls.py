
from django.urls import path
from . import views

urlpatterns = [
   path('', views.home, name='home'),
   path('profile/<str:username>/', views.user_profile, name='user_profile'),
   path('profile/<str:username>/edit/', views.edit_user, name='edit_user'),
   path('post/<int:post_id>', views.post , name='post'),


   path('create/', views.new_post , name='new_post'),
   path('<int:post_id>/edit/', views.edit_post, name='edit_post'),
   path('<int:post_id>/delete/', views.delete_post, name='delete_post'),

   path('comment/delete/<int:comment_id>', views.delete_comment, name='delete_comment'),
   path('comment/edit/<int:comment_id>', views.edit_comment, name='edit_comment'),

   path('register/', views.register, name='register'),
   path('login/', views.login_view, name='login'),
   path('logout/', views.logout_view, name='logout'),
   
]
