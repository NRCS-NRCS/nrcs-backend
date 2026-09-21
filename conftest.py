import pytest
from django.db import connection
from django.db.migrations.executor import MigrationExecutor


@pytest.fixture
def restore_migration_state():
    """Put the test database back on the latest migrations once the test is done.

    Migration tests rewind the schema to a historical point and step forward
    again, which leaves the database wherever the test stopped. Every later test
    in the same session would then run against that stale schema, so roll the
    graph back up to its leaves on teardown.
    """
    yield

    executor = MigrationExecutor(connection)
    executor.loader.build_graph()
    targets = executor.loader.graph.leaf_nodes()
    if executor.migration_plan(targets):
        executor.migrate(targets)
