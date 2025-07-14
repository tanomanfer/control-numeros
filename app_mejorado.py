import streamlit as st
import pandas as pd
from datetime import date
import os

PERSONAS_FILE = "personas.csv"
HISTORIAL_FILE = "historial_detallado.csv"

def cargar_personas():
    if os.path.exists(PERSONAS_FILE):
        return pd.read_csv(PERSONAS_FILE)
    else:
        return pd.DataFrame(columns=["Nombre"] + [f"N{i+1}" for i in range(10)])

def guardar_historial_detallado(dataframe):
    if os.path.exists(HISTORIAL_FILE):
        anterior = pd.read_csv(HISTORIAL_FILE)
        dataframe = pd.concat([anterior, dataframe], ignore_index=True)
    dataframe.to_csv(HISTORIAL_FILE, index=False, encoding="utf-8-sig")

st.title("🎯 Control Diario de Números")

personas_df = cargar_personas()

st.sidebar.title("Menú")
menu = st.sidebar.radio("Seleccioná una opción", ["📅 Verificación diaria", "👥 Administrar personas"])

if menu == "📅 Verificación diaria":
    st.header("📅 Ingresá los 20 números del día")
    numeros_input = st.text_input("Números del día (separados por coma)")
    if st.button("Verificar coincidencias"):
        try:
            numeros_dia = [int(x.strip()) for x in numeros_input.split(",") if x.strip()]
            if len(numeros_dia) != 20:
                st.error("Debés ingresar exactamente 20 números.")
            else:
                resultados = []
                resumen = []

                for _, fila in personas_df.iterrows():
                    nombre = fila["Nombre"]
                    numeros = fila[1:].dropna().astype(int).tolist()
                    aciertos = [n for n in numeros if n in numeros_dia]
                    resultado_visual = [f"✅{n}" if n in aciertos else str(n) for n in numeros]

                    resultados.append({
                        "Nombre": nombre,
                        "Números": ", ".join(resultado_visual),
                        "Aciertos": len(aciertos)
                    })

                    for n in numeros:
                        resultados.append({
                            "Fecha": str(date.today()),
                            "Persona": nombre,
                            "Número": n,
                            "Coincide": n in numeros_dia
                        })

                df_resumen = pd.DataFrame(resultados)
                df_tabla = pd.DataFrame([{
                    "Nombre": r["Nombre"],
                    "Aciertos": r["Aciertos"],
                    "Números": r["Números"]
                } for r in resultados if "Nombre" in r])

                st.success("Coincidencias encontradas")
                st.dataframe(df_tabla)

                guardar_historial_detallado(df_resumen)

                # Descargar historial detallado
                with open(HISTORIAL_FILE, "rb") as f:
                    st.download_button("⬇️ Descargar historial detallado", f, file_name="historial_detallado.csv")

        except Exception as e:
            st.error(f"Error al procesar los números: {e}")

elif menu == "👥 Administrar personas":
    st.header("👥 Administración de Personas")
    st.subheader("📄 Personas registradas")
    st.dataframe(personas_df)

    st.subheader("➕ Agregar persona")
    nombre = st.text_input("Nombre")
    numeros_txt = st.text_input("10 números separados por coma")
    if st.button("Agregar persona"):
        try:
            numeros = [int(x.strip()) for x in numeros_txt.split(",")]
            if len(numeros) != 10:
                st.error("Ingresá exactamente 10 números.")
            else:
                nueva_fila = pd.DataFrame([[nombre] + numeros], columns=personas_df.columns)
                personas_df = pd.concat([personas_df, nueva_fila], ignore_index=True)
                personas_df.to_csv(PERSONAS_FILE, index=False)
                st.success("Persona agregada.")
                st.rerun()
        except:
            st.error("Formato incorrecto.")

    st.subheader("❌ Eliminar persona")
    opciones = personas_df["Nombre"].tolist()
    persona_a_eliminar = st.selectbox("Seleccioná", [""] + opciones)
    if st.button("Eliminar") and persona_a_eliminar:
        personas_df = personas_df[personas_df["Nombre"] != persona_a_eliminar]
        personas_df.to_csv(PERSONAS_FILE, index=False)
        st.success("Persona eliminada.")
        st.rerun()
