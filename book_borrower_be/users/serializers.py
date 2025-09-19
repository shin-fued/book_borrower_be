from rest_framework import serializers
from .models import Roles, UserRole, Users


class UserSerializer(serializers.ModelSerializer):
    # Change this to SerializerMethodField for reading
    roles = serializers.SerializerMethodField()

    class Meta:
        model = Users
        fields = ["id", "username", "phone_number", "roles", "created_at"]

    lookup_field = "username"

    def get_roles(self: "UserSerializer", obj: Users) -> list[dict[str, any]]:
        # get all roles for this user via the join table
        user_roles = UserRole.objects.filter(user_id=obj.id)
        roles = [ur.role for ur in user_roles]
        return RoleSerializer(roles, many=True).data

    def to_internal_value(self: "UserSerializer", data: object) -> dict[str, any]:
        # Handle roles input during create/update
        if "roles" in data:
            # Store roles for later processing in create/update methods
            self._roles_data = data.pop("roles", [])
        else:
            self._roles_data = []
        return super().to_internal_value(data)

    def create(self: "UserSerializer", validated_data: dict[str, any]) -> Users:
        # Get roles from the stored data
        roles_data = getattr(self, "_roles_data", [])
        user = Users.objects.create(**validated_data)

        # handle roles
        for role_name in roles_data:
            role_obj = Roles.objects.get(name=role_name)
            UserRole.objects.create(user=user, role=role_obj)

        return user

    def update(
        self: "UserSerializer", instance: Users, validated_data: dict[str, any]
    ) -> Users:
        # Get roles from the stored data
        roles_data = getattr(self, "_roles_data", None)

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
