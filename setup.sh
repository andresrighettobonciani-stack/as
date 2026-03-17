#!/bin/bash

echo "Setting up Anonymous Social Network..."

if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

echo "Activating virtual environment..."
source venv/bin/activate

echo "Installing dependencies..."
pip install -r requirements.txt

echo "Running migrations..."
python manage.py makemigrations
python manage.py migrate

echo ""
echo "Setup complete!"
echo ""
echo "To start the server:"
echo "1. Activate the virtual environment: source venv/bin/activate"
echo "2. Run the server: python manage.py runserver"
echo "3. Visit http://127.0.0.1:8000 in your browser"
