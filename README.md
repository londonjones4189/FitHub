# FitHub: A Sustainable Clothing Trading Platform
# A CS 3200 Group Project Fall 2025 

FitHub is a digital clothing exchange platform designed to help people refresh their wardrobes sustainably. Instead of buying new clothes or engaging in bidding wars on platforms like Depop or Ebay, FitHub allows users to swap, take, or donate items based on personalized style and profiles. FitHub’s Flask REST API and Streamlit UI work together to support finding your dream wardrobe through analytical recommendations.

The platform serves two main user groups:

Swappers

Users who want to exchange clothing items they no longer use. They can post items, tag them as “swap” or “take,” and accept or reject match suggestions based on their preferences.

Takers / Donators

Users who want to take items for free or find places to donate clothing. These users can browse items without bidding or fees.

FitHub supports smart listings, personalized match suggestions, swap/task progression, user communication, and admin moderation tools.


## Structure of the Repo

app/: 

Location of the Streamlit frontend.
Contains all user interface code, page layouts, and the main Home.py entry page inside app/src/

api/ :
The Flask REST API backend: 
Includes all server logic, business logic, and communication with the MySQL database.

database-files/ :

Contains SQL files that automatically initialize the MySQL database when the container is first created.

fithub.sql – Full schema and seed data for FitHub.

docker-compose.yml

Defines and runs all three containers: MySQL database, Flask backend API. Streamlit frontend

## Prerequisites

Before running the project:

A GitHub account

Git installed (CLI or GitHub Desktop)

Docker Desktop installed and running

A code editor 

Python 3.11 if you want to run the backend/frontend without Docker

##  Instructions 

How to Run the Project (Using Docker)

Follow these steps to run a fresh version of FitHub on your machine.

1. Pull the Latest Version of the Project

In a terminal:

git checkout main
git pull
Start All Containers
Terminal 
docker compose up --build


This will build and start:

Service	Description	URL(go to the front end link to test):
web-app	Streamlit frontend	http://localhost:8501/

web-api	Flask REST API backend	http://localhost:4000/

mysql_db	MySQL 8+ Database	localhost:3306 (mapped 3200)


Stop your containers: docker compose down
