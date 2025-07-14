import streamlit as st
import pandas as pd
from datetime import date
import os

PERSONAS_FILE = "personas.csv"
HISTORIAL_FILE = "historial.csv"

def cargar_personas():
    if os.path.exists(PERSONAS_FILE):
        return pd.read_csv(PERSONAS_FILE)
    else:
        return pd.DataFrame(columns=["Nombre"] + [f"N{i+1}" for i in range(10)])

def guardar_personas(df):
    df.to_csv(PERSONAS_FILE, index=False)

def guardar_historial(fecha, numeros, coincidencias):
    df = pd.DataFrame({
        "Fecha": [fecha] * len(numeros),
        "Número": numeros,
        "Coincide": coincidencias
    })
    if os.path.exists(HISTORIAL_FILE):
        historial = pd.read_csv(HISTORIAL_FILE)
        historial = pd.concat([historial, df], ignore_index=True)
    else:
        historial = df
    historial.to_csv(HISTORIAL_FILE, index=False, encoding="utf-8-sig")

st.title("🎯 Control Diario de Números")

menu = st.sidebar.radio("Menú", ["✅ Verificar números diarios", "📋 Administrar personas"])

if menu == "✅ Verificar números diarios":
    st.header("✅ Verificar 20 números diarios")
    personas = cargar_personas()

    numeros_dia = st.text_input("Ingresá los 20 números separados por coma", "")
    if st.button("Verificar Coincidencias"):
        try:
            numeros = [int(x.strip()) for x in numeros_dia.split(",") if x.strip() != ""]
            if len(numeros) != 20:
                st.error("Debés ingresar exactamente 20 números.")
            else:
                coincidencias = []
                for n in numeros:
                    coincide = (personas.iloc[:, 1:].astype(str) == str(n)).any().any()
                    coincidencias.append("✔️" if coincide else "❌")
                resultado = pd.DataFrame({
                    "Número": numeros,
                    "Coincidencia": coincidencias
                })
                st.success("Resultado de comparación:")
                st.dataframe(resultado)
                guardar_historial(str(date.today()), numeros, [c == "✔️" for c in coincidencias])
        except Exception as e:
            st.error(f"Error al procesar los números: {e}")

    if os.path.exists(HISTORIAL_FILE):
        with open(HISTORIAL_FILE, "rb") as f:
            st.download_button("⬇️ Descargar historial", f, file_name="historial.csv")

elif menu == "📋 Administrar personas":
    st.header("📋 Gestión de Personas y sus Números")
    df = cargar_personas()

    st.subheader("Listado actual")
    st.dataframe(df)

    st.subheader("➕ Agregar persona")
    nombre = st.text_input("Nombre")
    numeros = st.text_input("10 números separados por coma")
    if st.button("Agregar"):
        try:
            lista_numeros = [int(x.strip()) for x in numeros.split(",")]
            if len(lista_numeros) != 10:
                st.error("Debés ingresar exactamente 10 números.")
            else:
                nueva_persona = pd.DataFrame([[nombre] + lista_numeros], columns=df.columns)
                df = pd.concat([df, nueva_persona], ignore_index=True)
                guardar_personas(df)
                st.success("Persona agregada correctamente.")
                st.experimental_rerun()
        except Exception as e:
            st.error(f"Error: {e}")

    st.subheader("❌ Eliminar persona")
    nombres = df["Nombre"].tolist()
    persona_a_eliminar = st.selectbox("Seleccioná una persona", [""] + nombres)
    if st.button("Eliminar") and persona_a_eliminar:
        df = df[df["Nombre"] != persona_a_eliminar]
        guardar_personas(df)
        st.success("Persona eliminada.")
        st.rerun()
