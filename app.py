import streamlit as st

# === Datos básicos por par de divisas ===
# pip_value y margen_por_lote se expresan por 1 lote estándar (100,000 unidades)
PARES = {
    'EUR/USD': {'pip_value': 10.0, 'margen_por_lote': 200.0},
    'GBP/USD': {'pip_value': 10.0, 'margen_por_lote': 200.0},
    'USD/JPY': {'pip_value': 9.13, 'margen_por_lote': 200.0},
    'USD/CHF': {'pip_value': 10.27, 'margen_por_lote': 200.0},
    'AUD/USD': {'pip_value': 10.0, 'margen_por_lote': 200.0},
    'NZD/USD': {'pip_value': 10.0, 'margen_por_lote': 200.0},
    'EUR/GBP': {'pip_value': 11.76, 'margen_por_lote': 200.0},
    'EUR/JPY': {'pip_value': 9.1, 'margen_por_lote': 200.0},
    'GBP/JPY': {'pip_value': 8.63, 'margen_por_lote': 200.0},
    'USD/CAD': {'pip_value': 7.93, 'margen_por_lote': 200.0},
    'CAD/JPY': {'pip_value': 7.8, 'margen_por_lote': 200.0},
    # Puedes agregar más...
}


def calcular_dca(balance, precio_inicial, precio_final, tipo, par):
    entradas = 8
    apalancamiento = 500
    pip_value = PARES[par]['pip_value']
    margen_por_lote = PARES[par]['margen_por_lote']

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
        perdida_total = pips_contra * lote * entradas * pip_value

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
    perdida_total = pips_contra * lote_aceptable * entradas * pip_value
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


# === INTERFAZ STREAMLIT ===
st.set_page_config(page_title="Calculadora DCA Forex", layout="centered")

st.title("📊 Calculadora DCA Forex (1:500)")
st.markdown("Simula entradas DCA con margen ajustado por par. Precio de liquidación a 10% contra breakeven.")

tab1, tab2 = st.tabs(["🧮 Calculadora", "💱 Pares de Forex"])

with tab2:
    st.markdown("### Pares disponibles (Majors y Minors)")
    for pair, data in PARES.items():
        st.write(f"- **{pair}** → Pip: ${data['pip_value']}/lote | Margen estimado: ${data['margen_por_lote']}")

with tab1:
    with st.form("formulario_dca"):
        par = st.selectbox("💱 Selecciona el par", options=list(PARES.keys()), index=0)
        balance = st.number_input("💰 Balance de la cuenta (USD)", min_value=1.0, value=5000.0)
        precio_inicial = st.number_input("📈 Precio inicial", value=1.1800, format="%.5f")
        precio_final = st.number_input("📉 Precio final", value=1.0100, format="%.5f")
        tipo = st.selectbox("🟩 Tipo de operación", options=["buy", "sell"])

        calcular = st.form_submit_button("📐 Calcular")

    if calcular:
        resultado = calcular_dca(balance, precio_inicial, precio_final, tipo, par)

        if resultado:
            st.success("✅ Cálculo completado con éxito.")
            st.markdown(f"""
            - **Par**: `{par}`
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
