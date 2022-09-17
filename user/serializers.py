from .models import User
from rest_framework import serializers


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'first_name', 'last_name', 'email', 'role')


class UserCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'first_name', 'last_name', 'email', 'role', 'password')
        read_only_fields = ('id', 'role')
        extra_kwargs = { 'password': { 'write_only': True } }

    def create(self, validated_data):
        user = super(UserCreateSerializer, self).create(validated_data)
        user.set_password(validated_data['password'])
        user.save()
        return user


class UserUpdateSerializer(serializers.ModelSerializer):
    role = serializers.CharField() 

    class Meta:
        model = User
        fields = ('id', 'username', 'first_name', 'last_name', 'email', 'role', 'password')
        read_only_fields = ('id',)
        extra_kwargs = { 'password': { 'write_only': True, 'required': False } }

    def validate_role(self, value):
        user = User.objects.get(pk=self.context['request'].user.pk)
        if user.is_manager and value in ['admin',]:
             raise serializers.ValidationError('User manager is not allowed to set admin role.')
        if user.is_user and value in ['admin', 'manager']:
             raise serializers.ValidationError('Regular user is allowed to change the role.')
        return value

    def validate(self, data):
        if 'role' in data:
            if data['role'] == 'admin':
                data['is_staff'] = True
                data['is_admin'] = True
            elif data['role'] == 'manager':
                data['is_staff'] = True
        return super(UserUpdateSerializer, self).validate(data)

    def update(self, instance, validated_data):
        user = super(UserUpdateSerializer, self).update(self.instance, validated_data)
        if 'password' in validated_data:
            user.set_password(validated_data['password'])
        user.save()
        return user
