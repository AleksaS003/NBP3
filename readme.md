## Shongo - Online Prodavnica

# Potrebno je imati:
docker
docker-compose

# Pokretanje:


# 1. Uđite u kontejner
```docker-compose exec web bash```

# 2. Napravite migracije
```python manage.py makemigrations core```

# 3. Primenite migracije
```python manage.py migrate core```

# 4. Izlaz
```exit```

# 5. pokretanje

```docker-compose up -d --build```