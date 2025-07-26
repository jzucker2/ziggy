"""
Tests for Gunicorn configuration.
"""

import importlib.util
import multiprocessing
import os
from unittest.mock import patch


def load_gunicorn_config():
    """Load the gunicorn configuration file."""
    spec = importlib.util.spec_from_file_location(
        "gunicorn.conf", "gunicorn.conf.py"
    )
    config = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(config)
    return config


class TestGunicornConfiguration:
    """Test cases for Gunicorn configuration."""

    def test_gunicorn_config_file_exists(self):
        """Test that the Gunicorn configuration file exists."""
        config = load_gunicorn_config()
        assert hasattr(config, "bind")
        assert hasattr(config, "workers")
        assert hasattr(config, "worker_class")

    def test_default_worker_count(self):
        """Test that the default worker count is calculated correctly."""
        expected_workers = multiprocessing.cpu_count() * 2 + 1

        # Mock environment to test default calculation
        with patch.dict(os.environ, {}, clear=True):
            # Import the config module to trigger the calculation
            config = load_gunicorn_config()
            assert config.workers == expected_workers

    def test_custom_worker_count(self):
        """Test that custom worker count is respected."""
        custom_workers = "8"

        with patch.dict(os.environ, {"GUNICORN_WORKERS": custom_workers}):
            # Import the config module to trigger the calculation
            config = load_gunicorn_config()
            assert config.workers == int(custom_workers)

    def test_default_bind_address(self):
        """Test that the default bind address is correct."""
        with patch.dict(os.environ, {}, clear=True):
            config = load_gunicorn_config()
            assert config.bind == "0.0.0.0:8000"

    def test_custom_bind_address(self):
        """Test that custom bind address is respected."""
        custom_bind = "127.0.0.1:9000"

        with patch.dict(os.environ, {"GUNICORN_BIND": custom_bind}):
            config = load_gunicorn_config()
            assert config.bind == custom_bind

    def test_default_worker_class(self):
        """Test that the default worker class is correct."""
        with patch.dict(os.environ, {}, clear=True):
            config = load_gunicorn_config()
            assert config.worker_class == "uvicorn.workers.UvicornWorker"

    def test_custom_worker_class(self):
        """Test that custom worker class is respected."""
        custom_class = "uvicorn.workers.UvicornH11Worker"

        with patch.dict(os.environ, {"GUNICORN_WORKER_CLASS": custom_class}):
            config = load_gunicorn_config()
            assert config.worker_class == custom_class

    def test_default_timeout(self):
        """Test that the default timeout is correct."""
        with patch.dict(os.environ, {}, clear=True):
            config = load_gunicorn_config()
            assert config.timeout == 30

    def test_custom_timeout(self):
        """Test that custom timeout is respected."""
        custom_timeout = "60"

        with patch.dict(os.environ, {"GUNICORN_TIMEOUT": custom_timeout}):
            config = load_gunicorn_config()
            assert config.timeout == int(custom_timeout)

    def test_default_log_level(self):
        """Test that the default log level is correct."""
        with patch.dict(os.environ, {}, clear=True):
            config = load_gunicorn_config()
            assert config.loglevel == "info"

    def test_custom_log_level(self):
        """Test that custom log level is respected."""
        custom_level = "debug"

        with patch.dict(os.environ, {"GUNICORN_LOG_LEVEL": custom_level}):
            config = load_gunicorn_config()
            assert config.loglevel == custom_level

    def test_access_log_enabled(self):
        """Test that access log is enabled by default."""
        with patch.dict(os.environ, {}, clear=True):
            config = load_gunicorn_config()
            assert config.accesslog == "-"

    def test_access_log_disabled(self):
        """Test that access log can be disabled."""
        with patch.dict(os.environ, {"GUNICORN_ACCESS_LOG": ""}):
            config = load_gunicorn_config()
            assert config.accesslog == ""

    def test_max_requests_default(self):
        """Test that the default max requests is correct."""
        with patch.dict(os.environ, {}, clear=True):
            config = load_gunicorn_config()
            assert config.max_requests == 1000

    def test_custom_max_requests(self):
        """Test that custom max requests is respected."""
        custom_max = "500"

        with patch.dict(os.environ, {"GUNICORN_MAX_REQUESTS": custom_max}):
            config = load_gunicorn_config()
            assert config.max_requests == int(custom_max)

    def test_preload_app_default(self):
        """Test that preload app is enabled by default."""
        with patch.dict(os.environ, {}, clear=True):
            config = load_gunicorn_config()
            assert config.preload_app is True

    def test_preload_app_disabled(self):
        """Test that preload app can be disabled."""
        with patch.dict(os.environ, {"GUNICORN_PRELOAD_APP": "false"}):
            config = load_gunicorn_config()
            assert config.preload_app is False

    def test_lifecycle_hooks_exist(self):
        """Test that lifecycle hooks are defined."""
        config = load_gunicorn_config()

        # Check that the hook functions exist
        assert hasattr(config, "on_starting")
        assert hasattr(config, "when_ready")
        assert hasattr(config, "worker_int")
        assert hasattr(config, "post_worker_init")
        assert hasattr(config, "on_exit")

    def test_lifecycle_hooks_are_callable(self):
        """Test that lifecycle hooks are callable functions."""
        config = load_gunicorn_config()

        # Check that the hooks are callable
        assert callable(config.on_starting)
        assert callable(config.when_ready)
        assert callable(config.worker_int)
        assert callable(config.post_worker_init)
        assert callable(config.on_exit)


class TestGunicornStartupScript:
    """Test cases for the Gunicorn startup script."""

    def test_startup_script_exists(self):
        """Test that the startup script exists."""
        import os

        assert os.path.exists("start.sh")

    def test_startup_script_is_executable(self):
        """Test that the startup script is executable."""
        import os
        import stat

        if os.path.exists("start.sh"):
            st = os.stat("start.sh")
            assert bool(st.st_mode & stat.S_IEXEC)

    def test_startup_script_content(self):
        """Test that the startup script contains expected content."""
        with open("start.sh", "r") as f:
            content = f.read()

        # Check for expected content
        assert "gunicorn" in content
        assert "app.main:app" in content
        assert "--config gunicorn.conf.py" in content
        assert "GUNICORN_LOG_LEVEL" in content
        assert "GUNICORN_ACCESS_LOG" in content


class TestGunicornDependencies:
    """Test cases for Gunicorn dependencies."""

    def test_gunicorn_in_requirements(self):
        """Test that Gunicorn is listed in requirements.txt."""
        with open("requirements.txt", "r") as f:
            content = f.read()

        assert "gunicorn" in content
        assert "gunicorn>=" in content

    def test_uvicorn_in_requirements(self):
        """Test that Uvicorn is still in requirements.txt."""
        with open("requirements.txt", "r") as f:
            content = f.read()

        assert "uvicorn" in content
        assert "uvicorn>=" in content
