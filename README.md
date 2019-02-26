# Blood-Bank

You need to have [Flask](http://flask.pocoo.org/docs/0.12/installation/), at least [python 2.6 installed](https://www.python.org/downloads/windows/), and [pip and virtual environment for windows](http://timmyreilly.azurewebsites.net/python-pip-virtualenv-installation-on-windows/), or [pip and virtual environment for mac/linux](http://flask.pocoo.org/docs/0.12/installation/), setup to run the project.

Once setup everything is setup, navigate to the project's root folder and create a virtual environment. Then, run the following command to allow source code editing without needing to reinstall the Flask app:

```
pip install --editable .
```

### Windows Setup

To set the environment, type the following:

```
set FLASK_APP=flaskr
set FLASK_DEBUG=true
```

You need to initialize the database before running the application:
```
flask initdb
```

Finally, run the application:
```
flask run
```

### Mac/Linux Setup

To set the environment, type the following:

```
export FLASK_APP=flaskr
export FLASK_DEBUG=true
```

You need to initialize the database before running the application:
```
flask initdb
```

Finally, run the application:
```
flask run
```

### After setup

Once you're done working on the environment, you can get with the command:
```
deactivate
```

## Note:

To open the project again, simply follow the setup for your appropriate OS. YOU MUST NOT PUT ANY SPACES NEXT TO THE '=' OPERAND, doing so will not properly setup the environment.
# Blood_Bank
