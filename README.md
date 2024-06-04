# Python REST APIs with Flask, Connexion, and SQLAlchemy

> This application is made using the [Real Python REST APIs with Flask][rp-flask-api] tutorial.

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

> **REQUIRED**
>
> The versions MUST be included in the install so as to ensure functionality of the app in the context of this tutorial.

With the virtual environment activated, we can install **Flask**:

```shell
(api_env) $ pip install Flask==2.2.2
```

We can also install **[Connexion][connexion]** to handle the HTTP requests:

```shell
(api_env) $ pip install "connexion[swagger-ui]==2.14.1"
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

In `swagger.yml` we configured Connexion with the `operationId` value of `"people.read_all"`. When the API gets an HTTP request for `GET /api/people`, the Flask app calls a `read_all()` function within a `people` module.

In order for this to work, create a `people.py` file with a `read_all()` function:

```python3
# people.py

# get_timestamp defined
# ...

# PEOPLE dictionary defined
# ...

def read_all():
    return list(PEOPLE.values())
```

For now, we'll use the `PEOPLE` dictionary as sample data just to get the API working. It's a stand in for a proper databse. Its state *persists* between REST API calls. However, any data that you change will be lost when you restart the web application. This is not ideal for production, but is fine for now.

The `read_all()` function will serve the data when the server receives an HTTP request to `GET /api/people`.

Run the server and navigate the browser to `http://localhost:8000/api/people` to display the list of people on the screen.

We'll explore the API in the next section.

#### Explore Your API Documentation

We now have a single URL endpoint for our REST API. Flask knows what to serve based on based on the API specificication in `swagger.yml`. Additionally, Connexion uses `swagger.yml` to create API documentation at `/api/ui`. You can navigate to `http://localhost:8000/api/ui` to see the documentation in action.

If you click the `/people` endpoint in the interface, then the interface will expand to show more information about the API.

Any time the configuration file changes, the Swagger UI changes as well. You can even try the endpoint out by clicking the *Try it out* button. This can be extremely useful when the API grows. The Swagger UI API documentation gives you a way to explore and experiment with the API without having ot write any code to do so.

Using OpenAPI with Swagger offers a nice, clean way to create the API URL endpoints. Next, we can add additional endpoints to create, update, and delete people in the collection.

### Building Out the Complete API

Now it's time to provide full CRUD access to the `PEOPLE` structure.

Recall that the API definition looks like this:

| Action | HTTP Verb | URL Path              | Description                 |
| :----- | :-------- | :-------------------- | :-------------------------- |
| Read   | GET       | `/api/people`         | Read a collection of people |
| Create | POST      | `/api/people`         | Create a new person         |
| Read   | GET       | `/api/people/<lname>` | Read a particular person    |
| Update | PUT       | `/api/people/<lname>` | Update an existing person   |
| Delete | DELETE    | `/api/people/<lname>` | Delete an existing person   |

To add functionality, we extend both the `swagger.yml` and `people.py` files.

#### Work with Components

Before defining new API paths, we'll add a new block for **components**. Components are building blocks in the OpenAPI specification that you can reference from other parts of your specification.

Add a `components` block with `schemas` for a single person:

```yaml
# swagger.yml

openapi: 3.0.0
info:
  title: "Flask REST API"
  description: "An API about people and notes"
  version: "1.0.0"

servers:
  - url: "/api"

components:
  schemas:
    Person:
      type: "object"
      required:
        - lname
      properties:
        fname:
          type: "string"
        lname:
          type: "string"
# ...
```

A `components` block helps to avoid code duplication. For now, we save only the `Person` data model in the `schemas` block:

- `type` &mdash; The data type of the schema
- `required` &mdash; The required properties

The dash in front of `- lname` indicates that `required` can contain a list of properties. Any property that you define as `required` must also exist in `properties`, which includes the following:

- `fname` &mdash; The first name of a person
- `lname` &mdash; The last name of a person

The `type` key defines the value associated with its parent key. For `Person`, all properties are strings. This schema will be presented in Python as a dictionary.

#### Create a New Person

Extend your API endpoints by adding a new block for the `post` request in the `/people` block:

```yaml
# swagger.yml

# ...

paths:
  /people:
    get:
        # ...
    post:
      operationId: "people.create"
      tags:
        - People
      summary: "Create a person"
      requestBody:
          description: "Person to create"
          required: True
          content:
            application/json:
              schema:
                x-body-name: "person"
                $ref: "#/components/schemas/Person"
      responses:
        "201":
          description: "Successfully created person"
```

