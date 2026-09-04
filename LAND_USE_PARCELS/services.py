from datetime import timedelta
from django.utils import timezone
from django.core.exceptions import PermissionDenied
from django.contrib.auth.models import User

LOCK_TIMEOUT = timedelta(minutes=5)

class ParcelLockService:
    @staticmethod
    def acquire(parcel, user):
        if parcel.locked_by and parcel.locked_by != user:
            # Check if lock expired
            if parcel.locked_at and timezone.now() - parcel.locked_at > LOCK_TIMEOUT:
                # Auto‑release expired lock
                parcel.locked_by = None
                parcel.locked_at = None
                parcel.save(update_fields=['locked_by', 'locked_at'])
            else:
                raise PermissionDenied(
                    f'Parcel is locked by {parcel.locked_by.username} since {parcel.locked_at}'
                )

        # Acquire lock
        parcel.locked_by = user
        parcel.locked_at = timezone.now()
        parcel.lock_version += 1
        parcel.save(update_fields=['locked_by', 'locked_at', 'lock_version'])
        return True

    @staticmethod
    def renew(parcel, user):
        if parcel.locked_by != user:
            raise PermissionDenied('You do not own this lock')
        parcel.locked_at = timezone.now()
        parcel.save(update_fields=['locked_at'])
        return True

    @staticmethod
    def release(parcel, user):
        if parcel.locked_by == user or (parcel.locked_by is None):
            parcel.locked_by = None
            parcel.locked_at = None
            parcel.save(update_fields=['locked_by', 'locked_at'])
            return True
        raise PermissionDenied('You do not own this lock')

    @staticmethod
    def get_status(parcel):
        if parcel.locked_by and parcel.locked_at:
            if timezone.now() - parcel.locked_at > LOCK_TIMEOUT:
                # Auto‑release expired lock (in getter)
                parcel.locked_by = None
                parcel.locked_at = None
                parcel.save(update_fields=['locked_by', 'locked_at'])
                return {'locked': False, 'locked_by': None}
            return {
                'locked': True,
                'locked_by': parcel.locked_by.username,
                'locked_at': parcel.locked_at.isoformat()
            }
        return {'locked': False, 'locked_by': None}