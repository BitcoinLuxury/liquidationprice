import streamlit as st

# Pares de divisas disponibles
PARES = [
    'AUD/CAD', 'AUD/CHF', 'AUD/JPY', 'AUD/NZD', 'AUD/USD',
    'CAD/CHF', 'CAD/JPY',
    'CHF/JPY',
    'EUR/AUD', 'EUR/CAD', 'EUR/CHF', 'EUR/GBP', 'EUR/JPY', 'EUR/NZD', 'EUR/USD',
    'GBP/AUD', 'GBP/CAD', 'GBP/CHF', 'GBP/JPY', 'GBP/NZD', 'GBP/USD',
    'NZD/CAD', 'NZD/CHF', 'NZD/JPY', 'NZD/USD',
    'USD/CAD', 'USD/CHF', 'USD/JPY'
]

def calcular_dca(balance, precio_inicial, precio_final, tipo, par):
    entradas = 8
    apalancamiento = 500
    lote = 1.0
    paso_lote = 0.01
    lote_aceptable = 0.0

    # Calcular precios de entrada
    distancia_total = abs(precio_final - precio_inicial)
    paso_precio = distancia_total / (entradas - 1)
    precios = [
        precio_inicial + i * paso_precio * (-1 if tipo == 'buy' else 1)
        for i in range(entradas)
    ]

    # Calcular precio de liquidación a partir de precio final
    if tipo == 'buy':
        precio_liquidacion = precio_final - (precio_final * 0.10)
    else:
        precio_liquidacion = precio_final + (precio_final * 0.10)

    # Estimar valor del pip (para USD cuentas)
    pip_size = 0.0001 if 'JPY' not in par else 0.01
    pip_value = 10 if 'JPY' not in par else 100000 * pip_size / precio_final

    while lote > 0:
        # Calcular margen total
        margen_total = sum((p * 100000 * lote) / apalancamiento for p in precios)
        if margen_total > balance:
            lote -= paso_lote
            continue

        # Calcular pérdida total si el precio cae a liquidación
        perdidas = []
        for p in precios:
            pips_perdidos = abs(p - precio_liquidacion) / pip_size
            perdida = pips_perdidos * pip_value * lote
            perdidas.append(perdida)
        perdida_total = sum(perdidas)

        if perdida_total <= balance:
            lote_aceptable = lote
            break

        lote -= paso_lote

    if lote_aceptable == 0.0:
        return None

    # Recalcular valores finales con lote encontrado
    total_cost = sum(p * lote_aceptable for p in precios)
    breakeven = total_cost / (lote_aceptable * entradas)
    margen_total = sum((p * 100000 * lote_aceptable) / apalancamiento for p in precios)
    perdidas = []
    for p in precios:
        pips_perdidos = abs(p - precio_liquidacion) / pip_size
        perdida = pips_perdidos * pip_value * lote_aceptable
        perdidas.append(perdida)
    perdida_total = sum(perdidas)

    return {
        'entradas': entradas,
        'lote': round(lote_aceptable, 2),
        'rango': (round(precios[-1], 5), round(precios[0], 5)),
        'breakeven': round(breakeven, 5),
        'liquidacion': round(precio_liquidacion, 5),
        'perdida_total': round(perdida_total, 2),
        'margen_usado': round(margen_total, 2),
        'precios': [round(p, 5) for p in precios]
    }

# Interfaz de usuario con Streamlit
st.set_page_config(page_title="DCA Forex 1:500", layout="centered")
st.title("📊 Calculadora DCA Forex (1:500)")
tab1, tab2 = st.tabs(["🧮 Calculadora", "💱 Pares de Forex"])

with tab2:
    st.markdown("### Pares disponibles")
    st.write(", ".join(PARES))
    st.markdown("Usamos un apalancamiento de 1:500. El precio de liquidación se calcula con un margen de seguridad del 10% adicional desde el precio final del rango.")

with tab1:
    with st.form("form"):
        par = st.selectbox("💱 Par de divisas", PARES, index=0)
        balance = st.number_input("💰 Balance (USD)", min_value=1.0, value=5000.0)
        precio_inicial = st.number_input("📈 Precio inicial", value=1.1800, format="%.5f")
        precio_final = st.number_input("📉 Precio final", value=1.0100, format="%.5f")
        tipo = st.selectbox("🟩 Tipo de operación", ["buy", "sell"])
        btn = st.form_submit_button("📐 Calcular")

    if btn:
        resultado = calcular_dca(balance, precio_inicial, precio_final, tipo, par)
        if resultado:
            st.success("✅ Cálculo exitoso.")
            st.markdown(f"""
            - **Par:** `{par}`
            - **Tipo:** `{tipo.upper()}`
            - **Entradas:** {resultado['entradas']}
            - **Lote por entrada:** `{resultado['lote']}`
            - **Precios de entrada:** `{resultado['precios']}`
            - **Rango:** {resultado['rango'][0]} → {resultado['rango'][1]}
            - **Break-even:** `{resultado['breakeven']}`
            - **Precio de liquidación:** `{resultado['liquidacion']}`
            - **Pérdida total si cae a liquidación:** `${resultado['perdida_total']}`
            - **Margen total requerido:** `${resultado['margen_usado']}`
            """)
        else:
            st.error("❌ No se encontró un lote seguro que cumpla con el margen y el nivel de liquidación.")
