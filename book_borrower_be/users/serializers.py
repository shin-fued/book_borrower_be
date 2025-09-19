from rest_framework import serializers
from .models import Roles, UserRole, Users


class UserSerializer(serializers.ModelSerializer):
    roles = serializers.ListField(
        child=serializers.CharField(),
        required=True,
    )

    class Meta:
        model = Users
        fields = ["id", "username", "phone_number", "roles", "created_at"]

    lookup_field = "username"

    def create(self: "UserSerializer", validated_data: dict[str, any]) -> Users:
        roles_data = validated_data.pop("roles", [])
        user = Users.objects.create(**validated_data)

        # handle roles
        for role_name in roles_data:
            role_obj = Roles.objects.get(name=role_name)
            UserRole.objects.create(user=user, role=role_obj)

        return user

    def get_roles(self: "UserSerializer", obj: object) -> list[dict[str, any]]:
        # get all roles for this user via the join table
        user_roles = UserRole.objects.filter(user=obj)
        roles = [ur.role for ur in user_roles]
        return RoleSerializer(roles, many=True).data

    def update(
        self: "UserSerializer", instance: object, validated_data: dict[str, any]
    ) -> Users:
        roles_data = validated_data.pop("roles", None)
        instance.username = validated_data.get("username", instance.username)
        instance.phone_number = validated_data.get(
            "phone_number", instance.phone_number
        )
        instance.save()

        if roles_data is not None:
            # replace old roles with new
            UserRole.objects.filter(user=instance).delete()
            for role_name in roles_data:
                role_obj = Roles.objects.get(name=role_name)
                UserRole.objects.create(user=instance, role=role_obj)

        return instance


class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Roles
        fields = ["id", "name"]


class UserRoleSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=Users.objects.all())
    role = RoleSerializer(read_only=True)

    class Meta:
        model = UserRole
        fields = ["id", "user", "role"]
