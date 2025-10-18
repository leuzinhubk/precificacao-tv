# app_precificacao_tv.py
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from io import BytesIO
import datetime
import os

# ---------- Config ----------
st.set_page_config(page_title="Video e Cia · Precificação Premium", layout="wide")
COMPANY_NAME = "Video e Cia"
MARGEM_SEG = 0.8  # 80% fixo

# ---------- Histórico CSV ----------
HIST_FILE = "historico_precificacao.csv"
if not os.path.exists(HIST_FILE):
    pd.DataFrame(columns=["Data","TV","Peça","Valor Venda","Frete","Custo Adicional","Comissão","Imposto","Custo Total","Lucro Líquido","Markup"]).to_csv(HIST_FILE, index=False)

# ---------- Cabeçalho ----------
st.markdown(f"<h1 style='color:#1E90FF;'>📺 {COMPANY_NAME} — Precificação Super Premium</h1><hr>", unsafe_allow_html=True)

# ---------- Entradas ----------
st.header("1️⃣ Valores das peças")
tv_nome = st.text_input("Nome/Modelo da TV", "TV Quebrada Exemplo")

# Função para linha de peça apenas com valor de venda
def linha_peca(nome, valor_default):
    col1, col2 = st.columns([3,1])
    with col1:
        st.text(f"{nome}")
    with col2:
        vp = st.number_input(f"💰 Valor venda — {nome} (R$)", min_value=0.0, value=valor_default, key=f"vp_{nome}")
    return vp

# Lista de peças
pecas_lista = [
    ("Placa Principal", 150.0),
    ("Placa Fonte", 100.0),
    ("Placa T-CON", 40.0),
    ("Barras de LED", 0.0)
]

# Coletando valores
valores = []
for nome, val_default in pecas_lista:
    vp = linha_peca(nome, val_default)
    valores.append(vp)

# ---------- Custos adicionais ----------
st.header("2️⃣ Custos adicionais")
cad_total = st.number_input("Custo adicional total (R$)", min_value=0.0, value=0.0)

# ---------- Fretes ----------
st.header("3️⃣ Fretes das peças")
frete_plc = st.number_input("Frete da Placa Principal (R$)", min_value=0.0, value=25.0)
frete_font = st.number_input("Frete da Placa Fonte (R$)", min_value=0.0, value=20.0)
frete_tcon = st.number_input("Frete da Placa T-CON (R$)", min_value=0.0, value=15.0)
frete_led = st.number_input("Frete da Barras de LED (R$)", min_value=0.0, value=25.0)

fretes = [frete_plc, frete_font, frete_tcon, frete_led]

# ---------- Taxas ----------
st.header("4️⃣ Taxas (%)")
colp1, colp2 = st.columns(2)
with colp1:
    comissao_pct = st.number_input("Comissão MercadoLivre (%)", min_value=0.0, max_value=100.0, value=18.0)/100
with colp2:
    nota_pct = st.number_input("Nota/Imposto (%)", min_value=0.0, max_value=100.0, value=10.0)/100

# ---------- Cálculos ----------
pecas = [x[0] for x in pecas_lista]

df = pd.DataFrame({
    "Peça": pecas,
    "Valor Venda": valores,
    "Frete": fretes,
})

# Adiciona Custo adicional igual para todas as peças
df["Custo Adicional"] = cad_total / len(df)  # divide igualmente entre as peças

df["Comissão"] = (df["Valor Venda"]*comissao_pct).round(2)
df["Imposto"] = (df["Valor Venda"]*nota_pct).round(2)
df["Custo Total"] = (df["Frete"] + df["Comissão"] + df["Imposto"] + df["Custo Adicional"]).round(2)
df["Lucro Líquido"] = (df["Valor Venda"] - df["Custo Total"]).round(2)
df["Markup"] = df.apply(lambda r: float('inf') if r["Custo Total"]==0 else round(r["Valor Venda"]/r["Custo Total"],2), axis=1)

# Totais
lucro_total = df["Lucro Líquido"].sum().round(2)
valor_max_tv = round(lucro_total*(1-MARGEM_SEG),2)
lucro_real = round(lucro_total - valor_max_tv,2)

# ---------- Mostrar tabela ----------
st.header("5️⃣ Resultados por peça")
st.dataframe(df, use_container_width=True)

# ---------- Resumo ----------
st.header("6️⃣ Resumo")
col_r1,col_r2,col_r3 = st.columns(3)
col_r1.metric("Lucro líquido total (R$)", f"{lucro_total:,.2f}")
col_r2.metric("Valor máximo p/ pagar TV (R$)", f"{valor_max_tv:,.2f}")
col_r3.metric("Lucro real após pagar TV (R$)", f"{lucro_real:,.2f}")

# Alertas visuais
if valor_max_tv > 50:
    st.warning("⚠️ Cuidado: valor máximo para a TV está alto!")
if lucro_total < 0:
    st.error("❌ Lucro líquido negativo!")

# ---------- Gráfico compacto ----------
st.header("7️⃣ Gráficos interativos")
fig = go.Figure()
fig.add_trace(go.Bar(x=df["Peça"], y=df["Lucro Líquido"], name="Lucro Líquido", marker_color="green"))
fig.add_trace(go.Bar(x=df["Peça"], y=df["Custo Total"], name="Custo Total", marker_color="red"))
fig.add_trace(go.Bar(x=df["Peça"], y=df["Valor Venda"], name="Valor Venda", marker_color="blue", opacity=0.6))
fig.update_layout(
    title="Comparativo Valor Venda × Custo Total × Lucro",
    barmode="group",
    xaxis_title="Peça",
    yaxis_title="R$ (Reais)",
    width=800,
    height=400
)
st.plotly_chart(fig, use_container_width=False)

# ---------- Exportar Excel ----------
st.header("8️⃣ Exportar relatório Excel")
def to_excel_bytes(df_table):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df_table.to_excel(writer,index=False,sheet_name='Precificacao')
        workbook = writer.book
        worksheet = writer.sheets['Precificacao']
        money_fmt = workbook.add_format({'num_format':'R$#,##0.00'})
        worksheet.set_column('B:B',18,money_fmt)
        worksheet.set_column('C:C',12,money_fmt)
        worksheet.set_column('D:D',12,money_fmt)
        worksheet.set_column('E:E',12,money_fmt)
        worksheet.set_column('F:F',16,money_fmt)
    return output.getvalue()

excel_data = to_excel_bytes(df)
st.download_button("📥 Baixar relatório Excel", excel_data, file_name="precificacao_videoecia.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

# ---------- Histórico persistente ----------
st.header("9️⃣ Histórico de orçamentos")
if st.button("Salvar orçamento"):
    df_hist = df.copy()
    df_hist.insert(0,"Data",datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    df_hist.insert(1,"TV", tv_nome)
    df_hist.to_csv(HIST_FILE, mode="a", header=False,index=False)
    st.success("Orçamento salvo com sucesso!")

df_hist_all = pd.read_csv(HIST_FILE)
st.dataframe(df_hist_all, use_container_width=True)

st.markdown("<div style='color:gray; font-size:12px;'>Video e Cia · Super Premium — ferramenta interna.</div>", unsafe_allow_html=True)
