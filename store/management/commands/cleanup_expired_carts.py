"""
Management command to clean up cart items associated with expired sessions.
Run periodically via cron: python manage.py cleanup_expired_carts
"""
import time
from django.core.management.base import BaseCommand
from django.contrib.sessions.models import Session
from store.models import CartItem


class Command(BaseCommand):
    help = 'Remove cart items for expired or non-existent sessions'

    def handle(self, *args, **options):
        self.stdout.write("Starting cleanup of expired session cart items...")
        start_time = time.time()
        
        try:
            # Gather all active session keys from the session store
            active_sessions = set(
                Session.objects.values_list('session_key', flat=True)
            )
            
            # Exclude items belonging to active sessions to identify orphaned cart items
            orphaned_items = CartItem.objects.exclude(session_key__in=active_sessions)
            count = orphaned_items.count()
            
            if count > 0:
                orphaned_items.delete()
                self.stdout.write(
                    self.style.SUCCESS(f'Successfully cleaned up {count} orphaned cart items')
                )
            else:
                self.stdout.write(
                    self.style.SUCCESS('No orphaned cart items found. Clean up complete.')
                )
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'An error occurred during cart clean up: {str(e)}')
            )
            
        duration = time.time() - start_time
        self.stdout.write(f"Execution finished in {duration:.3f} seconds.")
