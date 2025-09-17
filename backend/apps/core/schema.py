import strawberry
from typing import List, Optional, Union
from .models import User, DeployedApp


@strawberry.type
class AppType:
    id: strawberry.ID
    active: bool


@strawberry.type
class UserType:
    id: strawberry.ID
    username: str
    plan: str
    apps: List[AppType]


Node = strawberry.union("Node", (UserType, AppType))


@strawberry.type
class Query:
    @strawberry.field
    async def user(self, id: strawberry.ID) -> Optional[UserType]:
        """Fetch a single user by ID (u_1, u_2, etc.)"""
        pk = str(id).replace("u_", "")
        try:
            user = await User.objects.aget(pk=pk)
        except User.DoesNotExist:
            return None

        apps = [
            AppType(id=f"app_{app.pk}", active=app.active)
            async for app in DeployedApp.objects.filter(owner=user)
        ]

        return UserType(
            id=f"u_{user.pk}",
            username=user.username,
            plan=user.plan,
            apps=apps,
        )

    @strawberry.field
    async def app(self, id: strawberry.ID) -> Optional[AppType]:
        pk = str(id).replace("app_", "")
        try:
            app = await DeployedApp.objects.aget(pk=pk)
        except DeployedApp.DoesNotExist:
            return None

        return AppType(id=f"app_{app.pk}", active=app.active)

    @strawberry.field
    async def node(self, id: strawberry.ID) -> Optional[Node]:
        if str(id).startswith("u_"):
            pk = str(id).replace("u_", "")
            try:
                user = await User.objects.aget(pk=pk)
            except User.DoesNotExist:
                return None

            apps = [
                AppType(id=f"app_{app.pk}", active=app.active)
                async for app in DeployedApp.objects.filter(owner=user)
            ]

            return UserType(
                id=f"u_{user.pk}",
                username=user.username,
                plan=user.plan,
                apps=apps,
            )

        elif str(id).startswith("app_"):
            pk = str(id).replace("app_", "")
            try:
                app = await DeployedApp.objects.aget(pk=pk)
            except DeployedApp.DoesNotExist:
                return None

            return AppType(id=f"app_{app.pk}", active=app.active)

        return None


@strawberry.type
class UpgradeAccountPayload:
    user: UserType


@strawberry.type
class DowngradeAccountPayload:
    user: UserType


@strawberry.type
class Mutation:
    @strawberry.mutation
    async def upgrade_account(self, user_id: strawberry.ID) -> Optional[UpgradeAccountPayload]:
        pk = str(user_id).replace("u_", "")
        try:
            user = await User.objects.aget(pk=pk)
        except User.DoesNotExist:
            return None

        user.plan = User.PRO
        await user.asave()

        apps = [
            AppType(id=f"app_{app.pk}", active=app.active)
            async for app in DeployedApp.objects.filter(owner=user)
        ]

        return UpgradeAccountPayload(
            user=UserType(
                id=f"u_{user.pk}",
                username=user.username,
                plan=user.plan,
                apps=apps,
            )
        )

    @strawberry.mutation
    async def downgrade_account(self, user_id: strawberry.ID) -> Optional[DowngradeAccountPayload]:
        pk = str(user_id).replace("u_", "")
        try:
            user = await User.objects.aget(pk=pk)
        except User.DoesNotExist:
            return None

        user.plan = User.HOBBY
        await user.asave()

        apps = [
            AppType(id=f"app_{app.pk}", active=app.active)
            async for app in DeployedApp.objects.filter(owner=user)
        ]

        return DowngradeAccountPayload(
            user=UserType(
                id=f"u_{user.pk}",
                username=user.username,
                plan=user.plan,
                apps=apps,
            )
        )


schema = strawberry.Schema(query=Query, mutation=Mutation, types=[UserType, AppType])
