# TABLEAU API CONNECTION

## Poetry Run commands

The environment variables file (.env) needs to be created in the root folder
- You can ask for the environment variables values to the Data Team

If you don't have poetry installed already, you can run the following command

```shell
$ pip install poetry
```

Once you have poetry installed in your system, you can run the following commands
- Make sure that you have your own list of tables in the utils/tables_list.py

This will install the poetry dependencies listed in the pyproject.toml file and run the app afterwards

```shell
$ poetry install
$ poetry run python3 main.py
```