The structure for `post` looks similar to the existing `get` schema. One difference is that you also send a `requestBody` to the server, since you need to tell Flask the information that it needs to create a new person. Another difference is `operationId`, which is set to `people.create`.

Inside of `content`, you define `application/json` as the **data exchange format** of the API. Different media types can be served in the API requests and responses, but most modern APIs commonly use JSON as the data exchange format. This is useful since JSON objects are pretty much Python dictionaries:

```json
{
    "fname": "Tooth",
    "lname": "Fairy"
}
```

This JSON object represents the `Person` component defined in the `swagger.yml` file and is being referenced with `$ref` in `schema`.

We also use a `201` HTTP status code, which is a success response that indicates the creation of a new resource.

With `people.create`, we're telling the server to look for a `create()` function in the `people` module. So we add the function:

```python
from datetime import datetime
from flask import abort

# other definitions
# ...

def create(person):
    lname = person.get("lname")
    fname = person.get("fname", "")

    if lname and lname not in PEOPLE:
        PEOPLE[lname] = {
            "lname": lname,
            "fname": fname,
            "timestamp": get_timestamp(),
        }
        return PEOPLE[lname], 201
    else:
        abort(
            406,
            f"Person with last name {lname} already exists",
        )
```

Using Flask's `abort()` function helps you send an error message. The error response is raised when the request body doesn't contain a last name or when a person with this last name already exists.

> **NOTE**
>
> By design, a person's last name must be unique, since we're using `lname` as a dictionary key of `PEOPLE`. This means we can't have two people with the same last name in our project, for now.

If the data in the request body is valid, the `PEOPLE` dictionary is updated and the function responds with the new object with a `201` HTTP status code.

#### Handle a Person

Now let's update `swagger.yml` and `people.py` to work with a new path that handles a single existing person.

```yaml
# swagger.yml

# ...

components:
  schemas:
    # ...
  parameters:
    lname:
      name: "lname"
      description: "Last name of the person to get"
      in: path
      required: True
      schema:
        type: "string"

paths:
  /people:
    # ...
  /people/{lname}:
    get:
      operationId: "people.read_one"
      tags:
        - People
      summary: "Read one person"
      parameters:
        - $ref: "#/components/parameters/lname"
      responses:
        "200":
          description: "Successfully read person"
```

Similar to the `/people` path, we start with the `get` operation for `/people/{lname}`. The `{lname}` substring is a placeholder for the last name, which you have to pass in as a URL parameter.

> **NOTE**
>
> URL parameters are case sensitive. So last names like *Ruprecht* and *ruprecht* will be treated as unique and will return an error if neither one exists.

We'll use the `lname` parameter in other operations, too. So it makes sense to create a component for it and reference it where needed.

Since `operationId` points to a `read_one()` function, we impliment it in `people.py`:

```python
# people.py

# ...

def read_one(lname):
    if lname in PEOPLE:
        return PEOPLE[lname]
    else:
        abort(
            404, f"Person with last name {lname} not found"
        )
```

Flask will return the data for a particular person with the provided last name in `PEOPLE`, otherwise the server will return a `404` HTTP error.

To update an existing person, we add a `put` operation to the `swagger.yml` file:

```yaml
# swagger.yml

# ...

paths:
  /people:
    # ...
  /people/{lname}:
    get:
        # ...
    put:
      tags:
        - People
      operationId: "people.update"
      summary: "Update a person"
      parameters:
        - $ref: "#/components/parameters/lname"
      responses:
        "200":
          description: "Successfully updated person"
      requestBody:
        content:
          application/json:
            schema:
              x-body-name: "person"
              $ref: "#/components/schemas/Person"
```

And since we have `people.update` as the `operationId`, we implement the `update()` function in `people.py`:

```python
# people.py

# ...

def update(lname, person):
    if lname in PEOPLE:
        PEOPLE[lname]["fname"] = person.get("fname", PEOPLE[lname]["fname"])
        PEOPLE[lname]["timestamp"] = get_timestamp()
        return PEOPLE[lname]
    else:
        abort(
            404,
            f"Person with last name {lname} not found"
        )
```

The `update()` function expects two arguments:

- `lname` &mdash; The last name of the person
- `person` &mdash; The data to update the person with

