
from flask import Flask, render_template, request, make_response, session,escape,redirect,url_for,flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import  Table, Column, Integer, ForeignKey
from sqlalchemy.orm import relationship, backref
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.sql import text
from flask_marshmallow import Marshmallow

import requests
import sqlite3
from flask import jsonify
import os

dbdir = "sqlite:///" + os.path.abspath(os.getcwd()) + "/database.db"


app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = dbdir
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)


#ESTO FUNCIONAAAAA!!!!!
#association_table = db.Table('association',
#                          db.Column('users_id',Integer,ForeignKey('users.codigo')),
#                          db.Column('grupos_id',Integer,ForeignKey('grupos.codigo')))



class Association(db.Model):
    __tablename__ = 'association'
    users_id = db.Column(db.Integer,ForeignKey('users.codigo'),primary_key=True)
    grupos_id = db.Column(db.Integer, ForeignKey('grupos.codigo'),primary_key=True)
    extra_data = db.Column(db.String(80))
    user1 = relationship("Users",back_populates = "grupo")
    grupo1 = relationship("Grupos", back_populates = "user")
    

#----- Tablas para la base de datos -----
class Users(db.Model):
    __tablename__ = 'users'
    codigo = db.Column(db.String(9), primary_key = True)
    username = db.Column(db.String(50),nullable =True)
    password = db.Column(db.String(80),nullable =True)
    carerra = db.Column(db.String(80),nullable =True)
    semestre = db.Column(db.String(80),nullable =True)
    tutor = db.Column(db.String(2),nullable =True)
    #Esto funcionaaaaa
    #grupos = db.relationship("Grupos",secondary=association_table)




    grupo = relationship("Association",back_populates = "user1")

    def __str__(self):
        return str("La persona c:" + str(self.codigo) + ", nombre: " + str(self.username) + 
        ", grupos: " + str(self.grupo))

class Grupos(db.Model):
    __tablename__ = 'grupos'
    codigo = db.Column(db.Integer, primary_key = True)
    materia = db.Column(db.String(50),nullable =True)
    lugar = db.Column(db.String(80),nullable =True)
    dia = db.Column(db.String(80),nullable =True)
    tutor = db.Column(db.String(80),nullable =True)
    #Esto funcionaaaaa
    #userss = db.relationship("Users",secondary=association_table)



    user = relationship("Association",back_populates = "grupo1")

    def __str__(self):
        return str("El grupo c:" + str(self.codigo) + ", materia: " + str(self.materia) + 
        ", users: " + str(self.userss))



#----- Entrar en cursos -----
@app.route("/entrarCursos",methods=["GET","POST"])
def entrar_Cursos():
    if request.method == "GET":
        Grupos.user = Users
        db.session.commit()
        return redirect("/cursos")
    elif request.method == "POST":
        flash("Te has unido al curso!.")
        print("Entrando por el POST")
        print(request.form['id'])
        #ESTO FUNCIONAA, GUARDA EN LA BASE DE DATOS!!
        #s = Grupos.query.filter_by(codigo=request.form['id']).first()
        #c = Users.query.filter_by(codigo=session["codigo"]).first()
        #c.grupos.append(s)
        #db.session.add(c)
        #db.session.commit()

        g = Grupos()
        a = Association(extra_data = "Dios")
        a.user1 = Users()
        g.user.append(a)

        for i in g.user:
            print(i.extra_data)
            print(i.user1)

        
        return '200'


#----- Registro del estudiante -----
@app.route("/signup/estudiante",methods=["GET","POST"])
def signup():
    if request.method == "POST":
        hashed_pw=generate_password_hash(request.form["password"],method="sha256")
        new_user = Users(codigo=request.form["codigo"] ,username=request.form["username"],password=hashed_pw,carerra=request.form["carerra"],semestre=request.form["semestre"],tutor=request.form["tutor"])
        db.session.add(new_user)
        db.session.commit()
        flash("Te has registrado exitosamente!.")
        return redirect("/login")
    return render_template("signup.html")

