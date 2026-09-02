from datetime import datetime
from pydantic import BaseModel
from enum import Enum

class NotificationType(str, Enum):
    MESSAGE = "message"
    ALERT = "alert"
    WARNING = "warning"
    SUCCESS = "success"
    SYSTEM = "system"

class NotificationBase(BaseModel):
    message: str
    type: NotificationType = NotificationType.MESSAGE
    is_read: bool = False


class NotificationCreate(NotificationBase):
    pass


class Notification(NotificationBase):
    id: int
    user_id: int
    created_at: datetime

    class Config:
        from_attributes = True
