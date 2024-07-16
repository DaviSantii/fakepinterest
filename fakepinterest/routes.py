from flask import render_template, url_for, redirect
from fakepinterest import app, database, bcrypt
from flask_login import login_required, login_user, logout_user, current_user
from fakepinterest.forms import FormLogin, FormCriarConta, FormFoto
from fakepinterest.models import Usuario, Foto
import os
from werkzeug.utils import secure_filename


@app.route("/", methods=["GET", "POST"])
def homepage():
    login = FormLogin()
    if login.validate_on_submit():
        usuario = Usuario.query.filter_by(email=login.email.data).first()
        if usuario and bcrypt.check_password_hash(usuario.senha, login.senha.data):
            login_user(usuario)
            return redirect(url_for("perfil", id_usuario= usuario.id))
    return render_template("homepage.html", form = login)

@app.route("/criar-conta", methods=["GET", "POST"])
def criarconta():
    criarconta = FormCriarConta()
    if criarconta.validate_on_submit():
        senha = bcrypt.generate_password_hash(criarconta.senha.data)
        usuario = Usuario(username=criarconta.username.data, email=criarconta.email.data, senha=senha)
        database.session.add(usuario)
        database.session.commit()
        login_user(usuario, remember= True)
        return redirect(url_for("perfil", id_usuario= usuario.id))
    return render_template("criar-conta.html", form = criarconta)

@app.route("/perfil/<id_usuario>", methods=["GET", "POST"])
@login_required
def perfil(id_usuario):
    if (int(id_usuario)) == int(current_user.id):
        form_foto = FormFoto()
        if form_foto.validate_on_submit():
            arquivo = form_foto.foto.data
            nome_seguro = secure_filename(arquivo.filename)
            # salvar o arquivo na pasta fotos_post
            caminho = os.path.join(os.path.abspath(os.path.dirname(__file__)),app.config["UPLOAD_FOLDER"],nome_seguro)
            arquivo.save(caminho)
            # registrar esse arquivo no banco de dados
            foto = Foto(imagem=nome_seguro, id_usuario = current_user.id)
            database.session.add(foto)
            database.session.commit()
        return render_template("perfil.html", usuario= current_user, form= form_foto)
    else:
        usuario = Usuario.query.get(int(id_usuario))
        return render_template("perfil.html", usuario= usuario, form= None)

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("homepage"))

@app.route("/feed")
@login_required
def feed():
    fotos = Foto.query.order_by(Foto.data_criacao.desc()).all()#[:200] até 200 fotos
    return render_template("feed.html", fotos=fotos)