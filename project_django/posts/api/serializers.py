from rest_framework.serializers import ModelSerializer,ReadOnlyField
from posts.models import Post,Comments,CustomUser

class SignupSerializer(ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'password']
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def create(self, validated_data):
        user = CustomUser.objects.create_user(**validated_data)
        return user
    
class PostSerializer(ModelSerializer):
  author = ReadOnlyField(source='author.username')
  class Meta:
    model= Post
    fields='__all__'

class commentSerializer(ModelSerializer):
  author = ReadOnlyField(source='user.username')
  class Meta:
    model=Comments
    fields='__all__'

class profileSerializer(ModelSerializer):
  class Meta:
    model=CustomUser
    fields=["id",
        "first_name", "last_name","date_joined","username","email","bio","profile_picture" ]
