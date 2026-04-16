import streamlit as st
import pickle
import pandas as pd
import numpy as np

st.write("App iniciando...")
@st.cache_data
def cargar_datos():
    with open("resultados.pkl", "rb") as f:
        data = pickle.load(f)
    return data["resultados"], data["sectores"], data["sector_names"]

resultados, sectores, sector_names = cargar_datos()
st.write("Datos cargados")

def simular(estado, sector, monto):
    L_r = resultados[estado]["L_r"]

    shock = np.zeros(len(sectores))
    idx = sectores.index(sector)
    shock[idx] = monto

    impacto = L_r @ shock
    impacto_total = impacto.sum()
    multiplicador = impacto_total / monto if monto != 0 else 0

    df = pd.DataFrame({
        "sector": sectores,
        "impacto": impacto
    }).sort_values(by="impacto", ascending=False)

    return impacto_total, multiplicador, df.head(10)

st.title("Simulador Económico Regional")

estado = st.selectbox(
    "Estado",
    list(resultados.keys()),
    format_func=lambda x: x.replace("_Sectores_", " - ").replace("_3CIF", "")
)

sector = st.selectbox(
    "Sector",
    sectores,
    format_func=lambda x: f"{x} - {sector_names.get(x, '')}"
)

monto = st.number_input("Monto (MXN)", value=1000000.0)

if st.button("Simular"):
    impacto_total, multiplicador, df_top = simular(estado, sector, monto)

    if monto > 0:
        st.success("Inversión positiva (expansión económica)")
    else:
        st.warning("Shock negativo (contracción económica)")

    st.metric("Impacto total", f"${impacto_total:,.2f}")
    st.metric("Multiplicador", f"{multiplicador:.2f}")

    st.write(f"Un cambio de ${monto:,.0f} en este sector genera un impacto total de ${impacto_total:,.0f} en la economía del estado.")

    if impacto_total > 0:
        st.success(f"Esto representa un crecimiento económico estimado de ${impacto_total:,.0f} en el estado.")
    else:
        st.error(f"Esto representa una contracción económica estimada de ${abs(impacto_total):,.0f} en el estado.")

    if multiplicador > 1:
        st.info("El efecto es amplificado en la economía (multiplicador > 1)")
    else:
        st.info("El efecto es limitado (multiplicador ≤ 1)")

    df_top["nombre"] = df_top["sector"].map(lambda x: sector_names.get(x, ""))
    df_top = df_top[["nombre", "impacto"]]
    
    st.dataframe(df_top)

    top_sector = df_top.iloc[0]

    st.bar_chart(df_top.set_index("nombre")["impacto"])