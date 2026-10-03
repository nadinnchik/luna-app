import logging
from fastapi import APIRouter, Depends
from app.schemas.schemas import AnalyticsEventSchema
from app.models.models import User
from app.core.deps import get_current_user

logger = logging.getLogger("luna.analytics")

router = APIRouter()


@router.post("/event")
def log_analytics_event(
    event_data: AnalyticsEventSchema,
    current_user: User = Depends(get_current_user)
):
    """
    Log funnel analytics event for marketing telemetry.
    """
    logger.info(
        f"[ANALYTICS] user={current_user.telegram_id} event={event_data.event} payload={event_data.payload}"
    )
    return {"status": "ok", "event": event_data.event}
