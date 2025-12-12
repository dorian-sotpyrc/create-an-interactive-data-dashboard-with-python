import os
from flask import Flask
from dotenv import load_dotenv

from .config_loader import load_dashboard_config
from .data import load_data
from .routes import bp as dashboard_bp


def create_app() -> Flask:
    """Application factory for the Flask dashboard app."""
    # Load environment variables from .env if present
    load_dotenv()

    app = Flask(__name__)

    # Basic config
    app.config["ENV"] = os.getenv("FLASK_ENV", "development")
    app.config["DEBUG"] = os.getenv("FLASK_DEBUG", "1") == "1"

    # Resolve config and data paths
    root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
    default_config_path = os.path.join(root_dir, "config", "dashboard.yml")
    default_data_path = os.path.join(root_dir, "data", "sample_sales.csv")

    config_path = os.getenv("DASHBOARD_CONFIG_PATH", default_config_path)
    data_path = os.getenv("DASHBOARD_DATA_PATH", default_data_path)

    # Load dashboard config and data once at startup
    dashboard_config = load_dashboard_config(config_path)
    df = load_data(data_path, dashboard_config)

    # Store in app config for access in routes
    app.config["DASHBOARD_CONFIG"] = dashboard_config
    app.config["DATAFRAME"] = df

    # Register blueprint
    app.register_blueprint(dashboard_bp)

    return app
