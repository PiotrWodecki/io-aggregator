# io-aggregator

## Overview
io-aggregator is a website designed for InternetoweOkazje S.A. which is an online shopping aggregator website.
The site allows for selecting multiple products and finding a common seller, which lowers the shopping cart’s total sum.
Additional features include: Allegro.pl filtering, User registration and login, and searching for multiple products using a text file.

## Development environment
### Requirements
- Python 3.10 or higher
- pip3
- venv
### Environment setup

1. Clone the repository from Git:
```
git clone https://github.com/PiotrWodecki/io-aggregator.git
```
2. Create a virtual environment:
```
python3 -m venv myenv
```
3. Activate the virtual environment:
```
source myenv/bin/activate
```
4. Install the required packages from requirements.txt:
```
pip3 install -r requirements.txt
```
5. Migrate DB:
```
python3 manage.py migrate
```
6. Run the Django project:
```
python3 manage.py runserver
```
You have successfully set up the Django project with virtual environment and required packages.

To achieve full SMTP functionality, add `EMAIL_HOST_USER` and `EMAIL_HOST_PASSWORD` environment variables, otherwise emails will be saved to `/tmp/app-messages`.

## Deployment
Recommended deployment stack is **Apache + mod_wsgi**.

First, clone the repository and follow the official Django [deployment checklist](https://docs.djangoproject.com/en/4.1/howto/deployment/checklist/) to prepare the website for serving.

Secondly, we recommend following [DigitalOcean's guide](https://www.digitalocean.com/community/tutorials/how-to-serve-django-applications-with-apache-and-mod_wsgi-on-ubuntu-16-04) for deployment details. Any missing details can be found in this [Django tutorial](https://docs.djangoproject.com/en/4.1/howto/deployment/wsgi/modwsgi/).

## Screenshots

![image](https://user-images.githubusercontent.com/44680063/215869894-d7b72e4d-fee0-4a56-8f8f-d0e6e0feba47.png)
![image](https://user-images.githubusercontent.com/44680063/215874375-fa9d33a2-9c36-4fbe-a807-3030e5168707.png)
![image](https://user-images.githubusercontent.com/44680063/215873283-33849439-5d4b-448d-a214-32bd9e1331c2.png)
![image](https://user-images.githubusercontent.com/44680063/215873004-772240e7-2311-4b53-9edd-708813fa5052.png)

