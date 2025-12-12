from app import create_app


if __name__ == "__main__":
    app = create_app()
    # For local development only; use Gunicorn or similar in production
    app.run(host="0.0.0.0", port=8509, debug=app.config.get("DEBUG", True))
