# app_precificacao_tv.py
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from io import BytesIO
import base64
import datetime

# ---------- Config ----------
st.set_page_config(page_title="Video e Cia · Precificação Pro", layout="wide")
COMPANY_NAME = "Video e Cia"
MARGEM_SEG = 0.8  # 80% fixo

# ---------- Cabeçalho / Branding ----------
st.markdown(
    f"""
    <div style="display:flex; align-items:center; gap:16px;">
      <div style="font-weight:700; font-size:20px;">📺 {COMPANY_NAME} — Precificação Pro</div>
      <div style="color:gray; font-size:13px;">{datetime.datetime.now().strftime('%d/%m/%Y %H:%M')}</div>
    </div>
    <hr/>
    """,
    unsafe_allow_html=True,
)

# ---------- Entradas (ordem: mais importantes primeiro) ----------
st.header("1️⃣ Insira valores (preencha os campos mais importantes primeiro)")

col1, col2 = st.columns([1, 1])

with col1:
    vp_plc = st.number_input("Valor venda — Placa Principal (R$)", min_value=0.0, value=150.00, step=1.0, format="%.2f")
    vp_font = st.number_input("Valor venda — Placa Fonte (R$)", min_value=0.0, value=100.00, step=1.0, format="%.2f")
    vp_tcon = st.number_input("Valor venda — Placa T-CON (R$)", min_value=0.0, value=40.00, step=1.0, format="%.2f")

with col2:
    vp_led = st.number_input("Valor venda — Barras de LED (R$)", min_value=0.0, value=0.00, step=1.0, format="%.2f")
    # Fretes por peça
    st.markdown("**Frete por peça (R$)**")
    fr_plc = st.number_input("Frete — Placa Principal (R$)", min_value=0.0, value=25.00, step=0.5, format="%.2f")
    fr_font = st.number_input("Frete — Placa Fonte (R$)", min_value=0.0, value=20.00, step=0.5, format="%.2f")
    fr_tcon = st.number_input("Frete — Placa T-CON (R$)", min_value=0.0, value=15.00, step=0.5, format="%.2f")
    fr_led = st.number_input("Frete — Barras de LED (R$)", min_value=0.0, value=25.00, step=0.5, format="%.2f")

st.markdown("---")

# custos adicionais opcionais
st.header("2️⃣ Custos opcionais / Percentuais")
col3, col4 = st.columns([1, 1])
with col3:
    cad_plc = st.number_input("Custo adicional — Placa Principal (R$)", min_value=0.0, value=0.0, format="%.2f")
    cad_font = st.number_input("Custo adicional — Placa Fonte (R$)", min_value=0.0, value=0.0, format="%.2f")
with col4:
    cad_tcon = st.number_input("Custo adicional — Placa T-CON (R$)", min_value=0.0, value=0.0, format="%.2f")
    cad_led = st.number_input("Custo adicional — Barras de LED (R$)", min_value=0.0, value=0.0, format="%.2f")

# percentuais
st.markdown("**Taxas e percentuais**")
pct_col1, pct_col2 = st.columns([1, 1])
with pct_col1:
    comissao_pct = st.number_input("Comissão MercadoLivre (%)", min_value=0.0, max_value=100.0, value=18.0, format="%.2f") / 100.0
with pct_col2:
    nota_pct = st.number_input("Nota/Imposto (%)", min_value=0.0, max_value=100.0, value=10.0, format="%.2f") / 100.0

st.markdown("---")

# ---------- Cálculo (por peça) ----------
pecas = ["Placa Principal", "Placa Fonte", "Placa T-CON", "Barras de LED"]
valores = [vp_plc, vp_font, vp_tcon, vp_led]
fretes = [fr_plc, fr_font, fr_tcon, fr_led]
custos_ad = [cad_plc, cad_font, cad_tcon, cad_led]

