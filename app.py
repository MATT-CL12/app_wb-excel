import streamlit as st
import pandas as pd
import os

ARCHIVO_EXCEL = "estudiantes.xlsx"

st.set_page_config(layout="wide") # Configura el layout de la página para usar todo el ancho disponible

# --- Funciones de Utilidad ---

# Función para cargar datos o crear DataFrame vacío con datos de ejemplo
def cargar_datos():
    if os.path.exists(ARCHIVO_EXCEL):
        return pd.read_excel(ARCHIVO_EXCEL)
    else:
        # Si el archivo no existe, crea un DataFrame con datos de ejemplo
        data_ejemplo = {
            "ID": [1, 2, 3, 4, 5],
            "Nombre": ["Ana García", "Carlos Ruíz", "Sofía López", "Diego Pérez", "Elena Castro"],
            "Email": ["ana.garcia@example.com", "carlos.ruiz@example.com", "sofia.lopez@example.com", "diego.perez@example.com", "elena.castro@example.com"],
            "Teléfono": ["123456789", "987654321", "555123456", "777888999", "333222111"],
            "Grupo": ["Grupo A", "Grupo B", "Grupo A", "Grupo C", "Grupo B"]
        }
        df_ejemplo = pd.DataFrame(data_ejemplo)
        df_ejemplo.to_excel(ARCHIVO_EXCEL, index=False) # Guarda los datos de ejemplo
        return df_ejemplo

# Función para guardar datos
def guardar_datos(df):
    df.to_excel(ARCHIVO_EXCEL, index=False)

# Cargar datos existentes o crear el archivo de ejemplo
df = cargar_datos()

st.title("📚 Gestión de Estudiantes y Grupos")
st.markdown("---")

# --- AGREGAR O MODIFICAR ESTUDIANTE ---
st.header("➕ Agrega o Modifica Estudiantes")

# Obtener IDs y grupos existentes para las opciones
ids_existentes = ["0 (Nuevo Estudiante)"] + df["ID"].astype(str).tolist()
grupos_existentes = df["Grupo"].unique().tolist()
grupos_existentes.sort() # Ordenar los grupos alfabéticamente

with st.form("form_estudiante", clear_on_submit=True):
    st.write("Completa los datos del estudiante. Si el ID es 0, se agregará un nuevo estudiante.")

    col1, col2 = st.columns(2)

    with col1:
        id_seleccionado = st.selectbox("Selecciona un ID para modificar o '0' para agregar", options=ids_existentes)
        id_modificar = 0
        if id_seleccionado != "0 (Nuevo Estudiante)":
            id_modificar = int(id_seleccionado)

        # Precargar datos si se selecciona un estudiante existente
        datos_estudiante = {}
        if id_modificar != 0 and id_modificar in df["ID"].values:
            datos_estudiante = df[df["ID"] == id_modificar].iloc[0].to_dict()

        nombre_precargado = datos_estudiante.get("Nombre", "")
        email_precargado = datos_estudiante.get("Email", "")
        telefono_precargado = datos_estudiante.get("Teléfono", "")
        grupo_precargado = datos_estudiante.get("Grupo", "")

        nombre = st.text_input("Nombre", value=nombre_precargado)
        email = st.text_input("Email", value=email_precargado)

    with col2:
        telefono = st.text_input("Teléfono", value=telefono_precargado)

        # Input de grupo con autocompletado y opción de escribir nuevo
        grupo_input = st.text_input("Grupo", value=grupo_precargado, help="Selecciona un grupo existente o escribe uno nuevo.")
        if grupo_input and grupo_input not in grupos_existentes and len(grupos_existentes) > 0:
            st.warning(f"El grupo '{grupo_input}' es nuevo y se agregará al sistema.")
        
        # Opcional: un selectbox para elegir de los existentes, si se prefiere
        # if len(grupos_existentes) > 0:
        #     opciones_grupo = ["(Escribir nuevo)"] + grupos_existentes
        #     grupo_seleccionado_sb = st.selectbox("O selecciona un grupo existente:", options=opciones_grupo, index=opciones_grupo.index(grupo_precargado) if grupo_precargado in opciones_grupo else 0)
        #     if grupo_seleccionado_sb != "(Escribir nuevo)":
        #         grupo = grupo_seleccionado_sb
        #     else:
        #         grupo = st.text_input("Escribe el nombre del grupo:")
        # else:
        #     grupo = st.text_input("Escribe el nombre del grupo:")
        
        grupo = grupo_input # Usamos el valor del text_input como el grupo final

    enviar_button = st.form_submit_button("💾 Guardar Estudiante")

