# praktikum_new_diplom

Foodgram is a web application for sharing recipes. 
Create your unique recipes and upload them to the website, read other
users' recipes and add them to favorites. 
Subscribe to other users to keep up with their new recipes.

### Requests Examples:

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