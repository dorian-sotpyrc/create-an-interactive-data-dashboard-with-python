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

    # Resolve project root and default paths
    root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
    default_config_path = os.path.join(root_dir, "config", "dashboard.yml")
    default_data_path = os.path.join(root_dir, "data", "sample_sales.csv")

    # 1) Load dashboard config from YAML
    config_path = os.getenv("DASHBOARD_CONFIG_PATH", default_config_path)
    dashboard_config = load_dashboard_config(config_path)

    # 2) Decide which CSV to load, priority:
    #    a) DASHBOARD_DATA_PATH env (absolute or relative)
    #    b) dashboard_config["data_source"]
    #    c) default_data_path (original sample_sales.csv)
    env_data_path = os.getenv("DASHBOARD_DATA_PATH")

    if env_data_path:
        if not os.path.isabs(env_data_path):
            data_path = os.path.join(root_dir, env_data_path)
        else:
            data_path = env_data_path
    else:
        cfg_data_source = dashboard_config.get("data_source")
        if cfg_data_source:
            if not os.path.isabs(cfg_data_source):
                data_path = os.path.join(root_dir, cfg_data_source)
            else:
                data_path = cfg_data_source
        else:
            data_path = default_data_path

    print("[dashboard] Using config:", config_path)
    print("[dashboard] Loading data from:", data_path)

    # 3) Load dashboard data once at startup
    df = load_data(data_path, dashboard_config)

    # Store in app config for access in routes
    app.config["DASHBOARD_CONFIG"] = dashboard_config
    app.config["DATAFRAME"] = df

    # Register blueprint
    app.register_blueprint(dashboard_bp)

    return app
