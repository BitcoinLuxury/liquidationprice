import streamlit as st

def calcular_dca(balance, precio_inicial, precio_final, tipo):
    entradas = 8
    apalancamiento = 500
    valor_lote = 100000
    margen_por_lote = valor_lote / apalancamiento  # 200 USD por lote
    pip_value_por_lote = 10  # USD por pip por lote

    distancia_total = abs(precio_final - precio_inicial)
    paso_entre_entradas = distancia_total / (entradas - 1)

    precios = [
        precio_inicial + i * paso_entre_entradas * (-1 if tipo == 'buy' else 1)
        for i in range(entradas)
    ]

    lote = 1.0
    paso = 0.01
    lote_aceptable = 0.0

    while lote > 0:
        margen_total = lote * entradas * margen_por_lote
        if margen_total > balance:
            lote -= paso
            continue

        total_cost = sum(precio * lote for precio in precios)
        breakeven = total_cost / (lote * entradas)

        distancia_liquidacion = breakeven * 0.10
        liquidacion = breakeven - distancia_liquidacion if tipo == 'buy' else breakeven + distancia_liquidacion
        pips_contra = abs(breakeven - liquidacion) / 0.0001
        perdida_total = pips_contra * lote * entradas * pip_value_por_lote

        if perdida_total <= balance:
            lote_aceptable = lote
            break

        lote -= paso

    if lote_aceptable == 0.0:
        return None

    total_cost = sum(precio * lote_aceptable for precio in precios)
    breakeven = total_cost / (lote_aceptable * entradas)
    liquidacion = breakeven - breakeven * 0.10 if tipo == 'buy' else breakeven + breakeven * 0.10
    pips_contra = abs(breakeven - liquidacion) / 0.0001
    perdida_total = pips_contra * lote_aceptable * entradas * pip_value_por_lote
    margen_total = lote_aceptable * entradas * margen_por_lote

    return {
        'entradas': entradas,
        'lote': round(lote_aceptable, 2),
        'rango': (round(precios[-1], 5), round(precios[0], 5)),
        'breakeven': round(breakeven, 5),
        'liquidacion': round(liquidacion, 5),
        'perdida_total': round(perdida_total, 2),
        'margen_usado': round(margen_total, 2)
    }

# ==== INTERFAZ STREAMLIT ====
st.set_page_config(page_title="Calculadora DCA Forex", layout="centered")

st.title("📊 Calculadora DCA Forex (1:500)")
st.markdown("Simula entradas DCA con apalancamiento 1:500. Precio de liquidación a 10% del breakeven.")

with st.form("formulario_dca"):
    balance = st.number_input("💰 Balance de la cuenta (USD)", min_value=1.0, value=5000.0)
    precio_inicial = st.number_input("📈 Precio inicial", value=1.1800, format="%.5f")
    precio_final = st.number_input("📉 Precio final", value=1.0100, format="%.5f")
    tipo = st.selectbox("🟩 Tipo de operación", options=["buy", "sell"])

    calcular = st.form_submit_button("📐 Calcular")

if calcular:
    resultado = calcular_dca(balance, precio_inicial, precio_final, tipo)

    if resultado:
        st.success("✅ Cálculo completado con éxito.")
        st.markdown(f"""
        - **Entradas**: {resultado['entradas']}
        - **Lote por entrada**: `{resultado['lote']}`
        - **Rango de precios**: `{resultado['rango'][0]} → {resultado['rango'][1]}`
        - **Breakeven**: `{resultado['breakeven']}`
        - **Precio liquidación (10% contra)**: `{resultado['liquidacion']}`
        - **Margen total usado**: `${resultado['margen_usado']}`
        - **Pérdida estimada si llega a liquidación**: `${resultado['perdida_total']}`
        """)
    else:
        st.error("❌ No se encontró un lote seguro con esos parámetros.")