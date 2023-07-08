import os
import requests
import zipfile
import pandas as pd
from io import BytesIO
import matplotlib.pyplot as plt
import streamlit as st

# URL base para os arquivos
base_url = "https://dados.cvm.gov.br/dados/FIDC/DOC/INF_MENSAL/DADOS/"

# Anos e meses para baixar
anos = range(2019, 2023)
meses = range(1, 13)

# Lista para armazenar os dataframes
dataframes = []

for ano in anos:
    for mes in meses:
        # Formato do arquivo é inf_mensal_fidc_YYYYMM.zip
        filename = f"inf_mensal_fidc_{ano}{mes:02}.zip"
        url = base_url + filename

        # Verifique se o arquivo já foi baixado
        if not os.path.exists(filename):
            print(f"Baixando {url}...")
            response = requests.get(url)
            with open(filename, "wb") as f:
                f.write(response.content)

        # Extraia o arquivo CSV específico do arquivo ZIP
        with zipfile.ZipFile(filename, 'r') as zip_ref:
            csv_file = f"inf_mensal_fidc_tab_V_{ano}{mes:02}.csv"
            try:
                df = pd.read_csv(zip_ref.open(csv_file), sep=';', encoding='ISO-8859-1')  # use 'ISO-8859-1' encoding
                dataframes.append(df)
            except KeyError:
                print(f"{csv_file} não está em {filename}")

# Concatene todos os dataframes
df_concat = pd.concat(dataframes, ignore_index=True)

# Obter uma lista de todos os fundos
fundos = df_concat['CNPJ_FUNDO'].unique()

# Criar um menu de seleção de fundos
fundo_selecionado = st.selectbox('Selecione um fundo', fundos)

# Filtrar o DataFrame para incluir apenas o fundo selecionado
df_fundo = df_concat[df_concat['CNPJ_FUNDO'] == fundo_selecionado]

# Análise: evolução dos valores de TAB_V_A* ao longo do tempo
tab_v_a_cols = [col for col in df_fundo.columns if 'TAB_V_A' in col]
df_fundo['DT_COMPTC'] = pd.to_datetime(df_fundo['DT_COMPTC'])
df_fundo.set_index('DT_COMPTC')[tab_v_a_cols].resample('M').sum().plot()

# Configurar o gráfico
plt.title('Evolução dos valores de TAB_V_A* ao longo do tempo')
plt.xlabel('Data')
plt.ylabel('Valor')
plt.legend(tab_v_a_cols, loc='upper left')

# Mostrar o gráfico no aplicativo Streamlit
st.pyplot(plt)