When a person with the provided last name exists, the `PEOPLE` dictionary's corresponding values will be updated with the `person` data.

To remove a person from the dataset, we add a `delete` operation:

```yaml
# swagger.yml

# ...

paths:
  /people:
    # ...
  /people/{lname}:
    get:
        # ...
    put:
        # ...
    delete:
      tags:
        - People
      operationId: "people.delete"
      summary: "Delete a person"
      parameters:
        - $ref: "#/components/parameters/lname"
      responses:
        "204":
          description: "Successfully deleted person"
```

Then add the corresponding `delete()` function to `people.py`:

```python
# people.py

from flask import abort, make_response

# ...

def delete(lname):
    if lname in PEOPLE:
        del PEOPLE[lname]
        return make_response(
            f"{lname} successfully deleted", 200
        )
    else:
        abort(
            404,
            f"Person with last name {lname} not found"
        )
```

If the person you want to delete exists in the dataset, then we remove it from `PEOPLE`.

Great! Both `people.py` and `swagger.yml` are complete. With all the endpoints to manage people in place, we can try out our API. Since we used Connexion to connect Flask to Swagger, the API documentation is ready as well!

Because we have a static dictionary to hold our people information, the changes we make won't persist whenever we restart the Flask application. That's why we'll implement a proper database for the project in the next part.

### Conclusion of Part 1

In **Part 1** we created a comprehensive REST API with Flask. With Connexion, and some additional configuration, we were able to provide useful documentation and an interactive system. This makes building a REST API an enjoyable experience.

