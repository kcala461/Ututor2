
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

#Tabla para guardar las dos llaves primarias.
association_table = db.Table('association_table',
                          db.Column('users_id',Integer,ForeignKey('users.username')),
                          db.Column('grupos_id',Integer,ForeignKey('grupos.codigo'))
                          )
    

#----- Tabla de estudiantes. -----
class Users(db.Model):
    __tablename__ = 'users'
    codigo = db.Column(db.String(9), primary_key = True)
    username = db.Column(db.String(50),nullable =True)
    password = db.Column(db.String(80),nullable =True)
    carerra = db.Column(db.String(80),nullable =True)
    semestre = db.Column(db.String(80),nullable =True)
    tutor = db.Column(db.String(2),nullable =True)
    #Esto funcionaaaaa!!!!! (Versión good)
    grupos = db.relationship("Grupos",secondary=association_table)


    #def __str__(self):
    #    return str("La persona c:" + str(self.codigo) + ", nombre: " + str(self.username) + 
    #    ", grupos: " + str(self.grupos))
    
    def __str__(self):
        return str("La persona c: Nombre:" + str(self.username) + 
        ", grupos: " + str(self.grupos))


#----- Tabla de grupos. -----
class Grupos(db.Model):
    __tablename__ = 'grupos'
    codigo = db.Column(db.Integer, primary_key = True)
    materia = db.Column(db.String(50),nullable =True)
    lugar = db.Column(db.String(80),nullable =True)
    dia = db.Column(db.String(80),nullable =True)
    hora = db.Column(db.String(80),nullable =True)
    tutor = db.Column(db.String(80),nullable =True)
    #Esto funcionaaaaa
    userss = db.relationship("Users",secondary=association_table)


    def __str__(self):
        return str("El grupo c:" + str(self.codigo) + ", materia: " + str(self.materia) + 
        ", user: " + str(self.userss))


#----- Entrar en un curso -----
@app.route("/entrarCursos",methods=["GET","POST"])
def entrar_Cursos():
    if request.method == "GET":
        Grupos.user = Users
        db.session.commit()
        return redirect("/cursos")
    elif request.method == "POST":
        print(request.form['id'])
        
        #GUARDA EN LA BASE DE DATOS!
        s = Grupos.query.filter_by(codigo=request.form['id']).first()
        print(s)
        c = Users.query.filter_by(codigo=session["codigo"]).first()
        c.grupos.append(s)
        db.session.add(c)
        db.session.commit()


        
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


#----- Registro del curso -----
@app.route("/signup/curso",methods=["GET","POST"])
def signup_curso():
    if request.method == "POST":
        if session["codigo"] != "debes iniciar sección en 'Login'":
            if session["tutor"] == "Si":
                new_curso = Grupos(materia=request.form["materia"],lugar=request.form["lugar"],dia=request.form["dia"],tutor=session["username"],hora=request.form["hora"])
                db.session.add(new_curso)
                db.session.commit()
                return redirect("/cursos")    
            else:
                flash("No eres tutor, por ende no puedes crear grupos de estudio")
        else:
            flash("Debes loguearte primero")
    return render_template("signup_curso.html")


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








#Redirecciones: 

#----- Ingresar a la pagina de cursos (cursos.html) -----
@app.route("/cursos", methods=['GET','POST'])
def cursos():
    g = Grupos.query.all()
    grupos = []
    for item in g:
        grupos.append({"codigo": item.codigo,"lugar" : item.lugar ,"materia": item.materia, "tutor" : item.tutor})

    return render_template('cursos.html', g = grupos)

#----- Ingresar a pagina de tutores (tutor.html) -----
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

#----- Volver a los grupos -----
@app.route("/volverGrupos",methods=["GET","POST"])
def volverGrupos():
    if request.method == "POST":
        return redirect("/cursos")

#----- Volver al login -----
@app.route("/volverLogin",methods=["GET","POST"])
def volverLogin():
    if request.method == "POST":
        return redirect("/login")

#----- Volver a los tutores -----
@app.route("/verTutores",methods=["GET","POST"])
def verTutores():
    if request.method == "POST":
        return redirect("/tutores")

#----- Volver al registro -----
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


#Ir a la información de los grupos (infocursos.html)
@app.route("/infoCursos",methods=["GET","POST"])
def info_cursos():

    #----- OPCION FOTO 1 -----
    #y = Users.query.join(association_table).join(Grupos).filter((association_table.c.users_id == Users.username) 
    #                                            & (association_table.c.grupos_id == Grupos.codigo)).all()

    #usuarios_curso = []
    #for i in y:
    #    usuarios_curso.append({"nombre":i.username,"grupos":i.grupos})
    
    #for x in usuarios_curso:
    #    print(x)

    #----- OPCION FOTO 2 -----
    x = Grupos.query.join(association_table).join(Users).filter((association_table.c.users_id == Users.username) 
                                            & (association_table.c.grupos_id == Grupos.codigo)).all()

    usuarios_curso = []
    xd = []

    for i in x:
        usuarios_curso.append({"Codigo":i.codigo,"User":i.userss,"Materia":i.materia,"Dia":i.dia,"Hora":i.hora})
    

    for x in usuarios_curso:
        print(x)


    return render_template("infocursos.html", h = usuarios_curso, y = xd)


#----- Ir a la información de los grupos (infocursos.html) -----
@app.route("/irInfo",methods=["GET","POST"])
def irInfo():
    if request.method == "POST":
        return redirect("/infoCursos")



app.secret_key = "12345"

if __name__=="__main__":
    db.create_all()
    app.run(debug=True)