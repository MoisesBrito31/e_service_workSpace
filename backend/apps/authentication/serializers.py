from rest_framework import serializers
from .models import User

class UserSerializer(serializers.ModelSerializer):
    """
    Serializer padrão para exibição e menções de usuários (@usuario).
    """
    cargo_display = serializers.CharField(source='get_cargo_display', read_only=True)
    nome_completo = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            'id',
            'username',
            'email',
            'first_name',
            'last_name',
            'nome_completo',
            'cargo',
            'cargo_display',
            'telefone',
            'avatar',
            'is_active',
        ]
        read_only_fields = ['id', 'cargo_display', 'nome_completo']

    def get_nome_completo(self, obj) -> str:
        return obj.get_full_name() or obj.username


class UserCreateUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer para criação e edição administrativa de usuários.
    """
    password = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = User
        fields = [
            'id',
            'username',
            'email',
            'password',
            'first_name',
            'last_name',
            'cargo',
            'telefone',
            'is_active',
        ]

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        user = super().create(validated_data)
        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()
        user.save()
        return user

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        user = super().update(instance, validated_data)
        if password:
            user.set_password(password)
            user.save()
        return user
