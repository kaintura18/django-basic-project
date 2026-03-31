from . import views
from django.urls import path,include
from rest_framework.routers import DefaultRouter


router=DefaultRouter()
router.register('post',views.postViewSet)
router.register('comments', views.CommentViewSet)
router.register('users', views.UserViewSet)

urlpatterns = [
#   # path( '', views.PostsList, name='postslist'),
#   # path( '<str:pk>/', views.getPost, name='getpost'),
#   # path( 'update/<str:pk>/', views.updatePost, name='updatepost'),
#   # path( 'delete/<int:id>/', views.deletePost,name='deletepost'),
#   path( '<int:post_id>/comments', views.getPostcomments, name='post-comments'),
#   path( 'comments', views.getcomments, name='getcomments'),
#   path( 'user', views.getuser, name='userposts'),

# #   path('post/', views.getCreatePost.as_view(), name='post-detail'), #class basedv iews
# #   path('post/<int:pk>/', views.getPostDetail.as_view(), name='post-detail'),

path('signup/', views.SignupView.as_view()),
path('',include(router.urls))


]