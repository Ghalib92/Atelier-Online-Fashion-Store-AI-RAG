from rest_framework import serializers


class ChatRequestSerializer(serializers.Serializer):
    message = serializers.CharField(max_length=1000)


class ChatResponseSerializer(serializers.Serializer):
    answer = serializers.CharField()
