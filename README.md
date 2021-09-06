# pokedex
A Pokeman based REST API written in Python using the Flask Restful framework.

## How to run manually?

### Setup your environment

You need to make sure your system has the following tools installed:
- Python 3.6.9 (tested on this version) or newer
- Python 3 Virtual Environments
- PIP 3 Package Manager

To verify/install on Debian Linux:
- `sudo apt-get install python3`
- `sudo apt-get install python3-pip`
- `sudo apt-get install python3-venv`

### Create your environment_variables file

Next duplicate the `environment_variables.example` file and rename the new file as just `environment_variables`, you don't need to modify the contents currently.

### Run the development server

Finally, you can run the developmeny server by running the shell script `./run-development-server.sh`.

### Run the unit tests

You can also run the unit tests by using `./runtests.sh`, this first runs a Flake8 linting test and then proceeds to run all the unit tests.

## How to run with Docker?

Coming soon...


## How would this be improved for a production release?
- Use a more secure and advanced framework like Django REST.
- Add some kind of authentication such as OAuth2 (built into Django) or even front it with a seperate authentication layer, such as using Kong API.
- Would write seperate integration tests that are capable of hitting test API instances, so that the unit tests can actually hit the servers without having to rely solely on mocked responses.
- Use the Python logging module to add logging throughout the API.
- Would create a third parent abstract class called ApiWrapper that both the FunTranslationAPIWrapper and PokeAPIWrapper classes inherit from to remove duplication.
- Would not be developing on main / master branch.
