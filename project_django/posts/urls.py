
from django.urls import path
from . import views

urlpatterns = [
   path('', views.home, name='home'),
   path('post/<int:post_id>', views.post , name='post'),


   path('create/', views.new_post , name='new_post'),
   path('<int:post_id>/edit/', views.edit_post, name='edit_post'),
   path('<int:post_id>/delete/', views.delete_post, name='delete_post'),

   path('comment/delete/<int:comment_id>', views.delete_comment, name='delete_comment'),

   path('register/', views.register, name='register'),
   
]