#----- Logearse -----
@app.route("/login",methods=["GET","POST"])
def login():
    if request.method == "POST":
        user = Users.query.filter_by(codigo=request.form["codigo"]).first()
        if user and check_password_hash( user.password, request.form["password"]):
            session["codigo"] = user.codigo
            print(session["codigo"])
            session["username"] = user.username
            session["tutor"] = user.tutor
            return redirect("/cursos")
        flash("Tus datos son incorrectos o no te has registrado, intentalo de nuevo.")
    return render_template("login.html")

#----- Crear un curso -----
@app.route("/signup/curso",methods=["GET","POST"])
def signup_curso():
    if request.method == "POST":
        if session["codigo"] != "debes iniciar sección en 'Login'":
            if session["tutor"] == "Si":
                new_curso = Grupos(materia=request.form["materia"],lugar=request.form["lugar"],dia=request.form["dia"],tutor=session["username"])
                db.session.add(new_curso)
                db.session.commit()
                return redirect("/cursos")    
            else:
                flash("No eres tutor, por ende no puedes crear grupos de estudio")
        else:
            flash("Debes loguearte primero")
    return render_template("signup_curso.html")


#----- Ingresar a pagina de cursos -----
@app.route("/cursos", methods=['GET','POST'])
def cursos():
    g = Grupos.query.all()
    grupos = []
    for item in g:
        grupos.append({"codigo": item.codigo,"lugar" : item.lugar ,"materia": item.materia, "tutor" : item.tutor})

    return render_template('cursos.html', g = grupos)

#----- Ingresar a pagina de tutores -----
@app.route("/tutores", methods=['GET','POST'])
def tutores():
    g = Users.query.all()
    usuarios = []
    for item in g:
        usuarios.append({"codigo": item.codigo,"username" : item.username ,"carrera": item.carerra,"tutor":item.tutor})
    return render_template('tutor.html',g = usuarios)

#----- Volver a inicio -----
@app.route("/volverInicio",methods=["GET","POST"])
def volverInicio():
    if request.method == "POST":
        return redirect("/")

#----- Volver a grupos -----
@app.route("/volverGrupos",methods=["GET","POST"])
def volverGrupos():
    if request.method == "POST":
        return redirect("/cursos")

#----- Volver a login -----
@app.route("/volverLogin",methods=["GET","POST"])
def volverLogin():
    if request.method == "POST":
        return redirect("/login")

#----- Volver a tutores -----
@app.route("/verTutores",methods=["GET","POST"])
def verTutores():
    if request.method == "POST":
        return redirect("/tutores")

#----- Volver a registro -----
@app.route("/volverRegistro",methods=["GET","POST"])
def volverRegistro():
    if request.method == "POST":
        return redirect("/signup/estudiante")

#----- Inicio ---> Registro estudiantes ------
@app.route("/",methods=["GET","POST"])
def inicio():
    if request.method == "POST":
        return redirect("/signup/estudiante")
    return render_template("inicio.html")

#Grupos/Cursos ---> CrearCurso
@app.route("/irCursos",methods=["GET","POST"])
def irCursos():
    if request.method == "POST":
        return redirect("/signup/curso")
    return render_template("signup_cursos.html")

#Cerrar seccion
@app.route("/logout")
def logout():
    session["codigo"] = "debes iniciar sección en 'Login'"
    return "Te has desconectado"


#Ir a infoCursos
@app.route("/infoCursos",methods=["GET","POST"])
def info_cursos():
    
   #Esto es lo viejo (No funciona)
    #g = association_table
    #print(g)
    #usuarios_curso = []


    return render_template("infocursos.html")


#----- Ir a infor cursos -----
@app.route("/irInfo",methods=["GET","POST"])
def irInfo():
    if request.method == "POST":
        return redirect("/infoCursos")







@app.route("/search")
def search():
    nickname = request.args.get("username")
    return nickname

@app.route("/home")
def home():
    if "codigo" in session:
        return "Tu eres %s" % escape(session["codigo"])
    return "Debes logearte primero"



#Debe ser una llave secreta de verdad
app.secret_key = "12345"



if __name__=="__main__":
    db.create_all()
    app.run(debug=True)