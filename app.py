import streamlit as st

# Listado de pares
PARES = [
    'EUR/USD', 'GBP/USD', 'USD/JPY', 'USD/CHF',
    'AUD/USD', 'NZD/USD', 'EUR/GBP', 'EUR/JPY',
    'GBP/JPY', 'USD/CAD', 'CAD/JPY'
]

def calcular_dca(balance, precio_inicial, precio_final, tipo, par):
    entradas = 8
    apalancamiento = 500

    # Pip value estimado (USD) estándar
    pip_value = 10 if 'JPY' not in par else 100000 * 0.0001 / precio_final

    # Calcular precios y lotaje
    distancia_total = abs(precio_final - precio_inicial)
    paso = distancia_total / (entradas - 1)
    precios = [
        precio_inicial + i * paso * (-1 if tipo == 'buy' else 1)
        for i in range(entradas)
    ]

    lote = 1.0
    paso_lote = 0.01
    lote_aceptable = 0.0

    while lote > 0:
        margenes = [(p * 100000) / apalancamiento * lote for p in precios]
        margen_total = sum(margenes)
        if margen_total > balance:
            lote -= paso_lote
            continue

        total_cost = sum(precio * lote for precio in precios)
        breakeven = total_cost / (lote * entradas)

        # Liquidación = precio_final ± 10%
        liqui = precio_final * (0.9 if tipo == 'buy' else 1.1)
        pips_contra = abs(breakeven - liqui) / (0.0001 if 'JPY' not in par else 0.01)
        perdida = pips_contra * lote * pip_value

        if perdida <= balance:
            lote_aceptable = lote
            liquidacion = liqui
            break

        lote -= paso_lote

    if lote_aceptable == 0.0:
        return None

    # Recalcular para salidas
    margen_total = sum((p * 100000) / apalancamiento * lote_aceptable for p in precios)
    total_cost = sum(precio * lote_aceptable for precio in precios)
    breakeven = total_cost / (lote_aceptable * entradas)
    liquidacion = precio_final * (0.9 if tipo == 'buy' else 1.1)
    pips_contra = abs(breakeven - liquidacion) / (0.0001 if 'JPY' not in par else 0.01)
    perdida_total = pips_contra * lote_aceptable * pip_value

    return {
        'entradas': entradas,
        'lote': round(lote_aceptable, 2),
        'rango': (round(precios[-1], 5), round(precios[0], 5)),
        'breakeven': round(breakeven, 5),
        'liquidacion': round(liquidacion, 5),
        'perdida_total': round(perdida_total, 2),
        'margen_usado': round(margen_total, 2)
    }

# Interfaz
st.set_page_config(page_title="DCA Forex 1:500", layout="centered")
st.title("📊 Calculadora DCA Forex (1:500)")
tab1, tab2 = st.tabs(["🧮 Calculadora", "💱 Pares de Forex"])

with tab2:
    st.markdown("### Pares disponibles")
    st.write(", ".join(PARES))
    st.markdown("El margen por lote se calcula dinámicamente según IC Markets.")

with tab1:
    with st.form("form"):
        par = st.selectbox("💱 Par de divisas", PARES, index=0)
        balance = st.number_input("💰 Balance (USD)", min_value=1.0, value=5000.0)
        precio_inicial = st.number_input("📈 Precio inicial", value=1.1800, format="%.5f")
        precio_final = st.number_input("📉 Precio final", value=1.0100, format="%.5f")
        tipo = st.selectbox("🟩 Tipo", ["buy", "sell"])
        btn = st.form_submit_button("📐 Calcular")

    if btn:
        res = calcular_dca(balance, precio_inicial, precio_final, tipo, par)
        if res:
            st.success("✅ Cálculo completado.")
            st.markdown(f"""
            - **Par**: {par}
            - **Entradas**: {res['entradas']}
            - **Lote por entrada**: {res['lote']}
            - **Rango**: {res['rango'][0]} → {res['rango'][1]}
            - **Break‑even**: {res['breakeven']}
            - **Liquidación estimada** (±10% del final): {res['liquidacion']}
            - **Margen usado**: ${res['margen_usado']}
            - **Pérdida estimada** en liquidación: ${res['perdida_total']}
            """)
        else:
            st.error("❌ No se encontró un lote seguro con esos parámetros.")