try:
    df = pd.DataFrame({
        "Peça": pecas,
        "Valor Venda (R$)": valores,
        "Frete (R$)": fretes,
        "Custo Adicional (R$)": custos_ad
    })

    # cálculos por peça
    df["Comissão (R$)"] = (df["Valor Venda (R$)"] * comissao_pct).round(2)
    df["Imposto (R$)"] = (df["Valor Venda (R$)"] * nota_pct).round(2)
    df["Custo Total (R$)"] = (df["Frete (R$)"] + df["Comissão (R$)"] + df["Imposto (R$)"] + df["Custo Adicional (R$)"]).round(2)
    df["Lucro Líquido (R$)"] = (df["Valor Venda (R$)"] - df["Custo Total (R$)"]).round(2)
    # evitar divisão por zero
    df["Markup"] = df.apply(lambda r: float('inf') if r["Custo Total (R$)"] == 0 else round(r["Valor Venda (R$)"] / r["Custo Total (R$)"], 2), axis=1)

    # totais
    lucro_total = df["Lucro Líquido (R$)"].sum().round(2)
    valor_max_tv = round(lucro_total * (1 - MARGEM_SEG), 2)
    lucro_real = round(lucro_total - valor_max_tv, 2)
except Exception as e:
    st.error("Erro ao calcular — verifique entradas. Detalhe: " + str(e))
    raise

# ---------- Mostrar tabela (sem usar Styler que pode quebrar em alguns ambientes) ----------
st.header("3️⃣ Tabela de resultados (por peça)")
# usar st.table ou st.dataframe com valores já arredondados
st.dataframe(df, use_container_width=True)

# ---------- Resumo destacado ----------
st.header("4️⃣ Resumo")
col_r1, col_r2, col_r3 = st.columns([1,1,1])
col_r1.metric("Lucro líquido total (R$)", f"{lucro_total:,.2f}")
col_r2.metric("Valor máximo p/ pagar TV (R$)", f"{valor_max_tv:,.2f}")
col_r3.metric("Lucro real após pagar TV (R$)", f"{lucro_real:,.2f}")

st.markdown("---")

# ---------- Gráficos ----------
st.header("5️⃣ Gráficos")

fig, ax = plt.subplots()
ax.bar(df["Peça"], df["Lucro Líquido (R$)"])
ax.set_ylabel("Lucro Líquido (R$)")
ax.set_title("Lucro líquido por peça")
st.pyplot(fig, use_container_width=True)

fig2, ax2 = plt.subplots()
x = df["Peça"]
ax2.bar(x, df["Valor Venda (R$)"], label="Valor Venda")
ax2.bar(x, df["Custo Total (R$)"], label="Custo Total", alpha=0.7)
ax2.set_title("Valor Venda x Custo Total")
ax2.legend()
st.pyplot(fig2, use_container_width=True)

st.markdown("---")

# ---------- Exportar Excel ----------
st.header("6️⃣ Exportar / Relatório")
def to_excel_bytes(df_table):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df_table.to_excel(writer, index=False, sheet_name='Precificacao')
        # formatação simples
        workbook  = writer.book
        worksheet = writer.sheets['Precificacao']
        money_fmt = workbook.add_format({'num_format': 'R$#,##0.00'})
        worksheet.set_column('B:B', 18, money_fmt)
        worksheet.set_column('C:C', 12, money_fmt)
        worksheet.set_column('D:D', 18, money_fmt)
        worksheet.set_column('E:E', 12, money_fmt)
        worksheet.set_column('F:F', 12, money_fmt)
        worksheet.set_column('G:G', 16, money_fmt)
    return output.getvalue()

excel_data = to_excel_bytes(df)
st.download_button("📥 Baixar relatório Excel", excel_data, file_name="precificacao_videoecia.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

# ---------- Histórico (simples, local na sessão) ----------
if 'historico' not in st.session_state:
    st.session_state['historico'] = []
if st.button("Salvar orçamento no histórico (esta sessão)"):
    record = {
        "data": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "lucro_total": float(lucro_total),
        "valor_max_tv": float(valor_max_tv),
        "lucro_real": float(lucro_real)
    }
    st.session_state['historico'].append(record)
    st.success("Orçamento salvo no histórico da sessão.")

if st.session_state['historico']:
    st.markdown("**Histórico (sessão atual)**")
    st.table(pd.DataFrame(st.session_state['historico']))

st.markdown("<div style='color:gray; font-size:12px;'>Video e Cia · Precificação Pro — ferramenta interna. Verifique impostos locais com seu contador.</div>", unsafe_allow_html=True)
