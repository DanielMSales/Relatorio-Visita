app_veolia.py
import streamlit as st
import pandas as pd
import json # Para lidar com a estrutura de dados de equipamentos
from datetime import date

st.set_page_config(layout="wide", page_title="Relatório Veolia - Checklist Profissional")

# --- Estilo CSS para uma "pegada" visual mais próxima ---
st.markdown("""
    <style>
    .reportview-container .main .block-container {
        max-width: 900px;
        padding-top: 2rem;
        padding-right: 1rem;
        padding-left: 1rem;
        padding-bottom: 2rem;
    }
    .veolia-card {
        background:#fff;
        border-radius:22px;
        box-shadow:0 4px 16px rgba(179,0,0,0.08); /* #b3000015 */
        margin-bottom:26px;
        padding:30px 18px 38px 18px;
        border:2px solid #e2e2e7;
    }
    header {
        display:flex;
        align-items:center;
        gap:16px;
        padding-bottom:20px;
    }
    .logo {
        height:48px;
    }
    .title-main {
        font-size:2rem;
        font-weight:900;
        color:#b30000;
        margin-left: 10px;
    }
    label {
        font-weight:700;
        font-size:1rem;
        margin-top:7px;
        display:block;
    }
    .stTextInput>div>div>input, .stDateInput>div>div>input, .stSelectbox>div>div>select, .stTextArea>div>div>textarea {
        width:100%;
        padding:11px 8px;
        border-radius:7px;
        border:2px solid #dadada;
        font-size:1.05rem;
        margin-bottom:10px;
        background:#fff;
    }
    .equipamento {
        background: #faf9fb;
        border-radius: 12px;
        box-shadow: 0 2px 12px rgba(179,0,0,0.07); /* #b3000012 */
        padding: 16px;
        margin-bottom: 18px;
        border:1.5px solid #e2e2e2;
        position:relative;
    }
    .produto-quimico-card {
        background:#f8fafd;
        padding:8px 8px 8px 8px;
        margin:7px 0 10px 0;
        border-radius:8px;
        box-shadow:0 1px 8px rgba(23,99,173,0.07); /* #1763ad11 */
        border:1px solid #e1e8f0;
        position:relative;
    }
    .param-row {
        display:flex;
        flex-wrap:wrap;
        gap:6px 8px;
        align-items:center;
        margin-bottom:7px;
    }
    .stCheckbox label {
        display: flex;
        align-items: center;
        background:#ffe6e6;
        padding:10px 14px;
        border-radius:9px;
        box-shadow:0 1px 3px #ddd;
        margin-bottom:6px;
        width: 100%; /* Garante que o checkbox ocupe toda a largura do item */
    }
    .stCheckbox label div[data-testid="stCheckbox-0"] { /* Alinha o checkbox corretamente */
        margin-right: 12px;
    }

    /* Botões personalizados */
    .stButton>button {
        flex:1;
        padding:15px;
        border-radius:10px;
        font-size:1.05rem;
        font-weight:800;
        border:none;
        box-shadow:0 2px 8px rgba(0,0,0,0.01);
        cursor:pointer;
        background:#b30000;
        color:#fff;
        width: 100%; /* Ocupa a largura total do container */
    }
    .stButton>button.blue { background:#1763ad; }
    .stButton>button.green { background:#25d366; }
    .stButton>button.orange { background:#ff9f00; }
    </style>
    """, unsafe_allow_html=True)

# --- Gerenciamento de estado (semelhante ao JavaScript) ---
# Inicializa 'equipamentos' no st.session_state se ainda não existir
if 'equipamentos' not in st.session_state:
    st.session_state.equipamentos = []

def add_equipamento():
    st.session_state.equipamentos.append({
        "tipo": "",
        "nome": "",
        "aplicaQuimica": "Não",
        "produtos": [],
        "parametros": [],
        "purga": "",
        "tempo_purga": "",
        "temp_desaerador": ""
    })

def delete_equipamento(index):
    if index < len(st.session_state.equipamentos):
        st.session_state.equipamentos.pop(index)

def add_produto(equip_index):
    if equip_index < len(st.session_state.equipamentos):
        st.session_state.equipamentos[equip_index]["produtos"].append({
            "nome": "",
            "leituraInicio": "",
            "completado": "",
            "leituraDepois": ""
        })

