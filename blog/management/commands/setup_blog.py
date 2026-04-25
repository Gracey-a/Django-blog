import os
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from blog.models import Post

class Command(BaseCommand):
    help = 'Create superuser and a default post if none exist'

    def handle(self, *args, **options):
        # Create superuser if none exists
        if not User.objects.filter(is_superuser=True).exists():
            username = 'admin'
            email = 'admin@example.com'
            password = os.environ.get('ADMIN_PASSWORD', 'admin123')
            User.objects.create_superuser(username, email, password)
            self.stdout.write(self.style.SUCCESS(f'Superuser {username} created.'))
        else:
            self.stdout.write('Superuser already exists.')

        # Create a sample post if no posts exist
        if Post.objects.count() == 0:
            admin = User.objects.filter(is_superuser=True).first()
            if admin:
                Post.objects.create(
                    title="Welcome to your new blog!",
                    content="This is the first post. You can edit or delete it in the admin panel. Enjoy!",
                    author=admin,
                    status='P',
                )
                self.stdout.write(self.style.SUCCESS('Sample post created.'))
        else:
            self.stdout.write('Posts already exist.')
