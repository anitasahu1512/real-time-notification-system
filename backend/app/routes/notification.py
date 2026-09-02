
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.schemas.notification import Notification, NotificationCreate
from app.models.notification import Notification as NotificationModel
from app.database.database import get_db
from app.websocket.manager import manager
from app.utils.auth import get_current_user
from app.models.user import User
from app.services.pubsub import publish_notification

router = APIRouter()

@router.get("/notifications", response_model=list[Notification])
async def read_notifications(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    is_read: bool | None = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    offset = (page - 1) * limit

    query = db.query(NotificationModel).filter(
    NotificationModel.user_id == current_user.id
    )

    if is_read is not None:
        query = query.filter(
            NotificationModel.is_read == is_read
        )

    notifications = (
        query
        .order_by(NotificationModel.created_at.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )

    return notifications

@router.get("/notifications/{notification_id}", response_model=Notification)
async def read_notification(
    notification_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    notification = db.query(NotificationModel).filter(
        NotificationModel.id == notification_id,
        NotificationModel.user_id == current_user.id
    ).first()

    if notification is None:
        raise HTTPException(
            status_code=404,
            detail="Notification not found"
        )

    return notification


@router.post("/notifications", response_model=Notification)
async def create_notification(
    notification: NotificationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    new_notification = NotificationModel(
        message=notification.message,
        type=notification.type,
        is_read=notification.is_read,
        user_id=current_user.id
    )

    db.add(new_notification)
    db.commit()
    db.refresh(new_notification)

    notification_data = {
        "id": new_notification.id,
        "user_id": new_notification.user_id,
        "message": new_notification.message,
        "type": new_notification.type,
        "is_read": new_notification.is_read,
        "created_at": new_notification.created_at.isoformat()
    }
    await publish_notification(notification_data)
    return new_notification


@router.patch(
    "/notifications/{notification_id}/read",
    response_model=Notification
)
async def mark_notification_as_read(
    notification_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    notification = db.query(NotificationModel).filter(
        NotificationModel.id == notification_id,
        NotificationModel.user_id == current_user.id
    ).first()

    if notification is None:
        raise HTTPException(
            status_code=404,
            detail="Notification not found"
        )

    notification.is_read = True

    db.commit()
    db.refresh(notification)

    return notification

@router.patch("/notifications/read-all")
async def mark_all_notifications_as_read(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    notifications = db.query(NotificationModel).filter(
        NotificationModel.user_id == current_user.id,
        NotificationModel.is_read == False
    ).all()

    for notification in notifications:
        notification.is_read = True

    db.commit()

    return {
        "message": "All notifications marked as read",
        "updated_count": len(notifications)
    }


@router.delete("/notifications/{notification_id}")
async def delete_notification(
    notification_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    notification = db.query(NotificationModel).filter(
        NotificationModel.id == notification_id,
        NotificationModel.user_id == current_user.id
    ).first()

    if notification is None:
        raise HTTPException(
            status_code=404,
            detail="Notification not found"
        )

    db.delete(notification)
    db.commit()

    return {
        "message": "Notification deleted successfully"
    }

@router.delete("/notifications")
async def delete_all_notifications(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    notifications = db.query(NotificationModel).filter(
        NotificationModel.user_id == current_user.id
    ).all()

    deleted_count = len(notifications)

    for notification in notifications:
        db.delete(notification)

    db.commit()

    return {
        "message": "All notifications deleted successfully",
        "deleted_count": deleted_count
    }