def delete_produto(equip_index, prod_index):
    if equip_index < len(st.session_state.equipamentos) and prod_index < len(st.session_state.equipamentos[equip_index]["produtos"]):
        st.session_state.equipamentos[equip_index]["produtos"].pop(prod_index)

def add_parametro(equip_index):
    if equip_index < len(st.session_state.equipamentos):
        st.session_state.equipamentos[equip_index]["parametros"].append({
            "nome": "",
            "valor": "",
            "unidade": "ppm",
            "min": "",
            "max": ""
        })

def delete_parametro(equip_index, param_index):
    if equip_index < len(st.session_state.equipamentos) and param_index < len(st.session_state.equipamentos[equip_index]["parametros"]):
        st.session_state.equipamentos[equip_index]["parametros"].pop(param_index)

# --- Layout da Aplicação Streamlit ---
st.markdown('<div class="main-wrap">', unsafe_allow_html=True)
st.markdown('<div class="veolia-card">', unsafe_allow_html=True)

# Header
st.markdown("""
    <header>
        <img src="https://upload.wikimedia.org/wikipedia/commons/4/48/Veolia_logo.svg" class="logo"/>
        <div class="title-main">Relatório Técnico</div>
    </header>
    """, unsafe_allow_html=True)

# Dados Principais
col1, col2 = st.columns(2)
with col1:
    data_visita = st.date_input("Data da Visita", value=date.today(), key="dataVisita")
with col2:
    cliente = st.selectbox("Cliente", ["Selecione", "Michelin", "B Braun", "BRF", "Burn", "Froneri", "P&G", "GE Celma", "Ecogen", "M Dias Branco", "Werner", "Outro"], key="cliente")

responsavel_cliente = st.text_input("Responsável do Cliente", placeholder="Nome completo", key="responsavelCliente")
operador = st.text_input("Operador", placeholder="Nome do operador", key="operador")
analista = st.selectbox("Analista", ["Daniel Sales", "Fabiano Argolo"], key="analista")

st.markdown('<label style="margin-top:13px;">Itens verificados na visita</label>', unsafe_allow_html=True)

# Checklist
checklist_options = {
    "item1": "Abastecimento de produtos",
    "item2": "Verificação do consumo e estoque",
    "item3": "Bombas dosadoras",
    "item4": "Tubulações e conexões sem vazamentos",
    "item5": "Integridade das FDS",
    "item6": "Equipamentos e controladores",
    "item7": "Limpeza dos sensores",
    "item8": "Coleta de amostras"
}
checked_items = {}
st.markdown('<div class="checklist">', unsafe_allow_html=True)
for item_id, item_label in checklist_options.items():
    checked_items[item_id] = st.checkbox(item_label, key=f"checkbox_{item_id}")
st.markdown('</div>', unsafe_allow_html=True)


st.subheader("Equipamentos")
# Botão para adicionar equipamento (fora do loop para evitar recriação)
st.button("+ Adicionar Equipamento", on_click=add_equipamento, key="add_equip_btn")

