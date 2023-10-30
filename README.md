# Page analyzer
[![Actions Status](https://github.com/Vadimhungry/python-project-83/actions/workflows/hexlet-check.yml/badge.svg)](https://github.com/Vadimhungry/python-project-83/actions)[![Maintainability](https://api.codeclimate.com/v1/badges/ee3b93ed4c4eec53bfc5/maintainability)](https://codeclimate.com/github/Vadimhungry/python-project-83/maintainability)

This is a web application. 
On the [main page](https://page-ceo-analyzer.onrender.com/) you can enter the website url and click "ПРОВЕРИТЬ". If url is correct you will see url's page with table of checks. Here click "Запустить проверку". Site will be checked and you will see the results in the table.

For deploy of application rename `.env.sample` file to `.env` in root directory. 
Then change values for `SECRET_KEY` and `DATABASE_URL`. You should insert your own values.  

For security reasons we recommend to use keys generator for creating the `SECRET_KEY` value.
For database connection set the value of `DATABASE_URL` in form `{provider}://{user}:{password}@{host}:{port}/{db}`

### Disclaimer
This is a pet project. 
During the work on it I had pleasure to practice such a grate stuff as Flask, Jinja, PostgreSQL, Gunicorn and BeautifulSoup. Service and its database are hosted on [https://render.com/](https://render.com/).
Feel free to try app on page 
[https://page-ceo-analyzer.onrender.com/](https://page-ceo-analyzer.onrender.com/). 