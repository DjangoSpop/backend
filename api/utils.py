from .models import Notification , CustomUser
from django.contrib.auth import get_user_model

# Get the CustomUser model (or default User model)
User = CustomUser()


def create_notification(user, notification_type, message, related_object_id=None):
    """
    Creates a notification for a specific
     user.

    Parameters:
    - user: CustomUser instance or user ID.
    - notification_type: The type of notification (string).
    - message: The message content (string).
    - related_object_id: Optional, related object for the notification (default: None).
    """
    # If `user` is passed as an ID, fetch the corresponding `CustomUser` instance
    if isinstance(user, int):  # Check if the user is passed as an ID
        try:
            user = CustomUser.objects.get(id=user)  # Fetch the user
        except CustomUser.DoesNotExist:
            raise ValueError(f"User with id {user} does not exist")

    # Create the notification with the valid user instance
    return Notification.objects.create(
        user=user,  # Pass the user instance here
        type=notification_type,
        message=message,
        related_object_id=related_object_id
    )
    # create_notification(
    #     user=user_instance,
    #     notification_type='GROUP COMPLETED',
    #     message=f'Group Completed {group_buy_instance.max_participants}',
    #     related_object_id=group_buy_instance.GROUP_BUY_STATUS
    # )