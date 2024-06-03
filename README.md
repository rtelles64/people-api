# Python REST APIs with Flask, Connexion, and SQLAlchemy

## Part 1 &mdash; Foundation

In the first part of this tutorial, we create a base Flask project which will plug into our API endpoints. We'll also leverage Swagger UI to create documentation for the API. This will enable us to test the API at each stage and get a useful overview of all endpoints.

### Planning

This REST API will provide access to a collection of people and to the individuals within that collection.

Here's the overall design:

| Action | HTTP Verb | URL Path              | Description                 |
| :----- | :-------- | :-------------------- | :-------------------------- |
| Read   | GET       | `/api/people`         | Read a collection of people |
| Create | POST      | `/api/people`         | Create a new person         |
| Read   | GET       | `/api/people/<lname>` | Read a particular person    |
| Update | PUT       | `/api/people/<lname>` | Update an existing person   |
| Delete | DELETE    | `/api/people/<lname>` | Delete an existing person   |

The dataset we'll be working with will look like this:

```python
PEOPLE = {
    "Fairy": {
        "fname": "Tooth",
        "lname": "Fairy",
        "timestamp": "2022-10-08 09:15:10",
    },
    "Ruprecht": {
        "fname": "Knecht",
        "lname": "Ruprecht",
        "timestamp": "2022-10-08 09:15:13",
    },
    "Bunny": {
        "fname": "Easter",
        "lname": "Bunny",
        "timestamp": "2022-10-08 09:15:27",
    }
}
```

One purpose of an API is to decouple the data from the application that uses it, thereby hiding any data implementation details.

### Setup

####  Create and Activate Virtual Environment

It's always a good idea to create and activate a virtual environment. That way we install any project dependencies within the project itself, and not on your local machine.

```shell
$ python3 -m venv api_env
$ source api_env/bin/activate
(api_env) $
```

With the commands above, we create a virtual and activate a virtual environment called `api_env` which uses Python 3. The parenthesized `(api_env)` indicates that you've successfully activated the virtual environment.

#### Add Dependencies

With the virtual environment activated, we can install **Flask**:

```shell
(api_env) $ pip install Flask
```

We can also install **[Connexion][connexion]** to handle the HTTP requests:

```shell
(api_env) $ pip install "connexion[swagger-ui]"
```

- This command installs Connexion with the added support for [Swagger UI][swagger].

#### Initiate Flask Project

The main file of the Flask project will be `app.py` in the root directory:

```python
# app.py

from flask import Flask, render_template

app = Flask(__name__)


@app.route("/")
def home():
    return render_template("home.html")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
```

- The `app.py` does some important things:
  1. Imports the `Flask` module, giving the application access to Flask functionality.
  2. Creates a Flask application instance named `app`.
  3. Connects the URL route **"/"** to the `home()` function using the decorator `@app.route("/")`.
  4. `home()` renders the `home.html` file in the browser using the `render_template()` function.
  5. Runs the web server with `app.run()`.

In short, the code in `app.py` gets a basic web server up and running and makes it respond with a `home.html` template, which is served to a browser when navigating to the **"/"** URL.

In order for Flask to render `home.html` properly, it expects it in a template directory named `templates/`. Create the directory and add the file:

```html
<!-- templates/home.html -->

<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>RP Flask REST API</title>
</head>
<body>
    <h1>
        Hello, World!
    </h1>
</body>
</html>
```

The purpose of this basic HTML file is to verify that the Flask project responds as intended.

With the Python virtual environment activate, run the application with this command while in the directory containing the `app.py` file:

```shell
(api_env) $ python3 app.py
```

When you run `app.py`, a web server will start on port `8000`. You can navigate to `http://localhost:8000` and should see _Hello, World!_ displayed!

Congratulations! You have a web server running that hosts the current version of your REST API.

By now, the Flask project structure should look like this:

```shell
.
│
├── templates/
│   └── home.html
│
└── app.py
```

This is a great starting structure for any Flask project. Next, we'll expand the project and add the first REST API endpoint.

### Adding Your First REST API Endpoint

Now that we have a working web server, we can add the first REST API endpoint.

