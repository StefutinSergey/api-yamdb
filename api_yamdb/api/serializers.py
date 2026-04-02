from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator 

from reviews.models import Comment, Review


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        read_only=True, slug_field='username'
    )

    class Meta:
        fields = '__all__'
        read_only_fields = ['review']
        model = Comment
        validators = ( 
            UniqueTogetherValidator( 
                queryset=Review.objects.all()
                fields=('author', 'title_id'),
                message='You already reviewed this title.',
            ),
        )
