"""
Management command to clean up cart items associated with expired sessions.
Run periodically via cron: python manage.py cleanup_expired_carts
"""
from django.core.management.base import BaseCommand
from django.contrib.sessions.models import Session
from store.models import CartItem


class Command(BaseCommand):
    help = 'Remove cart items for expired or non-existent sessions'

    def handle(self, *args, **options):
        active_sessions = set(
            Session.objects.values_list('session_key', flat=True)
        )
        orphaned_items = CartItem.objects.exclude(session_key__in=active_sessions)
        count = orphaned_items.count()
        orphaned_items.delete()
        self.stdout.write(
            self.style.SUCCESS(f'Cleaned up {count} orphaned cart items')
        )