In **[Part 2](#part-2--database-persistence)**, we'll learn how to use a proper databsae to store and persist data, instead of relying on in-memory storage as was done with the `PEOPLE` dictionary.

## Part 2 &mdash; Database Persistence

We've created a basic Flask application with some endpoints as the foundation for our REST API. We can now connect it to a database to persist existing data and any changes we make to the collection.

### Planning

In **[Part 1](#part-1--foundation)** we worked with a `PEOPLE` dictionary to store our data. This data structure was handy to get the project up and running. However, any data that was added was lost when the app restarted. In this part, we'll be translating the `PEOPLE` dictionary into a databsae table that'll look like this:

| id | lname    | fname  | timestamp           |
| :- | :------- | :----- | :------------------ |
| 1  | Fairy    | Tooth  | 2022-10-08 09:15:10 |
| 2  | Ruprecht | Knecht | 2022-10-08 09:15:13 |
| 3  | Bunny    | Easter | 2022-10-08 09:15:27 |

This won't require any changes to the REST API endpoints, but the changes made to the backend will be significant and will result in a much more versatile codebase to help scal the Flask project up in the future.

### Setup

To convert complex data types to and from Python data types, you'll need a **serializer**. For this tutorial, we use [Flask-Marshmallow][flask-marshmallow].

#### Add New Dependencies

> **UPDATE**
>
> Due to version conflicts as of the time the tutorial was written and since Python has been updated, the installed versions and formats have been changed.

> **REQUIRED**
>
> The versions MUST be included in the install so as to ensure functionality of the app in the context of this tutorial.

Be sure to activate the virtual environment before installing new packages.

With the virtual environment activated, install `flask-marshmallow` with the `sqlalchemy` option:

```shell
(api_env) $ pip install "flask-marshmallow==0.14.0"
```

```shell
(api_env) $ pip install sqlalchemy
```

Flask-Marshmallow also install `marshmallow`, which provides functionality to serialize and deserialize Python objects as they flow in and out of your REST API, which is based on JSON. Marshmallow converts Python class instances to objects that can be converted to JSON.

Installing `sqlalchemy` will help to leverage the powers of the [SQLAlchemy][sqlalchemy] ORM, which stores each Python object to a database representation of the object's data. This can help continue to think in a Pythonic way and not be concerned with how the object data will be represented in the database.

#### Check That Everything Still Works

After the installs, we need to verify that everything still works as expected:

```shell
(api_env) $ python3 app.py
```

After running the app, and navigating your browser to `http://localhost:8000/`, you should see a *"Hello, World!"* statement displayed. Also, your Swagger documentation should still be displayed and functional.

Since the app is still functional, it's time to update the backend with a proper database.

### Initializing the Database

Currently, we're storing the data of our Flask project in a dictionary. Storing data like this isn't persistent, any changes get lost when we restart the Flask app. On top of that, the structure of the dictionary isn't ideal.

The modifications we'll make will move all the data to a database table. This means the data will be saved to our local machine's disk and will exist between runs of the `app.py` program.

#### Conceptualize Your Database Table

Database tables usually have an auto-incrementing integer value as a primary key, whose value is unique across the entire table and is used as a lookup key to each row. Having a primary key independent of the data stored in the table gives you the freedom to modify any other field in the row.

We're going to follow a database convention of naming the table as singular, so the table will be called `person`.

With this concept in place, it's time to build the table.

#### Build Your Database

We're going to use SQLite as the database engine to store the `PEOPLE` data. [SQLite][sqlite] is a widely used relational database management system (RDBMS) that doesn't need a SQL server to work.

In contrast to other SQL database engines, SQLite works with a single file to maintain all the database functionality. Therefore, to use the database, a program just needs to know how to read and write to a SQLite file.

Python's built-in `sqlite3` module allows you to interact with SQLite databases without any external packages. This makes SQLite particularly useful when starting new Python projects.

In a Python interactive shell (i.e. running `python3` in a Terminal window), create the `people.db` SQLite database:

```shell
>>> import sqlite3
>>> conn = sqlite3.connect("people.db")
>>> columns = [
...     "id INTEGER PRIMARY KEY",
...     "lname VARCHAR UNIQUE",
...     "fname VARCHAR",
...     "timestamp DATETIME",
... ]
>>> create_table_cmd = f"CREATE TABLE person ({','.join(columns)})"
>>> conn.execute(create_table_cmd)
<sqlite3.Cursor object at 0x1063f4dc0>
```

After running `sqlite3.connect("people.db")`, you'll see that Python added a `people.db` database file to your file system.

With `conn.execute()`, you're running a SQL command to create a `person` table with the columns `id`, `lname`, `fname`, and `timestamp`.

Now that the database and table exist, you can add data to it:

```shell
>>> import sqlite3
>>> conn = sqlite3.connect("people.db")
>>> people = [
...     "1, 'Fairy', 'Tooth', '2022-10-08 09:15:10'",
...     "2, 'Ruprecht', 'Knecht', '2022-10-08 09:15:13'",
...     "3, 'Bunny', 'Easter', '2022-10-08 09:15:27'",
... ]
>>> for person_data in people:
...     insert_cmd = f"INSERT INTO person VALUES ({person_data})"
...     conn.execute(insert_cmd)
...
<sqlite3.Cursor object at 0x104ac4dc0>
<sqlite3.Cursor object at 0x104ac4f40>
<sqlite3.Cursor object at 0x104ac4fc0>

>>> conn.commit()
```

Once connected to the `people.db`, you declare a transaction to insert `people_data` into the `person` table. The `conn.execute()` command creates `sqlite3.Cursor` objects in memory. Only when you run `conn.commit()` do you make the transactions happen.

#### Interact with the Database

Unlike programming languages, SQL doesn't define *how* to get the data. SQL describes *what* data is desired and leaves the how up to the database engine.

In the following Python code, you use SQLite to run a query that displays all the data from the `person` table:

```shell
>>> import sqlite3
>>> conn = sqlite3.connect("people.db")
>>> cur = conn.cursor()
>>> cur.execute("SELECT * FROM person")
<sqlite3.Cursor object at 0x102357a40>

>>> people = cur.fetchall()
>>> for person in people:
...     print(person)
...
(1, 'Fairy', 'Tooth', '2022-10-08 09:15:10')
(2, 'Ruprecht', 'Knecht', '2022-10-08 09:15:13')
(3, 'Bunny', 'Easter', '2022-10-08 09:15:27')
```

In the above code, the SQL statement is a string passed directly to the database to execute. In this case, it isn't a big problem because the SQL is a string literal completely under the control of the program. However, the use case for our REST API will be taking user input from the web application and using it to create SQL queries. This can open our application to attacks.

> **Bobby Tables: A Cautionary Tale**
>
> 

[connexion]: https://connexion.readthedocs.io/en/latest/index.html
[flask-marshmallow]: https://flask-marshmallow.readthedocs.io/en/latest/
[openapi]: https://www.openapis.org/
[rp-flask-api]: https://realpython.com/flask-connexion-rest-api/
[sqlalchemy]: https://realpython.com/python-sqlite-sqlalchemy/
[sqlite]: https://www.sqlite.org/index.html
[swagger]: https://swagger.io/tools/swagger-ui/


