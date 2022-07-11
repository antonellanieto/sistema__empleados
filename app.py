from webbrowser import get
from flask import Flask, redirect
from flask import render_template, request ,  redirect
from flaskext.mysql import MySQL
from datetime import datetime
from toastify import notify
import os
from flask import send_from_directory

app= Flask(__name__)


mysql= MySQL()
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = ''
app.config['MYSQL_DATABASE_DB'] = 'sistemaempleados'
mysql.init_app(app)

CARPETA = os.path.join('uploads')
app.config['CARPETA']=CARPETA

@app.route("/uploads/<nombreFoto>")
def uploads(nombreFoto):
    return send_from_directory(app.config['CARPETA'], nombreFoto)






@app.route("/")
def index():
    sql = "SELECT * FROM `empleados`;"
    conn= mysql.connect()
    cursor=conn.cursor()
    cursor.execute(sql)
    empleados = cursor.fetchall()
    print(empleados)
    conn.commit()
    return render_template('empleados/index.html' , empleados=empleados)


@app.route("/destroy/<int:id>")
def destroy(id):
    conn= mysql.connect()
    cursor=conn.cursor()

    cursor.execute('SELECT foto FROM empleados WHERE id= %s', id)
    fila = cursor.fetchall()
    os.remove(os.path.join(app.config['CARPETA'], fila [0][0]))


    cursor.execute("DELETE FROM empleados WHERE id =%s ", (id))
    conn.commit()
    return redirect('/')  

@app.route("/edit/<int:id>")
def edit(id):
    conn= mysql.connect()
    cursor=conn.cursor()
    cursor.execute("SELECT * FROM empleados WHERE id =%s ", (id))
    empleados = cursor.fetchall()
    conn.commit()
    return render_template('empleados/edit.html', empleados = empleados)


@app.route("/update" , methods = ['POST'])
def update():
    _nombre = request.form['txtNombre']
    _correo =  request.form['txtCorreo']
    _foto   = request.files['txtFoto']
    id     = request.form['txtId']
    sql = "UPDATE empleados SET nombre=%s , correo=%s WHERE id=%s;" 
    datos=(_nombre,_correo, id)    
    conn=mysql.connect()
    cursor=conn.cursor()

    now = datetime.now()
    tiempo = now.strftime("%Y%H%M%S")

    if _foto.filename != '':
        nuevoNombreFoto = tiempo + _foto.filename
        _foto.save('uploads/' + nuevoNombreFoto)

        #ver como se llama la foto de ese id
        #para borrarla
        cursor.execute("SELECT foto FROM empleados WHERE id = %s", id)
        fila=cursor.fetchall()
        print(fila)
        os.remove(os.path.join(app.config['CARPETA'],fila[0][0] ))
        cursor.execute("UPDATE empleados SET foto=%s WHERE id=%s",(nuevoNombreFoto, id ))
        conn.commit()

    cursor.execute(sql,datos)
    conn.commit()
    return redirect('/')

@app.route("/create")
def create():
    return render_template('empleados/create.html')


@app.route("/store", methods=['POST'])
def storage():
    _nombre = request.form['txtNombre']
    _correo = request.form['txtCorreo']
    _foto = request.files['txtFoto']
    
    now = datetime.now()
    tiempo = now.strftime("%Y%H%M%S")

    if _foto.filename != "":
       nuevo_nombre_foto = tiempo + _foto.filename
       _foto.save("uploads/" + nuevo_nombre_foto)

    sql = "INSERT INTO `empleados` (`id`, `nombre`, `correo`, `foto`) VALUES (NULL, %s, %s, %s);"
    datos=(_nombre, _correo, nuevo_nombre_foto)


    conn=mysql.connect()
    cursor=conn.cursor()
    cursor.execute(sql, datos)
    conn.commit()
    return redirect('/')












if __name__ == '__main__':
    app.run(debug=True)