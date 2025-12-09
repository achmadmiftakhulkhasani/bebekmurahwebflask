from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_mysqldb import MySQL, MySQLdb
from flask import send_file
import pandas as pd
import bcrypt 
import werkzeug

app = Flask(__name__)
app.secret_key = "membuatLOginFlask1"

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'flaskdb1'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'
mysql = MySQL(app)

@app.route('/')
def home() :
    return render_template("home.html")

@app.route('/laporan')
def laporan():
    cur = mysql.connection.cursor((MySQLdb.cursors.DictCursor))
    cur.execute("SELECT * FROM jurnal")
    datao = cur.fetchall()
    cur.close()
    # Calculate total debit and kredit
    total_debit = sum(item['debit'] for item in datao)
    total_kredit = sum(item['kredit'] for item in datao)
    
    return render_template('laporan.html', datao=datao, total_debit=total_debit, total_kredit=total_kredit)

@app.route('/unduhbarang', methods=['GET'])
def unduh_barang():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM jurnal")
    datao = cur.fetchall()
    cur.close()

    # Membuat DataFrame dari jurnal
    df = pd.DataFrame(datao, columns=['id', 'tanggal', 'nama', 'debit', 'kredit'])

    # Menyimpan DataFrame ke file Excel
    filename = 'data_umum.xlsx'
    df.to_excel(filename, index=False)

    # Mengembalikan file Excel sebagai respons
    return send_file(filename, as_attachment=True)


@app.route('/login', methods=['GET', 'POST'])
def login(): 
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password'].encode('utf-8')
        curl = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        curl.execute("SELECT * FROM users WHERE email=%s",(email,))
        user = curl.fetchone()
        curl.close()

        if user is not None and len(user) > 0 :
            if bcrypt.hashpw(password, user['password'].encode('utf-8')) == user['password'].encode('utf-8'):
                session['name'] = user ['name']
                session['email'] = user['email']
                return redirect(url_for('home'))
            else :
                flash("Gagal, Email dan Password Tidak Cocok")
                return redirect(url_for('login'))
        else :
            flash("Gagal, User Tidak Ditemukan")
            return redirect(url_for('login'))
    else: 
        return render_template("login.html")

@app.route('/register', methods=['POST', 'GET'])
def register():
    if request.method=='GET':
        return render_template('register.html')
    else :
        name = request.form['name']
        email = request.form['email']
        password = request.form['password'].encode('utf-8') 
        hash_password = bcrypt.hashpw(password, bcrypt.gensalt())

        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO users (name,email,password) VALUES (%s,%s,%s)" ,(name, email, hash_password)) 
        mysql.connection.commit()
        session['name'] = request.form['name']
        session['email'] = request.form['email']
        return redirect(url_for('home'))


@app.route('/jurnal', methods=['POST'])
def jurnal():
    if request.method == 'POST':
        tanggal_jurnal = request.form['tanggal']
        nama_jurnal = request.form['nama']
        debit_jurnal = request.form['debit']
        kredit_jurnal = request.form['kredit']
        # id_perusahaan = request.form['perusahaan']

        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO jurnal (tanggal, nama, debit, kredit) VALUES (%s, %s, %s, %s)", (tanggal_jurnal, nama_jurnal, debit_jurnal, kredit_jurnal)) 
        mysql.connection.commit()
        cur.close()
        flash("jurnal berhasil ditambahkan")
        return redirect(url_for('laporan'))

@app.route('/editbarang/<int:id>', methods=['POST'])
def edit_barang(id):
    if request.method == 'POST':
        tanggal_jurnal = request.form['tanggal']
        nama_jurnal = request.form['nama']
        debit_jurnal = request.form['debit']
        kredit_jurnal = request.form['kredit']

        cur = mysql.connection.cursor()
        cur.execute("UPDATE jurnal SET tanggal=%s, nama=%s, debit=%s, kredit=%s WHERE id=%s", (tanggal_jurnal, nama_jurnal, debit_jurnal, kredit_jurnal, id))
        mysql.connection.commit()
        cur.close()
        flash("Barang berhasil diupdate")
        return redirect(url_for('laporan'))

    return redirect(url_for('laporan'))

@app.route('/hapusbarang/<int:id>', methods=['GET'])
def hapus_barang(id):
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM jurnal WHERE id=%s", (id,))
    mysql.connection.commit()
    cur.close()
    flash("jurnal berhasil dihapus")
    return redirect(url_for('laporan'))






@app.route('/about')
def about():
    if 'email' in session:
        return render_template("about.html")
    else:
        return redirect(url_for('home'))
@app.route('/portofolio')
def portofolio():
    if 'email' in session:
        return render_template("portofolio.html")
    else:
        return redirect(url_for('home')) 
@app.route('/contact')
def contact():
    if 'email' in session:
        cur = mysql.connection.cursor((MySQLdb.cursors.DictCursor))
        cur.execute("SELECT * FROM jurnal")
        datao = cur.fetchall()
        cur.close()
        return render_template("contact.html", datao=datao)
    else:
        return redirect(url_for('home'))


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home')) 

@app.route('/viewpdf')
def view_pdf():
    # Provide the correct path to your PDF file
    return send_file('ProjekSIMfix.pdf', mimetype='application/pdf')


if __name__ == '__main__':
    app.run(debug=True)

    