# Renderizar equipamentos dinamicamente
for i, eq in enumerate(st.session_state.equipamentos):
    st.markdown(f'<div class="equipamento">', unsafe_allow_html=True)
    st.markdown(f'<div style="text-align: right;"><button onClick="window.parent.document.querySelector(\'[data-testid=\"stButton-primary\"] button\').click()" style="background:none;border:none;color:#b30000;font-size:1.15rem;cursor:pointer;">🗑️</button></div>', unsafe_allow_html=True)
    # Streamlit não tem a mesma forma de `onclick` diretamente. Usamos um botão e um key unique.
    st.button("🗑️ Remover Equipamento", on_click=delete_equipamento, args=(i,), key=f"delete_equip_{i}")

    st.markdown(f'<label>Tipo Equipamento</label>', unsafe_allow_html=True)
    st.session_state.equipamentos[i]["tipo"] = st.selectbox(
        "Tipo Equipamento",
        ["Selecione", "Caldeira", "Torre de Resfriamento", "Chiller", "Abrandador", "Outro"],
        index=["Selecione", "Caldeira", "Torre de Resfriamento", "Chiller", "Abrandador", "Outro"].index(eq["tipo"]) if eq["tipo"] else 0,
        key=f"equip_tipo_{i}"
    )
    st.session_state.equipamentos[i]["nome"] = st.text_input(
        "Nome/Descrição",
        value=eq["nome"],
        key=f"equip_nome_{i}"
    )
    st.session_state.equipamentos[i]["aplicaQuimica"] = st.radio(
        "Há aplicação química?",
        ["Não", "Sim"],
        index=0 if eq["aplicaQuimica"] == "Não" else 1,
        key=f"aplica_quimica_{i}"
    )

    if st.session_state.equipamentos[i]["aplicaQuimica"] == "Sim":
        st.markdown(f'<b>Produtos Químicos</b>', unsafe_allow_html=True)
        st.button("+ Adicionar Produto", on_click=add_produto, args=(i,), key=f"add_prod_{i}")
        for k, prod in enumerate(eq["produtos"]):
            st.markdown(f'<div class="produto-quimico-card">', unsafe_allow_html=True)
            st.button("🗑️ Remover Produto", on_click=delete_produto, args=(i, k,), key=f"del_prod_{i}_{k}")
            st.session_state.equipamentos[i]["produtos"][k]["nome"] = st.text_input(
                "Nome do produto",
                value=prod["nome"],
                key=f"prod_nome_{i}_{k}"
            )
            st.session_state.equipamentos[i]["produtos"][k]["leituraInicio"] = st.number_input(
                "Leitura antes (L/kg)",
                value=float(prod["leituraInicio"]) if prod["leituraInicio"] else 0.0,
                key=f"prod_leitura_inicio_{i}_{k}",
                format="%.2f"
            )
            st.session_state.equipamentos[i]["produtos"][k]["completado"] = st.number_input(
                "Volume completado",
                value=float(prod["completado"]) if prod["completado"] else 0.0,
                key=f"prod_completado_{i}_{k}",
                format="%.2f"
            )
            st.session_state.equipamentos[i]["produtos"][k]["leituraDepois"] = st.number_input(
                "Leitura depois",
                value=float(prod["leituraDepois"]) if prod["leituraDepois"] else 0.0,
                key=f"prod_leitura_depois_{i}_{k}",
                format="%.2f"
            )
            st.markdown('</div>', unsafe_allow_html=True)

    st.markdown(f'<b>Parâmetros Analíticos</b>', unsafe_allow_html=True)
    st.button("+ Adicionar Parâmetro", on_click=add_parametro, args=(i,), key=f"add_param_{i}")
    for j, param in enumerate(eq["parametros"]):
        st.markdown(f'<div class="param-row">', unsafe_allow_html=True)
        col_p1, col_p2, col_p3, col_p4, col_p5, col_p6 = st.columns([3, 2, 2, 1, 1, 0.5]) # Ajuste as proporções
        with col_p1:
            st.session_state.equipamentos[i]["parametros"][j]["nome"] = st.text_input(
                "Nome",
                value=param["nome"],
                key=f"param_nome_{i}_{j}"
            )
        with col_p2:
            st.session_state.equipamentos[i]["parametros"][j]["valor"] = st.number_input(
                "Valor",
                value=float(param["valor"]) if param["valor"] else 0.0,
                key=f"param_valor_{i}_{j}",
                format="%.2f"
            )
        with col_p3:
            st.session_state.equipamentos[i]["parametros"][j]["unidade"] = st.selectbox(
                "Unidade",
                ["ppm", "mg/L", "g/L", "uS", "NTU", "Outro"],
                index=["ppm", "mg/L", "g/L", "uS", "NTU", "Outro"].index(param["unidade"]) if param["unidade"] else 0,
                key=f"param_unidade_{i}_{j}"
            )
        with col_p4:
            st.session_state.equipamentos[i]["parametros"][j]["min"] = st.number_input(
                "Min",
                value=float(param["min"]) if param["min"] else 0.0,
                key=f"param_min_{i}_{j}",
                format="%.2f"
            )
        with col_p5:
            st.session_state.equipamentos[i]["parametros"][j]["max"] = st.number_input(
                "Max",
                value=float(param["max"]) if param["max"] else 0.0,
                key=f"param_max_{i}_{j}",
                format="%.2f"
            )
        with col_p6:
            st.button("🗑️", on_click=delete_parametro, args=(i, j,), key=f"del_param_{i}_{j}")
        st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# Fotos (apenas placeholders, Streamlit não manipula upload e preview de imagens diretamente no navegador como HTML+JS)
