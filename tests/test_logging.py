import os
import shutil
import tempfile
from unittest.mock import patch

import pytest

from app.logging_config import get_logger, get_logging_config, setup_logging


class TestLoggingConfig:
    """Test cases for logging configuration."""

    def test_get_logging_config_defaults(self):
        """Test that get_logging_config returns default configuration."""
        with patch.dict(os.environ, {}, clear=True):
            config = get_logging_config()

            # Check that default values are used
            assert config["loggers"][""]["level"] == "INFO"
            assert config["loggers"][""]["handlers"] == ["console"]
            assert "console" in config["handlers"]

    def test_get_logging_config_with_env_vars(self):
        """Test that environment variables override defaults."""
        env_vars = {
            "LOG_LEVEL": "DEBUG",
            "LOG_FORMAT": "json",
            "LOG_HANDLERS": "console,file",
            "LOG_FILE": "/tmp/test.log",
            "LOG_MAX_BYTES": "5242880",
            "LOG_BACKUP_COUNT": "3",
        }

        with patch.dict(os.environ, env_vars, clear=True):
            config = get_logging_config()

            # Check that environment variables are respected
            assert config["loggers"][""]["level"] == "DEBUG"
            assert config["loggers"][""]["handlers"] == ["console", "file"]
            assert config["handlers"]["file"]["filename"] == "/tmp/test.log"
            assert config["handlers"]["file"]["maxBytes"] == 5242880
            assert config["handlers"]["file"]["backupCount"] == 3

    def test_get_logging_config_invalid_level(self):
        """Test that invalid log level defaults to INFO."""
        with patch.dict(os.environ, {"LOG_LEVEL": "INVALID"}, clear=True):
            config = get_logging_config()
            assert config["loggers"][""]["level"] == "INFO"

    def test_get_logging_config_invalid_format(self):
        """Test that invalid log format defaults to default."""
        with patch.dict(os.environ, {"LOG_FORMAT": "INVALID"}, clear=True):
            config = get_logging_config()
            # The format doesn't affect the logger level, so we check handlers
            assert config["loggers"][""]["handlers"] == ["console"]

    def test_get_logging_config_invalid_handlers(self):
        """Test that invalid handlers are filtered out."""
        with patch.dict(
            os.environ, {"LOG_HANDLERS": "console,invalid,file"}, clear=True
        ):
            config = get_logging_config()
            assert config["loggers"][""]["handlers"] == ["console", "file"]

    def test_get_logging_config_empty_handlers(self):
        """Test that empty handlers list defaults to console."""
        with patch.dict(os.environ, {"LOG_HANDLERS": "invalid"}, clear=True):
            config = get_logging_config()
            assert config["loggers"][""]["handlers"] == ["console"]

    def test_get_logging_config_file_handler_creation(self):
        """Test that log directory is created when file handler is used."""
        temp_dir = tempfile.mkdtemp()
        log_file = os.path.join(temp_dir, "logs", "app.log")

        try:
            env_vars = {
                "LOG_HANDLERS": "file",
                "LOG_FILE": log_file,
            }

            with patch.dict(os.environ, env_vars, clear=True):
                config = get_logging_config()

                # Check that directory was created
                log_dir = os.path.dirname(log_file)
                assert os.path.exists(log_dir)

                # Check that file handler is configured
                assert config["handlers"]["file"]["filename"] == log_file
        finally:
            shutil.rmtree(temp_dir)

    def test_get_logger_default_name(self):
        """Test that get_logger returns logger with default name."""
        logger = get_logger()
        assert logger.name == "app"

    def test_get_logger_custom_name(self):
        """Test that get_logger returns logger with custom name."""
        logger = get_logger("test_logger")
        assert logger.name == "test_logger"

    def test_setup_logging_no_errors(self):
        """Test that setup_logging doesn't raise errors."""
        try:
            setup_logging()
        except Exception as e:
            pytest.fail(f"setup_logging raised an exception: {e}")

    def test_logging_config_structure(self):
        """Test that the logging configuration has the expected structure."""
        config = get_logging_config()

        # Check required top-level keys
        assert "version" in config
        assert "disable_existing_loggers" in config
        assert "formatters" in config
        assert "handlers" in config
        assert "loggers" in config

        # Check formatters
        assert "default" in config["formatters"]
        assert "json" in config["formatters"]
        assert "simple" in config["formatters"]

        # Check handlers
        assert "console" in config["handlers"]
        assert "file" in config["handlers"]
        assert "json_console" in config["handlers"]

        # Check loggers
        assert "" in config["loggers"]  # Root logger
        assert "app" in config["loggers"]
        assert "uvicorn" in config["loggers"]
        assert "uvicorn.access" in config["loggers"]

    def test_logging_config_default_formats(self):
        """Test that default logging formats are properly configured."""
        config = get_logging_config()

        # Check default formatter
        default_format = config["formatters"]["default"]["format"]
        assert "%(asctime)s" in default_format
        assert "%(name)s" in default_format
        assert "%(levelname)s" in default_format
        assert "%(message)s" in default_format

        # Check JSON formatter
        json_format = config["formatters"]["json"]["format"]
        assert "timestamp" in json_format
        assert "level" in json_format
        assert "logger" in json_format
        assert "message" in json_format

        # Check simple formatter
        simple_format = config["formatters"]["simple"]["format"]
        assert "%(levelname)s" in simple_format
        assert "%(message)s" in simple_format

    def test_logging_config_handler_levels(self):
        """Test that handler levels are properly configured."""
        config = get_logging_config()

        # Check console handler
        assert config["handlers"]["console"]["level"] == "INFO"
        assert config["handlers"]["console"]["formatter"] == "default"

        # Check file handler
        assert config["handlers"]["file"]["level"] == "DEBUG"
        assert config["handlers"]["file"]["formatter"] == "default"

        # Check JSON console handler
        assert config["handlers"]["json_console"]["level"] == "INFO"
        assert config["handlers"]["json_console"]["formatter"] == "json"
