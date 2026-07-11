"""WSGI entry point. Run locally with:  flask --app wsgi run  (after seeding)."""
from app import create_app

app = create_app()

if __name__ == "__main__":
    app.run(debug=True, port=5000)
