import streamlit as st
import pandas as pd
import os

ARCHIVO_EXCEL = "estudiantes.xlsx"

st.set_page_config(layout="wide") # Configura el layout de la página para usar todo el ancho disponible

# --- Funciones de Utilidad ---

# Función para cargar datos o crear DataFrame vacío
def cargar_datos():
    if os.path.exists(ARCHIVO_EXCEL):
        # Si el archivo existe, simplemente lo carga
        return pd.read_excel(ARCHIVO_EXCEL)
    else:
        # Si el archivo NO existe, devuelve un DataFrame vacío
        st.warning(f"El archivo '{ARCHIVO_EXCEL}' no fue encontrado. Se iniciará con una base de datos vacía.")
        return pd.DataFrame(columns=["ID", "Nombre", "Email", "Teléfono", "Grupo"])

# Función para guardar datos
def guardar_datos(df):
    df.to_excel(ARCHIVO_EXCEL, index=False)

# Cargar datos existentes o iniciar con un DataFrame vacío
df = cargar_datos()

st.title("📚 Gestión de Estudiantes y Grupos")
st.markdown("---")

# --- AGREGAR O MODIFICAR ESTUDIANTE ---
st.header("➕ Agrega o Modifica Estudiantes")

# Obtener IDs y grupos existentes para las opciones
ids_existentes = ["0 (Nuevo Estudiante)"] + df["ID"].astype(str).tolist() if not df.empty else ["0 (Nuevo Estudiante)"]
grupos_existentes = df["Grupo"].unique().tolist() if not df.empty else []
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

        nombre = st.text_input("Nombre", value=nombre_precargado)
        email = st.text_input("Email", value=email_precargado)

    with col2:
        telefono_precargado = datos_estudiante.get("Teléfono", "")
        grupo_precargado = datos_estudiante.get("Grupo", "")

        telefono = st.text_input("Teléfono", value=telefono_precargado)

        # Input de grupo con autocompletado y opción de escribir nuevo
        grupo_input = st.text_input("Grupo", value=grupo_precargado, help="Selecciona un grupo existente o escribe uno nuevo.")
        if grupo_input and grupo_input not in grupos_existentes and len(grupos_existentes) > 0:
            st.warning(f"El grupo '{grupo_input}' es nuevo y se agregará al sistema.")
        
        grupo = grupo_input # Usamos el valor del text_input como el grupo final

    enviar_button = st.form_submit_button("💾 Guardar Estudiante")

if enviar_button:
    if nombre and email and telefono and grupo:
        if id_modificar == 0:
            # Agregar nuevo estudiante
            # Si el DataFrame está vacío, el primer ID será 1, de lo contrario, será el máximo ID + 1
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
            # Recargar la página para actualizar el selectbox de IDs y grupos
            st.rerun() 
        else:
            # Modificar estudiante existente
            if id_modificar in df["ID"].values:
                df.loc[df["ID"] == id_modificar, ["Nombre", "Email", "Teléfono", "Grupo"]] = [nombre, email, telefono, grupo]
                guardar_datos(df)
                st.success(f"✏️ ¡Estudiante con ID {id_modificar} modificado con éxito!")
                # Recargar la página para actualizar el selectbox de IDs y grupos
                st.rerun()
            else:
                st.error(f"❌ Error: No existe estudiante con ID {id_modificar} para modificar.")
    else:
        st.error("⚠️ Por favor, completa todos los campos (Nombre, Email, Teléfono, Grupo).")

st.markdown("---")

# --- ELIMINAR ESTUDIANTE ---
st.header("🗑️ Eliminar Estudiante")

with st.form("form_eliminar_estudiante"):
    st.write("Ingresa el ID del estudiante que deseas eliminar.")
    # Asegúrate de que el valor por defecto sea válido si el df está vacío
    default_id_eliminar = 1 if not df.empty else 0 
    id_eliminar = st.number_input("ID del estudiante a eliminar", min_value=0, step=1, value=default_id_eliminar)
    confirmar_eliminar = st.form_submit_button("🚫 Eliminar Estudiante")

if confirmar_eliminar:
    if id_eliminar == 0:
        st.error("❌ Por favor, ingresa un ID válido (mayor que 0) para eliminar.")
    elif id_eliminar in df["ID"].values:
        df = df[df["ID"] != id_eliminar]
        guardar_datos(df)
        st.success(f"🗑️ ¡Estudiante con ID {id_eliminar} eliminado con éxito!")
        # Recargar la página para actualizar las tablas y selectboxes
        st.rerun() 
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