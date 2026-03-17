# Anonymous Social Network

An anonymous social network built with Django, featuring a dark theme with lime green accents inspired by Anonymous aesthetics.

## Features

- **Anonymous User Registration**: Users can create accounts with automatically generated anonymous display names
- **Secure Authentication**: Login/logout functionality with password hashing
- **Dark Theme**: Black background with lime green (#00ff00) borders and accents
- **Modern UI**: Clean, cyberpunk-inspired interface

## Installation

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run migrations:
```bash
python manage.py makemigrations
python manage.py migrate
```

4. Create a superuser (optional):
```bash
python manage.py createsuperuser
```

5. Run the development server:
```bash
python manage.py runserver
```

6. Visit `http://127.0.0.1:8000` in your browser

## Project Structure

```
anonymous_social/
├── anonymous_social/       # Project settings
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── accounts/              # Authentication app
│   ├── models.py         # Custom AnonymousUser model
│   ├── views.py          # Login/Register/Logout views
│   ├── forms.py          # Authentication forms
│   └── urls.py           # App URLs
├── templates/            # HTML templates
│   ├── base.html
│   └── accounts/
│       ├── login.html
│       ├── register.html
│       └── home.html
└── manage.py
```

## Custom User Model

The project uses a custom `AnonymousUser` model that extends Django's `AbstractBaseUser`:
- Username-based authentication
- Auto-generated anonymous display names (e.g., "Anon_A1B2C3")
- Bio field for user descriptions
- Timestamp tracking

## Design

- **Color Scheme**: 
  - Background: #0a0a0a (near black)
  - Primary: #00ff00 (lime green)
  - Accents: Various shades of green
- **Typography**: Courier New monospace font for that hacker aesthetic
- **Effects**: Glowing borders, hover animations, and smooth transitions

## Security Notes

- Change the `SECRET_KEY` in `settings.py` before deploying to production
- Set `DEBUG = False` in production
- Configure `ALLOWED_HOSTS` appropriately
- Use environment variables for sensitive data
- Consider using PostgreSQL instead of SQLite for production

## Next Steps

Potential features to add:
- User profiles with customization
- Anonymous posting system
- Private messaging
- Groups/communities
- Content moderation
- API endpoints

## License

This project is open source and available for educational purposes.
