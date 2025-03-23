from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.core.management import call_command
from django.db import models


class Module(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    is_active = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    @property
    def is_upgradable(self):
        return self.has_unapplied_migrations()

    def activate(self):
        if self.is_active:
            return

        self.is_active = True
        self.save()

    def deactivate(self):
        if not self.is_active:
            return

        self.is_active = False
        self.save()

    def upgrade(self):
        """
        Run database migrations for this module.
        Assumes the module name corresponds to a Django app name.
        Checks if the module is in INSTALLED_APPS before migrating.
        """
        if self.name not in settings.INSTALLED_APPS:
            msg = (
                f"Cannot migrate module '{self.name}'. "
                f"It is not in INSTALLED_APPS setting."
            )
            raise ImproperlyConfigured(
                msg,
            )

        if not self.is_active:
            msg = f"Cannot migrate module '{self.name}'. It is not activated."
            raise ImproperlyConfigured(
                msg,
            )

        if not self.has_unapplied_migrations():
            return

        call_command("migrate", self.name)

    def has_unapplied_migrations(self):
        """
        Check if this module has any unapplied migrations.
        Returns True if there are migrations that need to be applied, False otherWwise.
        """
        loader, applied = self._get_migration_context()

        # Check if there are any unapplied migrations for this app
        app_migrations = [key for key in loader.graph.nodes if key[0] == self.name]

        return any(migration not in applied for migration in app_migrations)

    def get_unapplied_migrations(self):
        """
        Get a list of unapplied migrations for this module.
        Returns a list of migration names that need to be applied.
        """
        loader, applied = self._get_migration_context()

        # Find unapplied migrations for this app
        unapplied = []
        app_migrations = [key for key in loader.graph.nodes if key[0] == self.name]

        for migration in app_migrations:
            if migration not in applied:
                # Add as a tuple of (app_name, migration_name)
                unapplied.append(migration)  # noqa: PERF401

        # Sort by dependencies to maintain proper order
        sorted_migrations = []
        for migration in loader.graph.leaf_nodes():
            if migration[0] == self.name and migration in unapplied:
                for node in loader.graph.backwards_plan(migration):
                    if (
                        node[0] == self.name
                        and node in unapplied
                        and node not in sorted_migrations
                    ):
                        sorted_migrations.append(node)

        # Return the full tuples (app_name, migration_name)
        return sorted_migrations

    def _get_migration_context(self):
        """Get the common migration context for checking migrations."""
        from django.db import connections
        from django.db.migrations.loader import MigrationLoader
        from django.db.migrations.recorder import MigrationRecorder

        if self.name not in settings.INSTALLED_APPS:
            msg = f"Cannot check migrations for module '{self.name}'. It is not in INSTALLED_APPS setting."  # noqa: E501
            raise ImproperlyConfigured(msg)

        connection = connections["default"]
        loader = MigrationLoader(connection)
        recorder = MigrationRecorder(connection)
        applied = {tuple(x) for x in recorder.applied_migrations()}

        return loader, applied
