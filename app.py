import connexion

from flask import render_template

# Use connexion instead to create the app so that it can read in the
# swagger.yml file
app = connexion.App(__name__, specification_dir="./")
app.add_api("swagger.yml")


@app.route("/")
def home():
    return render_template("home.html")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
