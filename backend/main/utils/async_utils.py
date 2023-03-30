from typing import Any

from asgiref.sync import sync_to_async
from django.db.models import Model


async def get_model_prop(model: Model, prop: str) -> Any:
    return await sync_to_async(lambda: getattr(model, prop))()
