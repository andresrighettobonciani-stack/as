# Python 3.13 Compatibility Fix

## Problem
`psycopg2-binary==2.9.9` is **not compatible** with Python 3.13. The build fails with compilation errors related to deprecated Python C API functions.

## Solution Applied

### 1. Updated `requirements.txt`
**Changed from:**
```
psycopg2-binary==2.9.9
```

**Changed to:**
```
psycopg[binary]==3.1.18
```

### 2. Why psycopg3?
- **psycopg3** (also known as `psycopg`) is the modern PostgreSQL adapter for Python
- Fully compatible with Python 3.13
- Officially supported by Django 4.2+
- Better performance and async support
- Drop-in replacement for psycopg2

### 3. Django Compatibility
Django 5.0 (used in this project) **fully supports** psycopg3 out of the box. No code changes needed.

## Installation Instructions

### For VPS/Server Deployment:

```bash
# Install system dependencies (Ubuntu/Debian)
sudo apt update
sudo apt install python3-pip python3-dev libpq-dev postgresql postgresql-contrib

# Install Python dependencies
pip install -r requirements.txt
```

### For Heroku/Railway:
No changes needed - the buildpack will automatically install psycopg3.

### For Local Development:
```bash
pip install -r requirements.txt
```

## Alternative Solutions

If you prefer to use Python 3.11 instead:

### Option A: Update `runtime.txt`
```
python-3.11.7
```

### Option B: Use pyenv to switch Python version
```bash
pyenv install 3.11.7
pyenv local 3.11.7
```

Then revert `requirements.txt` to use `psycopg2-binary==2.9.9`.

## Recommended Approach
✅ **Keep psycopg3** - It's the future-proof solution and works perfectly with Django 5.0 and Python 3.13.

## Testing
After installation, verify the database connection:
```bash
python manage.py check --database default
```

## References
- [psycopg3 Documentation](https://www.psycopg.org/psycopg3/)
- [Django PostgreSQL Notes](https://docs.djangoproject.com/en/5.0/ref/databases/#postgresql-notes)
