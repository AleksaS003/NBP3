# 1. Uđite u kontejner
docker-compose exec web bash

# 2. Napravite migracije
python manage.py makemigrations core

# 3. Primenite migracije
python manage.py migrate core

# 4. Izlaz
exit

# 5. Restartujte aplikaciju (opciono)
docker-compose restart web