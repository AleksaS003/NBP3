#!/bin/sh

# docker-entrypoint.sh
set -e

echo "Waiting for MongoDB to start..."

# Test konekcije sa više detalja
MAX_ATTEMPTS=30
ATTEMPT=0

while [ $ATTEMPT -lt $MAX_ATTEMPTS ]; do
    echo "Testing connection to mongodb:27017 (attempt $((ATTEMPT+1))/$MAX_ATTEMPTS)..."
    
    if python -c "
import socket
import sys
try:
    print(f'Attempting to connect to mongodb:27017...')
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(5)
    s.connect(('mongodb', 27017))
    s.close()
    print('Connection successful!')
    sys.exit(0)
except Exception as e:
    print(f'Connection failed: {e}')
    sys.exit(1)
" ; then
        echo "✓ MongoDB is ready!"
        break
    else
        echo "✗ MongoDB not ready yet..."
    fi
    
    ATTEMPT=$((ATTEMPT + 1))
    echo "Waiting 2 seconds before retry..."
    sleep 2
done

if [ $ATTEMPT -eq $MAX_ATTEMPTS ]; then
    echo "Failed to connect to MongoDB after $MAX_ATTEMPTS attempts"
    echo "Checking if MongoDB is reachable via ping..."
    ping -c 2 mongodb || true
    echo "Checking MongoDB port with nc..."
    nc -zv mongodb 27017 || true
    exit 1
fi

echo "MongoDB started - continuing with setup..."

# Run migrations
echo "Running migrations..."
python manage.py makemigrations --noinput
python manage.py migrate --noinput

# Create superuser if it doesn't exist
echo "Creating superuser if not exists..."
python manage.py shell << 'END'
from django.contrib.auth import get_user_model
import sys
User = get_user_model()
try:
    if not User.objects.filter(username='admin').exists():
        User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
        print('Superuser created.')
    else:
        print('Superuser already exists.')
except Exception as e:
    print(f'Error creating superuser: {e}')
END

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput

# Start server
echo "Starting server..."
exec python manage.py runserver 0.0.0.0:8000