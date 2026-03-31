from rest_framework.decorators import api_view, APIView
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet,ReadOnlyModelViewSet
from rest_framework import status ,permissions

from .serializers import PostSerializer,commentSerializer,profileSerializer,SignupSerializer
from posts.models import Post,Comment,CustomUser

from django.shortcuts import get_object_or_404
from django.http import Http404, JsonResponse


# ##VIEWSETS
class postViewSet(ModelViewSet):
  queryset=Post.objects.all()
  permission_classes = [permissions.IsAuthenticatedOrReadOnly]
  serializer_class=PostSerializer

  def perform_create(self, serializer):
      serializer.save(author=self.request.user)

class CommentViewSet(ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = commentSerializer

    def get_queryset(self):
      post_id = self.request.query_params.get('post')
      if post_id:
          return Comment.objects.filter(post_id=post_id)
      return Comment.objects.all()

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class UserViewSet(ReadOnlyModelViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = profileSerializer

class SignupView(APIView):
    def post(self, request):
        serializer = SignupSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "User created"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors)
    

##CLASS BASED VIEWS
# class getCreatePost(APIView):
#   permission_classes = [permissions.IsAuthenticatedOrReadOnly]
#   def get(self,request):
#     posts=Post.objects.all()
#     serializer=PostSerializer(posts, many=True)
#     return Response(serializer.data)
  
#   def post(self, request):
#     serializer=PostSerializer(data=request.data)
  
#     if serializer.is_valid():
#       serializer.save( author=requet.user)
#       return Response(serializer.data)
#     return Response(serializer.errors)
  
# class getPostDetail(APIView):

#   def getPost(self,pk):
#     try:
#       return Post.objects.get(id=pk)
#     except Post.DoesNotExist:
#       raise Http404
    
#   def get(self,request,pk):
#     post=self.getPost(pk)
#     serializer=PostSerializer(post, many=False)
#     return Response(serializer.data)

#   def put(self, request, pk, format=None):
#         post = self.getPost(pk)
#         serializer = PostSerializer(post, data=request.data)
#         if serializer.is_valid():
#             serializer.save(author=requet.user)
#             return Response(serializer.data)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#   def delete(self, request, pk, format=None):
#         post = self.getPost(pk)
#         post.delete()
#         return Response(status=status.HTTP_204_NO_CONTENT)
    


##FUNCTION BASED VIEWS

# @api_view(['GET'])
# def getRoutes(request):
#   routes=[
#     'GET/api',
#     'GET/api/id:'
#   ]
#   return Response(routes)

# @api_view(['GET','POST'])
# def PostsList(request):
#   if request.method=='GET':
#     posts=Post.objects.all()
#     serializer=PostSerializer(posts, many=True)
#     return Response(serializer.data)
  
#   elif request.method=='POST':
#     serializer=PostSerializer(data=request.data)
#     if serializer.is_valid():
#       serializer.save()
#       return Response(serializer.data)
#     return Response(serializer.errors)

# @api_view(['GET'])
# def getPost(request,pk):
#   post=Post.objects.get(id=pk)
#   serializer=PostSerializer(post, many=False)
#   return Response(serializer.data)

# @api_view(['PUT'])
# def updatePost(request,pk):
#    post=Post.objects.get(id=pk)
#    serializer=PostSerializer(post, data=request.data)
#    if serializer.is_valid():
#       serializer.save()
#       return Response(serializer.data)
#    return Response(serializer.data)
   
# @api_view(['DELETE'])
# def deletePost(request, id):
#     post = Post.objects.get(id=id)
#     post.delete()
#     return Response("Deleted")

# @api_view(['GET','POST'])
# def getcomments(request):
#  if request.method=='GET':
#     comments=Comments.objects.all()
#     serializer=commentSerializer(comments, many=True)   
#     return Response(serializer.data)
 
#  elif request.method=='POST':
#     serializer=commentSerializer(data=request.data)
#     if serializer.is_valid():
#       serializer.save()
#       return Response(serializer.data)
#     return Response(serializer.errors)
 
# @api_view(['GET'])
# def getPostcomments(request,post_id):
#   comments=Comments.objects.filter(post_id=post_id)
#   serializer=commentSerializer(comments, many=True)
#   return Response(serializer.data)


# @api_view(['GET'])
# def getuser(request):
#   user=CustomUser.objects.all()
#   serializer=profileSerializer(user,many=True)
#   return Response(serializer.data)