st.markdown('<label>Fotos Antes/Depois</label>', unsafe_allow_html=True)
col_foto_antes, col_foto_depois = st.columns(2)
with col_foto_antes:
    st.file_uploader("Foto Antes:", type=["jpg", "jpeg", "png"], key="foto_antes_upload")
    # st.image(preview_antes_url, use_column_width=True) # Se tiver URL de preview

with col_foto_depois:
    st.file_uploader("Foto Depois:", type=["jpg", "jpeg", "png"], key="foto_depois_upload")
    # st.image(preview_depois_url, use_column_width=True) # Se tiver URL de preview

# Assinatura (simplificado, Streamlit não tem canvas para desenhar assinatura)
st.markdown('<label style="margin-top:13px;">Assinatura do Cliente</label>', unsafe_allow_html=True)
with st.container(border=True): # Simula o assinatura-box
    nome_responsavel_assina = st.text_input("Nome do responsável", placeholder="Nome do responsável pela assinatura", key="nomeResponsavelAssina")
    st.info("O Streamlit não possui um componente de canvas para assinatura digital. Você pode usar um campo para upload de imagem da assinatura ou coletar o nome do responsável.")
    # Exemplo de upload de imagem para assinatura, se for o caso
    # assinatura_upload = st.file_uploader("Upload da Assinatura (imagem)", type=["png", "jpg"], key="assinatura_upload")
    # if assinatura_upload:
    #    st.image(assinatura_upload, caption="Assinatura Carregada", use_column_width=True)


recomendacoes = st.text_area("Recomendações/Ações em Destaque", placeholder="Recomendações ou ações sugeridas", key="recomendacoes")

# Botões de Ação
st.markdown('<div class="btn-row" style="display:flex; gap:13px;">', unsafe_allow_html=True)
col_pdf, col_email = st.columns(2)
with col_pdf:
    if st.button("📄 Gerar PDF", key="btn_pdf"):
        st.success("Função 'Gerar PDF' acionada! (Implementação futura de geração de PDF)")
with col_email:
    if st.button("📧 Enviar E-mail", key="btn_email"):
        st.success("Função 'Enviar E-mail' acionada! (Implementação futura de envio de e-mail)")
st.markdown('</div>', unsafe_allow_html=True)


st.markdown('<div class="btn-row" style="display:flex; gap:13px; margin-top:10px;">', unsafe_allow_html=True)
col_whatsapp, col_agenda = st.columns(2)
with col_whatsapp:
    if st.button("📱 WhatsApp", key="btn_whatsapp"):
        st.success("Função 'Enviar WhatsApp' acionada! (Implementação futura de envio de WhatsApp)")
with col_agenda:
    if st.button("📅 Google Agenda", key="btn_agenda"):
        st.success("Função 'Agendar Visita' acionada! (Implementação futura de integração com Google Agenda)")
st.markdown('</div>', unsafe_allow_html=True)

st.markdown("""
    <div class="rodape-pdf">
        Veolia Water Technologies Ltda - CNPJ: 03.000.597/0001-00
    </div>
    """, unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# --- Exibir dados coletados (para depuração ou visualização no Power BI) ---
st.sidebar.subheader("Dados Coletados")
data_output = {
    "dataVisita": str(data_visita),
    "cliente": cliente,
    "responsavelCliente": responsavel_cliente,
    "operador": operador,
    "analista": analista,
    "itensVerificados": checked_items,
    "equipamentos": st.session_state.equipamentos,
    "nomeResponsavelAssinatura": nome_responsavel_assina,
    "recomendacoes": recomendacoes
}
st.sidebar.json(data_output) # Exibe os dados coletados como JSON na barra lateral

# Opcional: Preparar DataFrames para exportação/visualização
# df_principal = pd.DataFrame([data_output]) # Você pode querer reestruturar isso
# st.sidebar.write(df_principal)