if enviar_button:
    if nombre and email and telefono and grupo:
        if id_modificar == 0:
            # Agregar nuevo estudiante
            nuevo_id = df["ID"].max() + 1 if not df.empty else 1
            nuevo_registro = {
                "ID": nuevo_id,
                "Nombre": nombre,
                "Email": email,
                "Teléfono": telefono,
                "Grupo": grupo
            }
            # Usar pd.concat en lugar de append (append está obsoleto)
            df = pd.concat([df, pd.DataFrame([nuevo_registro])], ignore_index=True)
            guardar_datos(df)
            st.success(f"✅ ¡Estudiante '{nombre}' agregado con ID {nuevo_id}!")
        else:
            # Modificar estudiante existente
            if id_modificar in df["ID"].values:
                df.loc[df["ID"] == id_modificar, ["Nombre", "Email", "Teléfono", "Grupo"]] = [nombre, email, telefono, grupo]
                guardar_datos(df)
                st.success(f"✏️ ¡Estudiante con ID {id_modificar} modificado con éxito!")
            else:
                st.error(f"❌ Error: No existe estudiante con ID {id_modificar} para modificar.")
    else:
        st.error("⚠️ Por favor, completa todos los campos (Nombre, Email, Teléfono, Grupo).")

st.markdown("---")

# --- ELIMINAR ESTUDIANTE ---
st.header("🗑️ Eliminar Estudiante")

with st.form("form_eliminar_estudiante"):
    st.write("Ingresa el ID del estudiante que deseas eliminar.")
    id_eliminar = st.number_input("ID del estudiante a eliminar", min_value=1, step=1, value=1)
    confirmar_eliminar = st.form_submit_button("🚫 Eliminar Estudiante")

if confirmar_eliminar:
    if id_eliminar in df["ID"].values:
        df = df[df["ID"] != id_eliminar]
        guardar_datos(df)
        st.success(f"🗑️ ¡Estudiante con ID {id_eliminar} eliminado con éxito!")
    else:
        st.error(f"❌ Error: No se encontró un estudiante con ID {id_eliminar}.")

st.markdown("---")

# --- VER ESTUDIANTES ---
st.header("📊 Estudiantes y Grupos")

tab1, tab2 = st.tabs(["Ver Todos los Estudiantes", "Ver por Grupo"])

with tab1:
    st.subheader("Todos los Estudiantes")
    if df.empty:
        st.info("No hay estudiantes registrados. Agrega algunos para empezar.")
    else:
        st.dataframe(df, use_container_width=True)

with tab2:
    st.subheader("Filtrar por Grupo")
    if df.empty:
        st.info("No hay grupos disponibles. Agrega estudiantes primero.")
    else:
        grupos_disponibles = ["Todos los Grupos"] + df["Grupo"].unique().tolist()
        grupo_seleccionado_filtro = st.selectbox("Selecciona un grupo para filtrar", options=grupos_disponibles)

        if grupo_seleccionado_filtro == "Todos los Grupos":
            estudiantes_filtrados = df
        else:
            estudiantes_filtrados = df[df["Grupo"] == grupo_seleccionado_filtro]

        if estudiantes_filtrados.empty:
            st.info(f"No hay estudiantes en el grupo '{grupo_seleccionado_filtro}'.")
        else:
            st.dataframe(estudiantes_filtrados.drop(columns=["ID"]), use_container_width=True)