# Storytelling Server
This is a Django project that functions as a middleware to connect the Storytelling mobile app, Fitbit, and more.

## Getting Started

### Setup Python's virtual environment for Storytelling
```bash
virtualenv venv
source venv/bin/activate
pip install mysql-connector-python-rf
pip install mysqlclient
pip install django
pip install djangorestframework
pip install fitbit
python manage.py migrate
python manage.py runserver
````

## Prerequisites
- MySQL 5.6
- [Fitbit API](https://dev.fitbit.com/docs/)
- [Android 7.0 SDK](https://developer.android.com)

## Authors
* **Herman Saksono** - *Initial work* - [CCIS Website](http://ccs.neu.edu/~hsaksono)

## Running the tests

Explain how to run the automated tests for this system

### Break down into end to end tests

Explain what these tests test and why

```
Give an example
```

### And coding style tests

Explain what these tests test and why

```
Give an example
```

## Deployment

Add additional notes about how to deploy this on a live system

## Built With

* [Django 1.11](https://www.djangoproject.com/) - The web framework used

## Contributing