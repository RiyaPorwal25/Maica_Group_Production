from django.core.management.base import BaseCommand
from myapp.models import RolePermission


class Command(BaseCommand):
    help = 'Initialize default role permissions from hard-coded logic'

    def handle(self, *args, **options):
        try:
            RolePermission.initialize_permissions()
            self.stdout.write(
                self.style.SUCCESS('Successfully initialized role permissions!')
            )
            
            # Display initialized permissions
            self.stdout.write('\nPermissions initialized:')
            for role, _ in RolePermission.ROLES:
                perms = RolePermission.get_role_permissions(role)
                modules = [m for m, _ in RolePermission.MODULES if perms.get(m, False)]
                self.stdout.write(f'  {role}: {", ".join(modules)}')
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error initializing permissions: {str(e)}')
            )
