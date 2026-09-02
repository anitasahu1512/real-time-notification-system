import json

from app.services.redis_client import get_redis_client
from app.websocket.manager import manager


CHANNEL_NAME = "notifications"


async def publish_notification(notification: dict):
    redis_client = get_redis_client()

    try:
        await redis_client.publish(
            CHANNEL_NAME,
            json.dumps(notification)
        )
    except Exception as e:
        print(f"Redis publish error: {e}")
    finally:
        await redis_client.aclose()


async def subscribe_notifications():
    redis_client = get_redis_client()
    pubsub = redis_client.pubsub()

    try:
        await pubsub.subscribe(CHANNEL_NAME)
        print("Redis subscriber started...")

        async for message in pubsub.listen():
            if message["type"] != "message":
                continue

            try:
                notification = json.loads(message["data"])
                print("Notification from Redis:", notification)

                user_id = notification.get("user_id")

                if user_id is not None:
                    await manager.send_to_user(
                        int(user_id),
                        notification
                    )

            except Exception as e:
                print(f"Notification processing error: {e}")

    except Exception as e:
        print(f"Redis subscriber error: {e}")

    finally:
        try:
            await pubsub.unsubscribe(CHANNEL_NAME)
        except Exception:
            pass

        await pubsub.aclose()
        await redis_client.aclose()

        print("Redis subscriber stopped.")