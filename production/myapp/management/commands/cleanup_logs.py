from django.core.management.base import BaseCommand
from django.conf import settings
import os
import time
from datetime import datetime, timedelta


class Command(BaseCommand):
    help = 'Clean up log files older than specified days (default: 90 days)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--days',
            type=int,
            default=90,
            help='Delete logs older than this many days (default: 90)'
        )

    def handle(self, *args, **options):
        days = options['days']
        cutoff_date = datetime.now() - timedelta(days=days)
        
        log_dirs = [
            os.path.join(settings.BASE_DIR, 'logs', 'errors'),
            os.path.join(settings.BASE_DIR, 'logs', 'audit'),
            os.path.join(settings.BASE_DIR, 'logs', 'business'),
        ]

        deleted_files = 0
        total_size = 0

        for log_dir in log_dirs:
            if not os.path.exists(log_dir):
                self.stdout.write(self.style.WARNING(f'Directory not found: {log_dir}'))
                continue

            for filename in os.listdir(log_dir):
                filepath = os.path.join(log_dir, filename)
                
                # Skip directories
                if os.path.isdir(filepath):
                    continue
                
                # Skip the current active log file
                if filename.endswith('.log') and not filename.endswith('.log.1'):
                    continue
                
                # Check file modification time
                file_mtime = datetime.fromtimestamp(os.path.getmtime(filepath))
                
                if file_mtime < cutoff_date:
                    # Get file size before deleting
                    file_size = os.path.getsize(filepath)
                    total_size += file_size
                    
                    try:
                        os.remove(filepath)
                        deleted_files += 1
                        self.stdout.write(
                            self.style.SUCCESS(f'Deleted: {filename} (modified: {file_mtime.strftime("%Y-%m-%d")})')
                        )
                    except Exception as e:
                        self.stdout.write(
                            self.style.ERROR(f'Failed to delete {filename}: {str(e)}')
                        )

        # Convert bytes to MB
        size_mb = total_size / (1024 * 1024)
        
        self.stdout.write(
            self.style.SUCCESS(
                f'\nCleanup completed:\n'
                f'  - Files deleted: {deleted_files}\n'
                f'  - Space freed: {size_mb:.2f} MB\n'
                f'  - Cutoff date: {cutoff_date.strftime("%Y-%m-%d")}'
            )
        )