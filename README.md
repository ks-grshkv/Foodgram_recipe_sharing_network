# praktikum_new_diplom
# CHECK IT OUT AT http://finalprjct-foodgram.sytes.net or http://62.84.113.104/

### test user username sup

email sup@sup.sup

password sup

Foodgram is a web application for sharing recipes. 
Create your unique recipes and upload them to the website, read other
users' recipes and add them to favorites. 
Subscribe to other users to keep up with their new recipes.

### API Requests Examples for local testing:

```
Signup for new users:  
###  
POST http://127.0.0.1:8000/api/users/  
Content-Type: application/json  

{  
    "username": "test_user",  
    "password": "test_password",  
    "email": "test@email.com",  
    "first_name": "Test",  
    "last_name": "Test"  
}

Login:  
###  
POST http://127.0.0.1:8000/api/auth/token/login/  
Content-Type: application/json

{  
    "password": "test_password",  
    "email": "test@email.com"  
}  

Logout:  
###  
POST  http://127.0.0.1:8000/api/auth/token/logout/  
Content-Type: application/json  
Authorization: Token <insert_token_here>  

All recipes:  
###  
GET http://127.0.0.1:8000/api/recipes/  
Content-Type: application/json 
```

### Launching project :

```
git clone https://github.com/ks-grshkv/foodgram-project-react.git
```

In foodgram-project-react folder
Activate virtual environment

```
python3 -m venv env
```
```
source venv/bin/activate
```

Install requirements from requirements.txt:

```
python3 -m pip3 install --upgrade pip
```
```
pip3 install -r requirements.txt
```

Then go to the folder containing manage.py file:

```
cd backend/foodgram
```

Run migrations:

```
python3 manage.py migrate
```

Make sure you have a postgres database set up
and start the project:

```
python3 manage.py runserver
```

## Run in docker-compose

```
cd infra

# execute when you run app with config that builds all the stuff localy
docker-compose up --detach --build 

docker-compose exec backend python manage.py migrate
docker-compose exec backend python manage.py createsuperuser
docker-compose exec backend python manage.py collectstatic --no-input

# stop and purge all the data
docker-compose down -v
```

## .env example:

```
SECRET_KEY=YOUR-SECRET-KEY
DB_ENGINE=django.db.backends.postgresql
DB_NAME=postgres_database
POSTGRES_USER=postgres_user
POSTGRES_PASSWORD=postgres_pass
DB_HOST=127.0.0.1
# DB_HOST=db # to run with docker-compose
DB_PORT=5432
API_URL=http://<ip>
IP=<ip>
```
