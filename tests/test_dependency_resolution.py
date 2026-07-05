from pathlib import Path

from create_app.framework.bundler import Bundler


def resolved_deps(database="sqlite", framework="flask"):
    bundler = Bundler(
        Path("/tmp/example"),
        {
            "project_name": "example",
            "framework": framework,
            "fw_name": framework,
            "build_strategy": "standard",
            "database": database,
        },
    )
    return set(bundler.ctx["dependencies"].splitlines())


def test_mysql_uses_portable_driver():
    deps = resolved_deps(database="mysql")

    assert "PyMySQL" in deps
    assert "mysqlclient" not in deps


def test_sqlite_does_not_pull_native_database_drivers():
    deps = resolved_deps(database="sqlite")

    assert "mysqlclient" not in deps
    assert "psycopg2-binary" not in deps
    assert "psycopg[binary]" not in deps


def test_postgres_uses_modern_binary_package():
    deps = resolved_deps(database="postgresql")

    assert "psycopg[binary]" in deps
    assert "psycopg2-binary" not in deps