The Connexion module allows Python to use the [OpenAPI][openapi] specification with Swagger. The **OpenAPI** Specification is an API description format for REST APIs and provides a lot of functionality, including:

- Validation of input and output data to and from your API
- Configuration of the API URL endpoints and the expected parameters

When you use OpenAPI with Swagger, you can create a UI to explore the API. All of this can ahppen when you create a configuration file that your Flask application can access.

#### Create the API Configuration File

The Swagger configuration file is a YAML or JSON file containing your OpenAPI definitions. This file contains all the necessary information to configur your server to provide input parameter validation, output response data validation, and URL endpoint definition.

```yaml
# swagger.yml

openapi: 3.0.0
info:
  title: "Flask REST API"
  description: "An API about people and notes"
  version: "1.0.0"
```

When you define an API, you must include the version of your OpenAPI definition, which is indicated by the `openapi` keyword. The version is important because some parts of the OpenAPI structure may change over time.

The `info` keyword begins the scope of the API information block:

- `title` &mdash; Title included in the Connexion-generated UI system
- `description` &mdash; Description of what the API provides or is about
- `version` &mdash; Version value for the API

Next, add `servers` and the `url`, which define the root path of your API:

```yaml
# swagger.yml

# info definition
# ...

servers:
  - url: "/api"
```

By providing `"/api"` as the value of `url`, you'll be able to access all of your API paths relative to `http://localhost:8000/api`.

We then define the API endpoints in a `paths` block:

```yaml
# swagger.yml

# info definition
# ...

# servers definition
# ...

paths:
  /people:
    get:
      operationId: "people.read_all"
      tags:
        - "People"
      summary: "Read the list of people"
      responses:
        "200":
          description: "Successfully read people list"
```

The `paths` block begins the configuration of the API URL endpoint paths:

- `/people` &mdash; The relative URL of your API endpoint
- `get` &mdash; The HTTP method that this URL endpoint will respond to

Together with the `url` definition in `servers`, this creates the `GET /api/people` URL endpoint that you can access at `http://localhost:8000/api/people`.

The `get` block begins the configuration of the single `/api/people` URL endpoint:

- `operationId` &mdash; The python function that'll respond to the request
  - This must contain a string.
  - Connexion will use `"people.read_all"` to find a Python function named `read_all()` in a `people` module of your project, which will be created later.

- `tags` &mdash; The tags assigned to this endpoint, which allow you to group the operations in the UI

- `summary` &mdash; The UI display text for this endpoint

- `responses` &mdash; The status codes that the endpoint responds with
  - This block defines the configuration of the possible status codes.
  - We define a successful response for the status code `"200"`, containing some `description` text.

The `swagger.yml` file is like a blueprint for your API. With the specifications included in `swagger.yml`, you define what data your web server can expect and how your server should respond to requests.

So far, your Flask project doesn't know about your `swagger.yml` file. We'll connect it to the Flask app next.

#### Add Connexion to the App

There are two steps to adding a REST API URL endpoint to your Flask application with Connexion:

1. Add an API configuration file eto your project (this is the `swagger.yml` file)
2. Connect your Flask app with the configuration file.

To connect the API configuration file with the Flask app, we have to reference `swagger.yml` in the `app.py` file:

```python
# app.py

from flask import render_template # Remove: import Flask
import connexion

app = connexion.App(__name__, specification_dir="./")
app.add_api("swagger.yml")

@app.route("/")
def home():
    return render_template("home.html")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
```

The application instance uses Connexion rather than Flask to connect to the `swagger.yml` file. Internally, the Flask app is still created, but it now has additional functionality added to it.

The *specification_dir* parameter of the `connexion.App()` function tells Connexion which directory to look in for its configuration file. We then tell the app instance to read the `swagger.yml` file from the specification directory and configure the system to provide the Connexion functionality.

#### Return Data From Your People Endpoint



[connexion]: https://connexion.readthedocs.io/en/latest/index.html
[openapi]: https://www.openapis.org/
[swagger]: https://swagger.io/tools/swagger-ui/
[rp-flask-api]: https://realpython.com/flask-connexion-rest-api/
