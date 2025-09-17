from aiodataloader import DataLoader
from collections import defaultdict
from .models import User, DeployedApp

class UserLoader(DataLoader):
    async def batch_load_fn(self, keys):
        user_map = await User.objects.in_bulk(keys)
        return [user_map.get(k) for k in keys]

class AppsByUserLoader(DataLoader):
    async def batch_load_fn(self, user_ids):
        apps = await DeployedApp.objects.filter(owner_id__in=user_ids).aall()
        grouped = defaultdict(list)
        for app in apps:
            grouped[app.owner_id].append(app)
        return [grouped.get(uid, []) for uid in user_ids]

def get_dataloaders():
    return {
        "user_loader": UserLoader(),
        "apps_by_user": AppsByUserLoader(),
    }
