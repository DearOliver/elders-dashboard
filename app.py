from flask import Flask, render_template, request, redirect, url_for, session, flash
from sqlalchemy import event
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)

app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://ucqnhvk6u5rvsr:p90d1e1fcd767495447f50c9db8447f74bed656c9882c6dc3d1de7cb392ace2ca@cdgn4ufq38ipd0.cluster-czz5s0kz4scl.eu-west-1.rds.amazonaws.com:5432/d50i6d64k7h43f'
db = SQLAlchemy(app)
port = int(os.environ.get("PORT", 6969))

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(50), nullable=False)
    matricule = db.Column(db.Integer, nullable=False)
    patrol_id = db.Column(db.Integer, db.ForeignKey('patrol.id'))
    role = db.Column(db.String(50), nullable=False)
    name = db.Column(db.String(200))

class Patrol(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    intervention_id = db.Column(db.Integer, db.ForeignKey('intervention.id'))
    users = db.relationship('User', backref='patrol')

class Intervention(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    patrols = db.relationship('Patrol', backref='intervention')

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/test")
def test():
    return render_template("test.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        user = User.query.filter_by(username=username).first()
        
        if user and (user.password == password) :
            session["user_id"] = user.id
            session["username"] = user.username
            session["matricule"] = user.matricule
            session["role"] = user.role

            return redirect(url_for("home"))
        else:
            return render_template("login.html", error="Nom d'utilisateur ou mot de passe incorrect")

    return render_template("login.html")

@app.route("/home")
def home():
    if "user_id" in session:
        role = session.get("role")
        matricule = session.get("matricule")
        patrols = Patrol.query.all()
        interventions = Intervention.query.all()
        users_waiting = User.query.filter_by(patrol_id=0)
        return render_template("home.html", matricule=matricule, patrols=patrols, users_waiting=users_waiting, role=role, interventions=interventions)
    else:
        return redirect(url_for("login"))
    
@app.route("/create_patrol/<int:user_id>")
def create_patrol(user_id):
    new_patrol = Patrol(intervention_id=0)

    db.session.add(new_patrol)
    db.session.commit()

    new_patrol_id = new_patrol.id

    user = User.query.get(user_id)
    user.patrol_id = new_patrol_id
    db.session.commit()

    patrols = Patrol.query.all()
    for patrol in patrols :
        if User.query.filter_by(patrol_id=patrol.id).count() == 0 :
            Patrol.query.filter_by(id=patrol.id).delete()

    return redirect(url_for("home"))

@app.route("/create_intervention", methods=["POST"])
def create_intervention():
    intervention_name = request.form["interventionName"]

    new_intervention = Intervention(name=intervention_name)

    db.session.add(new_intervention)
    db.session.commit()

    return redirect(url_for("home"))

@app.route("/delete_intervention/<int:intervention_id>")
def delete_intervention(intervention_id):
    if "user_id" in session:
        user_id = session["user_id"]

        patrols_in_intervention = Patrol.query.filter_by(intervention_id=intervention_id)
        
        for patrol in patrols_in_intervention :
            users_in_patrol = User.query.filter_by(patrol_id=patrol.id)
            for user in users_in_patrol :
                user.patrol_id = 0
                db.session.commit()
            
            Patrol.query.filter_by(id=patrol.id).delete()

        Intervention.query.filter_by(id=intervention_id).delete()

        return redirect(url_for("home"))
    else:
        return redirect(url_for("login"))
    
@app.route("/join_intervention/<int:intervention_id>")
def join_intervention(intervention_id):
    if "user_id" in session:
        new_patrol = Patrol(intervention_id=intervention_id)

        db.session.add(new_patrol)
        db.session.commit()

        new_patrol_id = new_patrol.id

        user_id = session.get("user_id")
        user = User.query.get(user_id)
        user.patrol_id = new_patrol_id
        db.session.commit()

        patrols = Patrol.query.all()
        for patrol in patrols :
            if User.query.filter_by(patrol_id=patrol.id).count() == 0 :
                Patrol.query.filter_by(id=patrol.id).delete()

        return redirect(url_for("home"))
    else:
        return redirect(url_for("login"))

@app.route("/drop_patrol/<int:user_id>/<int:patrol_id>")
def drop_patrol(user_id, patrol_id):
    user = User.query.get(user_id)
    user.patrol_id = patrol_id
    db.session.commit()

    patrols = Patrol.query.all()
    for patrol in patrols :
        if User.query.filter_by(patrol_id=patrol.id).count() == 0 :
            Patrol.query.filter_by(id=patrol.id).delete()

    return redirect(url_for("home"))

@app.route("/join_patrol/<int:patrol_id>")
def join_patrol(patrol_id):
    if "user_id" in session:
        user_id = session["user_id"]

        user = User.query.get(user_id)
        user.patrol_id = patrol_id
        db.session.commit()

        patrols = Patrol.query.all()
        for patrol in patrols :
            if User.query.filter_by(patrol_id=patrol.id).count() == 0 :
                Patrol.query.filter_by(id=patrol.id).delete()

        return redirect(url_for("home"))
    else:
        return redirect(url_for("login"))
    
@app.route("/drop_intervention/<int:user_id>/<int:intervention_id>")
def drop_intervention(user_id, intervention_id):
    print("TEST ", intervention_id)
    new_patrol = Patrol(intervention_id=intervention_id)

    db.session.add(new_patrol)
    db.session.commit()

    new_patrol_id = new_patrol.id

    user = User.query.get(user_id)
    user.patrol_id = new_patrol_id
    db.session.commit()

    patrols = Patrol.query.all()
    for patrol in patrols :
        if User.query.filter_by(patrol_id=patrol.id).count() == 0 :
            Patrol.query.filter_by(id=patrol.id).delete()

    return redirect(url_for("home"))

if __name__ == "__main__" :
    app.run(debug = True, port = port)