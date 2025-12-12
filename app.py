from app import create_app


if __name__ == "__main__":
    app = create_app()
    # For local development only; use Gunicorn or similar in production
    app.run(host="127.0.0.1", port=5000, debug=app.config.get("DEBUG", True))
