# Page analyzer
[![Actions Status](https://github.com/Vadimhungry/python-project-83/actions/workflows/hexlet-check.yml/badge.svg)](https://github.com/Vadimhungry/python-project-83/actions)[![Maintainability](https://api.codeclimate.com/v1/badges/ee3b93ed4c4eec53bfc5/maintainability)](https://codeclimate.com/github/Vadimhungry/python-project-83/maintainability)

This is a web application. 
On the [main page](https://page-ceo-analyzer.onrender.com/) you can enter the website url and click "ПРОВЕРИТЬ". If url is correct you will see url's page with table of checks. Here click "Запустить проверку". Site will be checked and you will see the results in the table.

For deploy of application you have to create .env file in root directory.
In the .env file should be two variables, SECRET_KEY and DATABASE_URL.
For security reasons we recommend to use keys generator for creating the key.
For database connection set the value of DATABASE_URL in form `{provider}://{user}:{password}@{host}:{port}/{db}`

[https://page-ceo-analyzer.onrender.com/home](https://page-ceo-analyzer.onrender.com/home)