import graphene
from graphene import relay
from graphene_django import DjangoObjectType
from graphql import GraphQLError

from .models import User, DeployedApp
from .dataloaders import get_dataloaders


TYPE_PREFIXES = {
    "UserType": "u",
    "AppType": "app"
}

class CustomNode(relay.Node):
    class Meta:
        name = "Node"

    @staticmethod
    def to_global_id(type_, id):
        prefix = TYPE_PREFIXES.get(type_)
        if not prefix:
            raise ValueError(f"Unknown type: {type_}")
        return f"{prefix}_{id}"

    @staticmethod
    def get_node_from_global_id(info, global_id, only_type=None):
        try:
            if global_id.startswith("u_"):
                pk = global_id.split("_", 1)[1]
                return User.objects.get(pk=pk)
            elif global_id.startswith("app_"):
                pk = global_id.split("_", 1)[1]
                return DeployedApp.objects.get(pk=pk)
        except User.DoesNotExist:
            raise GraphQLError("User not found.")
        except DeployedApp.DoesNotExist:
            raise GraphQLError("App not found.")
        return None

class UserType(DjangoObjectType):
    class Meta:
        model = User
        interfaces = (CustomNode,)
        fields = ("username", "plan")

    async def resolve_apps(self, info):
        return await info.context["loaders"]["apps_by_user"].load(self.id)

class AppType(DjangoObjectType):
    class Meta:
        model = DeployedApp
        interfaces = (CustomNode,)
        fields = ("active",)

    async def resolve_owner(self, info):
        return await info.context["loaders"]["user_loader"].load(self.owner_id)


class PlanMutationMixin:
    plan_value = None 

    @classmethod
    async def mutate(cls, root, info, user_id):
        try:
            user_pk = user_id.split("_", 1)[1]
            user = await User.objects.aget(pk=user_pk)
        except User.DoesNotExist:
            raise GraphQLError("User not found.")

        user.plan = cls.plan_value
        await user.asave()
        return cls(user=user)


class UpgradeAccount(PlanMutationMixin, graphene.Mutation):
    class Arguments:
        user_id = graphene.ID(required=True)

    user = graphene.Field(UserType)
    plan_value = 'P'

class DowngradeAccount(PlanMutationMixin, graphene.Mutation):
    class Arguments:
        user_id = graphene.ID(required=True)

    user = graphene.Field(UserType)
    plan_value = 'H'


class Query(graphene.ObjectType):
    node = CustomNode.Field()

class Mutation(graphene.ObjectType):
    upgrade_account = UpgradeAccount.Field()
    downgrade_account = DowngradeAccount.Field()

schema = graphene.Schema(query=Query, mutation=Mutation, types=[UserType, AppType])
