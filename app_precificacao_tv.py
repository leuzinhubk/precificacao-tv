import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from io import BytesIO

st.set_page_config(page_title="Precificação TV Quebrada", layout="wide")
st.title("📺 Precificação TV Quebrada")

pecas = ["Placa Principal", "Placa Fonte", "Placa T-CON"]
valores, fretes, custos_adicionais = [], [], []

st.header("1️⃣ Valores das peças e custos")
for p in pecas:
    valores.append(st.number_input(f"Valor de venda {p} (R$):", min_value=0, value=100))
    fretes.append(st.number_input(f"Frete {p} (R$):", min_value=0, value=25))
    custos_adicionais.append(st.number_input(f"Custo adicional {p} (R$):", min_value=0, value=0))

comissao_pct = st.number_input("Percentual de comissão ML (%):", min_value=0, max_value=100, value=18)/100
nota_pct = st.number_input("Percentual de nota fiscal (%):", min_value=0, max_value=100, value=10)/100
margem_seg = 0.8  # 80% fixo

df = pd.DataFrame({
    "Peça": pecas,
    "Valor Venda": valores,
    "Frete": fretes,
    "Custo Adicional": custos_adicionais
})
df["Comissão (R$)"] = df["Valor Venda"] * comissao_pct
df["Imposto (R$)"] = df["Valor Venda"] * nota_pct
df["Custo Total"] = df["Frete"] + df["Comissão (R$)"] + df["Imposto (R$)"] + df["Custo Adicional"]
df["Lucro Líquido"] = df["Valor Venda"] - df["Custo Total"]
df["Markup"] = df["Valor Venda"] / df["Custo Total"]

lucro_total = df["Lucro Líquido"].sum()
valor_max_tv = lucro_total * (1 - margem_seg)
lucro_real = lucro_total - valor_max_tv

st.header("2️⃣ Resultados")
st.dataframe(df.style.format("{:.2f}"))
st.subheader("Resumo Geral")
st.write(f"💰 Lucro líquido total: R$ {lucro_total:.2f}")
st.write(f"⚠️ Valor máximo que posso pagar pela TV (margem segurança 80%): R$ {valor_max_tv:.2f}")
st.write(f"✅ Lucro real após pagar a TV: R$ {lucro_real:.2f}")

st.header("3️⃣ Dashboard Gráfico")
fig, ax = plt.subplots()
ax.bar(df["Peça"], df["Lucro Líquido"], color='green')
ax.set_ylabel("Lucro Líquido (R$)")
ax.set_title("Lucro Líquido por Peça")
st.pyplot(fig)

fig2, ax2 = plt.subplots()
ax2.bar(df["Peça"], df["Valor Venda"], color='blue', label="Valor Venda")
ax2.bar(df["Peça"], df["Custo Total"], color='red', alpha=0.6, label="Custo Total")
ax2.set_ylabel("R$")
ax2.set_title("Valor Venda x Custo Total")
ax2.legend()
st.pyplot(fig2)

st.header("4️⃣ Exportar resultados")
def to_excel(df):
    output = BytesIO()
    writer = pd.ExcelWriter(output, engine='xlsxwriter')
    df.to_excel(writer, index=False, sheet_name='Precificacao')
    writer.save()
    processed_data = output.getvalue()
    return processed_data

excel_data = to_excel(df)
st.download_button(label="📥 Baixar Excel", data=excel_data, file_name="Precificacao_TV.xlsx")
