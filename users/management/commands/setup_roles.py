from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from users.models import CustomUser

class Command(BaseCommand):
    help = 'Create user roles and assign permissions'

    def handle(self, *args, **kwargs):
        # Define groups and their permissions
        roles_permissions = {
            'Admin': [
                'add_user', 'change_user', 'delete_user', 'view_user',
                'add_blog', 'change_blog', 'delete_blog', 'view_blog',
                'add_product', 'change_product', 'delete_product', 'view_product',
                'add_order', 'change_order', 'delete_order', 'view_order',
            ],
            'Student': [
                'view_blog', 'view_product', 'add_order', 'view_order'
            ],
        }

        for role, permissions in roles_permissions.items():
            group, created = Group.objects.get_or_create(name=role)

            for permission_codename in permissions:
                try:
                    permission = Permission.objects.get(codename=permission_codename)
                    group.permissions.add(permission)
                except Permission.DoesNotExist:
                    self.stdout.write(f"Permission '{permission_codename}' not found.")

            self.stdout.write(f"Group '{role}' created or updated.")

        self.stdout.write('Roles and permissions setup complete.')
