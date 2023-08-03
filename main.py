import pandas as pd
from google.oauth2 import service_account
import streamlit as st


credenciais = service_account.Credentials.from_service_account_info(
    {
  "type": st.secrets['type'],
  "project_id": st.secrets['project_id'],
  "private_key_id": st.secrets['private_key_id'],
  "private_key": st.secrets['private_key'],
  "client_email": st.secrets['client_email'],
  "client_id": st.secrets['client_id'],
  "auth_uri": st.secrets['auth_uri'],
  "token_uri": st.secrets['token_uri'],
  "auth_provider_x509_cert_url": st.secrets['auth_provider_x509_cert_url'],
  "client_x509_cert_url": st.secrets['client_x509_cert_url'],
  "universe_domain": st.secrets['universe_domain']
    }
)


def ano():
    ano = st.sidebar.slider('Ano', 1994, 2022, step=2)
    return ano


@st.cache_data
def ufs(ano):
    ufs = f'''
        SELECT sigla_uf.sigla_uf
        FROM sigla_uf.sigla_uf
        WHERE ano = {ano} AND sigla_uf IS NOT NULL    
    '''
    df = pd.read_gbq(query=ufs, credentials=credenciais)
    return df


@st.cache_data
def receita_por_todas_uf(ano):
    receita_por_todas_uf = f'''
        SELECT sigla_uf, ROUND(AVG(valor_receita), 2) AS Receita_Media, ROUND(SUM(valor_receita), 2) AS Total_Receita
        FROM basedosdados.br_tse_eleicoes.receitas_candidato
        WHERE ano = {ano} AND sigla_uf IS NOT NULL
        GROUP BY sigla_uf
        ORDER BY Receita_Media DESC;
    '''
    df = pd.read_gbq(query=receita_por_todas_uf, credentials=credenciais)
    return df


@st.cache_data
def receita_por_uf(ano, opcoes):
    receita_por_uf = f'''
        SELECT sigla_uf, ROUND(AVG(valor_receita), 2) AS Receita_Media, ROUND(SUM(valor_receita), 2) AS Total_Receita
        FROM basedosdados.br_tse_eleicoes.receitas_candidato
        WHERE ano = {ano} AND sigla_uf IS NOT NULL AND sigla_uf IN ({opcoes})
        GROUP BY sigla_uf
        ORDER BY Receita_Media DESC, Total_Receita DESC;
    '''
    df = pd.read_gbq(query=receita_por_uf, credentials=credenciais)
    return df


st.title('Análise das Eleições')
filtro = st.sidebar.selectbox(label='Análises', options=['Receita por Estado', 'Receita por Partido', 'Cargos', 'Candidatos'])
ano = ano()
if filtro == 'Receita por Estado':
    filtrar_uf = st.sidebar.multiselect(label='Escolha os Estados', options=[uf[1]['sigla_uf'] for uf in ufs(ano).iterrows()])
    if filtrar_uf:
        col1, col2 = st.columns(2)
        valores_aspas = [f"'{valor}'" for valor in filtrar_uf]
        ufs = ', '.join(valores_aspas)
        col1.subheader('Receita Média por Estado')
        col1.bar_chart(receita_por_uf(ano, ufs), y='Receita_Media', x='sigla_uf')
        col2.subheader('Total de Receita por Estado')
        col2.line_chart(receita_por_uf(ano, ufs), y='Total_Receita', x='sigla_uf')
    else:
        st.subheader('Receita Média por Estado')
        tabela_todas_ufs = st.checkbox('Tabela')
        if tabela_todas_ufs:
            st.table(receita_por_todas_uf(ano))
        else:
            st.bar_chart(receita_por_todas_uf(ano), y='Receita_Media', x='sigla_uf')
