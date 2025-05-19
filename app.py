from flask import Flask, render_template, request, redirect, url_for, session
import pandas as pd
import json
import os

app = Flask(__name__)
app.secret_key = 'clave_secreta'

EXCEL_PATH = 'data/base_datos.xlsx'
USUARIOS_JSON = 'data/usuarios.json'

def cargar_datos():
    xls = pd.ExcelFile(EXCEL_PATH)
    return {
        'grupos': pd.read_excel(xls, 'Grupos'),
        'materias': pd.read_excel(xls, 'Materias'),
        'estudiantes': pd.read_excel(xls, 'Estudiantes'),
        'notas': pd.read_excel(xls, 'Notas')
    }

def guardar_datos(dfs):
    with pd.ExcelWriter(EXCEL_PATH, engine='openpyxl', mode='w') as writer:
        for key, df in dfs.items():
            df.to_excel(writer, sheet_name=key.capitalize(), index=False)

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        with open(USUARIOS_JSON) as f:
            usuarios = json.load(f)
        user = request.form['username']
        pwd = request.form['password']
        if user in usuarios and usuarios[user]['password'] == pwd:
            session['user'] = user
            return redirect(url_for('home'))
        return 'Credenciales inválidas'
    return render_template('login.html')

@app.route('/home')
def home():
    if 'user' not in session:
        return redirect(url_for('login'))
    return render_template('home.html')

@app.route('/grupos')
def grupos():
    datos = cargar_datos()
    return render_template('grupos.html', grupos=datos['grupos'].to_dict(orient='records'))

@app.route('/materias')
def materias():
    datos = cargar_datos()
    return render_template('materias.html', materias=datos['materias'].to_dict(orient='records'))

@app.route('/grupo/<int:grupo_id>')
def estudiantes_grupo(grupo_id):
    datos = cargar_datos()
    estudiantes = datos['estudiantes'][datos['estudiantes']['GrupoID'] == grupo_id]
    return render_template('estudiantes.html', estudiantes=estudiantes.to_dict(orient='records'))

@app.route('/materia/<int:materia_id>')
def estudiantes_materia(materia_id):
    datos = cargar_datos()
    estudiantes_ids = datos['notas'][datos['notas']['MateriaID'] == materia_id]['EstudianteID']
    estudiantes = datos['estudiantes'][datos['estudiantes']['ID'].isin(estudiantes_ids)]
    return render_template('estudiantes.html', estudiantes=estudiantes.to_dict(orient='records'))

@app.route('/estudiante/<int:est_id>', methods=['GET', 'POST'])
def ver_estudiante(est_id):
    datos = cargar_datos()
    estudiante = datos['estudiantes'][datos['estudiantes']['ID'] == est_id].iloc[0]
    materias = datos['materias']
    notas = datos['notas'][datos['notas']['EstudianteID'] == est_id]

    if request.method == 'POST':
        for i in notas.index:
            nueva_nota = request.form.get(f"nota_{notas.loc[i, 'MateriaID']}")
            if nueva_nota:
                datos['notas'].loc[i, 'Nota'] = float(nueva_nota)
        guardar_datos(datos)
        return redirect(url_for('ver_estudiante', est_id=est_id))

    info = []
    for _, nota in notas.iterrows():
        materia = materias[materias['ID'] == nota['MateriaID']].iloc[0]
        info.append({
            'Materia': materia['Nombre'],
            'Nota': nota['Nota'],
            'MateriaID': nota['MateriaID']
        })

    return render_template('estudiante.html', estudiante=estudiante, info=info)

if __name__ == '__main__':
    app.run(debug=True)
