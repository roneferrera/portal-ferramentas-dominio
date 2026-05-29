import streamlit as st
import pandas as pd
import os
from datetime import datetime
from io import BytesIO

# =========================================================
# CONFIGURAÇÃO GERAL
# =========================================================

st.set_page_config(
    page_title="Portal de Ferramentas",
    page_icon="🧩",
    layout="wide"
)

# =========================================================
# CONSTANTES
# =========================================================

PASTA_DADOS = "dados"
PASTA_ASSETS = "assets"
PASTA_UPLOADS_IMAGENS = "uploads/modelos_bgr/imagens"
PASTA_UPLOADS_BGR = "uploads/modelos_bgr/arquivos_bgr"

ARQUIVO_CONVERSORES = os.path.join(PASTA_DADOS, "conversores.csv")
ARQUIVO_MODELOS_BGR = os.path.join(PASTA_DADOS, "modelos_bgr.csv")
ARQUIVO_ESCOLHAS_BGR = os.path.join(PASTA_DADOS, "escolhas_bgr.csv")

DEPARTAMENTOS = [
    "Fiscal",
    "Folha de Pagamento",
    "Contabilidade",
    "Patrimônio",
    "Honorários"
]

STATUS_FERRAMENTAS = [
    "Ativo",
    "Em manutenção",
    "Em desenvolvimento"
]

# =========================================================
# CRIAÇÃO DAS PASTAS
# =========================================================

os.makedirs(PASTA_DADOS, exist_ok=True)
os.makedirs(PASTA_ASSETS, exist_ok=True)
os.makedirs(PASTA_UPLOADS_IMAGENS, exist_ok=True)
os.makedirs(PASTA_UPLOADS_BGR, exist_ok=True)

# =========================================================
# ESTILO VISUAL - TEMA ESCURO THOMSON REUTERS / DOMÍNIO
# =========================================================

st.markdown("""
<style>

/* ===============================
   PALETA ESCURA THOMSON REUTERS / DOMÍNIO
================================ */

:root {
    --tr-orange: #FF8000;
    --tr-orange-dark: #E66F00;
    --tr-orange-soft: rgba(255, 128, 0, 0.16);

    --tr-bg-main: #121212;
    --tr-bg-sidebar: #181818;
    --tr-bg-card: #1F1F1F;
    --tr-bg-card-hover: #252525;
    --tr-bg-input: #242424;

    --tr-border: #333333;
    --tr-border-light: #444444;

    --tr-text-main: #F5F5F5;
    --tr-text-secondary: #D0D0D0;
    --tr-text-muted: #A8A8A8;

    --tr-success-bg: rgba(46, 125, 50, 0.22);
    --tr-success-text: #81C784;

    --tr-warning-bg: rgba(255, 128, 0, 0.18);
    --tr-warning-text: #FFB366;

    --tr-info-bg: rgba(66, 165, 245, 0.18);
    --tr-info-text: #90CAF9;

    --tr-error-bg: rgba(239, 83, 80, 0.18);
    --tr-error-text: #EF9A9A;
}

/* ===============================
   FUNDO GERAL
================================ */

.stApp {
    background-color: var(--tr-bg-main);
    color: var(--tr-text-main);
}

.block-container {
    padding-top: 1.5rem;
    padding-bottom: 3rem;
}

/* ===============================
   TIPOGRAFIA
================================ */

html, body, [class*="css"] {
    font-family: Arial, Helvetica, sans-serif;
}

p, span, label, div {
    color: var(--tr-text-secondary);
}

h1 {
    color: var(--tr-text-main);
    font-weight: 700;
    border-left: 6px solid var(--tr-orange);
    padding-left: 14px;
}

h2, h3, h4 {
    color: var(--tr-text-main);
}

/* ===============================
   SIDEBAR
================================ */

section[data-testid="stSidebar"] {
    background-color: var(--tr-bg-sidebar);
    border-right: 1px solid var(--tr-border);
}

section[data-testid="stSidebar"] h1,
section[data-testid="stSidebar"] h2,
section[data-testid="stSidebar"] h3,
section[data-testid="stSidebar"] label,
section[data-testid="stSidebar"] p,
section[data-testid="stSidebar"] span,
section[data-testid="stSidebar"] div {
    color: var(--tr-text-secondary);
}

section[data-testid="stSidebar"] hr {
    border-color: var(--tr-border);
}

/* ===============================
   CARDS
================================ */

.card {
    padding: 24px;
    border-radius: 14px;
    background-color: var(--tr-bg-card);
    border: 1px solid var(--tr-border);
    margin-bottom: 18px;
    box-shadow: 0 4px 16px rgba(0,0,0,0.35);
    transition: all 0.2s ease-in-out;
}

.card:hover {
    background-color: var(--tr-bg-card-hover);
    border-color: var(--tr-orange);
    box-shadow: 0 6px 20px rgba(255,128,0,0.18);
}

.card h3 {
    margin-top: 0;
    color: var(--tr-text-main);
}

.card p {
    color: var(--tr-text-secondary);
}

/* ===============================
   BOTÃO LINK LARANJA
================================ */

.botao-link {
    display: inline-block;
    background-color: var(--tr-orange);
    color: #FFFFFF !important;
    padding: 10px 18px;
    border-radius: 8px;
    text-decoration: none;
    font-weight: 700;
    margin-top: 10px;
    transition: background-color 0.2s ease-in-out;
}

.botao-link:hover {
    background-color: var(--tr-orange-dark);
    color: #FFFFFF !important;
}

/* ===============================
   BOTÕES NATIVOS STREAMLIT
================================ */

.stButton > button {
    background-color: var(--tr-orange);
    color: #FFFFFF;
    border: 1px solid var(--tr-orange);
    border-radius: 8px;
    font-weight: 700;
    padding: 0.5rem 1rem;
}

.stButton > button:hover {
    background-color: var(--tr-orange-dark);
    color: #FFFFFF;
    border-color: var(--tr-orange-dark);
}

.stButton > button:focus {
    box-shadow: 0 0 0 2px var(--tr-orange-soft);
}

.stDownloadButton > button {
    background-color: var(--tr-orange);
    color: #FFFFFF;
    border: 1px solid var(--tr-orange);
    border-radius: 8px;
    font-weight: 700;
}

.stDownloadButton > button:hover {
    background-color: var(--tr-orange-dark);
    color: #FFFFFF;
    border-color: var(--tr-orange-dark);
}

.stDownloadButton > button:focus {
    box-shadow: 0 0 0 2px var(--tr-orange-soft);
}

/* ===============================
   INPUTS / SELECTBOX / TEXTAREA
================================ */

.stTextInput input,
.stTextArea textarea {
    background-color: var(--tr-bg-input);
    color: var(--tr-text-main);
    border: 1px solid var(--tr-border-light);
    border-radius: 8px;
}

.stTextInput input::placeholder,
.stTextArea textarea::placeholder {
    color: var(--tr-text-muted);
}

.stTextInput input:focus,
.stTextArea textarea:focus {
    border-color: var(--tr-orange) !important;
    box-shadow: 0 0 0 1px var(--tr-orange) !important;
}

.stSelectbox div[data-baseweb="select"] {
    background-color: var(--tr-bg-input);
    color: var(--tr-text-main);
    border-radius: 8px;
}

.stSelectbox div[data-baseweb="select"] > div {
    background-color: var(--tr-bg-input);
    color: var(--tr-text-main);
}

/* Dropdown */
div[data-baseweb="popover"] {
    background-color: var(--tr-bg-card);
}

div[data-baseweb="menu"] {
    background-color: var(--tr-bg-card);
    color: var(--tr-text-main);
}

div[data-baseweb="menu"] li {
    color: var(--tr-text-main);
}

div[data-baseweb="menu"] li:hover {
    background-color: var(--tr-orange-soft);
}

/* ===============================
   RADIO / CHECKBOX
================================ */

.stRadio label,
.stCheckbox label {
    color: var(--tr-text-secondary);
}

.stCheckbox [data-testid="stMarkdownContainer"] p,
.stRadio [data-testid="stMarkdownContainer"] p {
    color: var(--tr-text-secondary);
}

/* ===============================
   STATUS
================================ */

.status-ativo {
    display: inline-block;
    padding: 5px 11px;
    border-radius: 999px;
    background-color: var(--tr-success-bg);
    color: var(--tr-success-text);
    font-weight: 700;
    font-size: 13px;
}

.status-manutencao {
    display: inline-block;
    padding: 5px 11px;
    border-radius: 999px;
    background-color: var(--tr-warning-bg);
    color: var(--tr-warning-text);
    font-weight: 700;
    font-size: 13px;
}

.status-desenvolvimento {
    display: inline-block;
    padding: 5px 11px;
    border-radius: 999px;
    background-color: var(--tr-info-bg);
    color: var(--tr-info-text);
    font-weight: 700;
    font-size: 13px;
}

/* ===============================
   CARDS DOS DEPARTAMENTOS
================================ */

.setor-card {
    padding: 22px;
    border-radius: 14px;
    background-color: var(--tr-bg-card);
    border: 1px solid var(--tr-border);
    text-align: center;
    box-shadow: 0 4px 16px rgba(0,0,0,0.35);
    min-height: 140px;
    transition: all 0.2s ease-in-out;
}

.setor-card:hover {
    background-color: var(--tr-bg-card-hover);
    border-color: var(--tr-orange);
    transform: translateY(-2px);
    box-shadow: 0 6px 20px rgba(255,128,0,0.18);
}

.setor-card h1 {
    border-left: none;
    padding-left: 0;
    color: var(--tr-orange);
}

.setor-card h4 {
    color: var(--tr-text-main);
    margin-bottom: 4px;
}

.setor-card p {
    color: var(--tr-text-muted);
}

/* ===============================
   AVISO ADMINISTRATIVO
================================ */

.aviso-admin {
    padding: 14px;
    border-radius: 10px;
    background-color: var(--tr-warning-bg);
    color: var(--tr-warning-text);
    border: 1px solid var(--tr-orange);
}

.aviso-admin strong {
    color: var(--tr-warning-text);
}

/* ===============================
   MÉTRICAS
================================ */

[data-testid="stMetric"] {
    background-color: var(--tr-bg-card);
    border: 1px solid var(--tr-border);
    border-radius: 14px;
    padding: 18px;
    box-shadow: 0 4px 16px rgba(0,0,0,0.35);
}

[data-testid="stMetricLabel"] {
    color: var(--tr-text-muted);
}

[data-testid="stMetricValue"] {
    color: var(--tr-orange);
    font-weight: 700;
}

/* ===============================
   TABS
================================ */

.stTabs [data-baseweb="tab-list"] {
    gap: 8px;
    border-bottom: 1px solid var(--tr-border);
}

.stTabs [data-baseweb="tab"] {
    background-color: var(--tr-bg-card);
    border-radius: 8px 8px 0 0;
    color: var(--tr-text-secondary);
    border: 1px solid var(--tr-border);
    padding: 10px 16px;
}

.stTabs [aria-selected="true"] {
    background-color: var(--tr-orange-soft);
    color: var(--tr-orange);
    border-bottom: 3px solid var(--tr-orange);
    font-weight: 700;
}

/* ===============================
   DATAFRAME / EDITOR
================================ */

[data-testid="stDataFrame"] {
    border: 1px solid var(--tr-border);
    border-radius: 10px;
    background-color: var(--tr-bg-card);
}

/* ===============================
   ALERTAS STREAMLIT
================================ */

div[data-testid="stAlert"] {
    border-radius: 10px;
    border: 1px solid var(--tr-border);
}

/* ===============================
   EXPANDER
================================ */

.streamlit-expanderHeader {
    color: var(--tr-text-main);
    font-weight: 700;
    background-color: var(--tr-bg-card);
}

div[data-testid="stExpander"] {
    background-color: var(--tr-bg-card);
    border: 1px solid var(--tr-border);
    border-radius: 10px;
}

/* ===============================
   FILE UPLOADER
================================ */

[data-testid="stFileUploader"] {
    background-color: var(--tr-bg-card);
    border: 1px dashed var(--tr-border-light);
    border-radius: 12px;
    padding: 12px;
}

[data-testid="stFileUploader"] section {
    background-color: var(--tr-bg-input);
    border: 1px dashed var(--tr-border-light);
}

/* ===============================
   LINHAS / DIVISORES
================================ */

hr {
    border-color: var(--tr-border);
}

/* ===============================
   LINKS
================================ */

a {
    color: var(--tr-orange);
}

a:hover {
    color: var(--tr-orange-dark);
}

/* ===============================
   SCROLLBAR OPCIONAL
================================ */

::-webkit-scrollbar {
    width: 10px;
    height: 10px;
}

::-webkit-scrollbar-track {
    background: var(--tr-bg-main);
}

::-webkit-scrollbar-thumb {
    background: var(--tr-border-light);
    border-radius: 999px;
}

::-webkit-scrollbar-thumb:hover {
    background: var(--tr-orange);
}

</style>
""", unsafe_allow_html=True)

# =========================================================
# FUNÇÕES AUXILIARES
# =========================================================

def inicializar_csvs():
    if not os.path.exists(ARQUIVO_CONVERSORES):
        df = pd.DataFrame([
            {
                "nome": "Gerador RPA TXT",
                "departamento": "Folha de Pagamento",
                "descricao": "Gera arquivos TXT para processamento por RPA.",
                "url": "https://gerador-rpa-txt.streamlit.app/",
                "status": "Ativo",
                "data_cadastro": datetime.now().strftime("%d/%m/%Y %H:%M:%S")
            },
            {
                "nome": "Converte Bens Domínio",
                "departamento": "Patrimônio",
                "descricao": "Conversor de bens patrimoniais para leiaute compatível com Domínio.",
                "url": "https://convertebensdominio.streamlit.app/",
                "status": "Ativo",
                "data_cadastro": datetime.now().strftime("%d/%m/%Y %H:%M:%S")
            },
            {
                "nome": "Eventos Com Plano / Sem Plano",
                "departamento": "Fiscal",
                "descricao": "Ferramenta para tratar eventos com plano e sem plano.",
                "url": "https://eventos-complano-semplano.streamlit.app/",
                "status": "Ativo",
                "data_cadastro": datetime.now().strftime("%d/%m/%Y %H:%M:%S")
            },
            {
                "nome": "Clientes e Fornecedores - Conta Patrimonial",
                "departamento": "Contabilidade",
                "descricao": "Tratamento de clientes, fornecedores e contas patrimoniais.",
                "url": "https://clientes-fornecedores-conta-patrimonial.streamlit.app/",
                "status": "Ativo",
                "data_cadastro": datetime.now().strftime("%d/%m/%Y %H:%M:%S")
            },
            {
                "nome": "Conversor Leiaute com Separador Domínio",
                "departamento": "Fiscal",
                "descricao": "Conversor de leiaute com separador para o sistema Domínio.",
                "url": "https://conversorleiautecomseparadordominio.streamlit.app/",
                "status": "Ativo",
                "data_cadastro": datetime.now().strftime("%d/%m/%Y %H:%M:%S")
            }
        ])
        df.to_csv(ARQUIVO_CONVERSORES, index=False)

    if not os.path.exists(ARQUIVO_MODELOS_BGR):
        df = pd.DataFrame(columns=[
            "nome",
            "departamento",
            "descricao",
            "imagem",
            "arquivo_bgr",
            "status",
            "data_upload"
        ])
        df.to_csv(ARQUIVO_MODELOS_BGR, index=False)

    if not os.path.exists(ARQUIVO_ESCOLHAS_BGR):
        df = pd.DataFrame(columns=[
            "data_hora",
            "cliente",
            "departamento",
            "modelo",
            "observacao"
        ])
        df.to_csv(ARQUIVO_ESCOLHAS_BGR, index=False)


def garantir_colunas_modelos_bgr():
    if not os.path.exists(ARQUIVO_MODELOS_BGR):
        return

    df = pd.read_csv(ARQUIVO_MODELOS_BGR)

    alterado = False

    if "imagem" not in df.columns:
        if "arquivo" in df.columns:
            df["imagem"] = df["arquivo"]
        else:
            df["imagem"] = ""
        alterado = True

    if "arquivo_bgr" not in df.columns:
        df["arquivo_bgr"] = ""
        alterado = True

    colunas_finais = [
        "nome",
        "departamento",
        "descricao",
        "imagem",
        "arquivo_bgr",
        "status",
        "data_upload"
    ]

    for coluna in colunas_finais:
        if coluna not in df.columns:
            df[coluna] = ""
            alterado = True

    df = df[colunas_finais]

    if alterado:
        df.to_csv(ARQUIVO_MODELOS_BGR, index=False)


def carregar_csv(caminho):
    if os.path.exists(caminho):
        return pd.read_csv(caminho)
    return pd.DataFrame()


def salvar_csv(df, caminho):
    df.to_csv(caminho, index=False)


def status_html(status):
    if status == "Ativo":
        return '<span class="status-ativo">Ativo</span>'
    elif status == "Em manutenção":
        return '<span class="status-manutencao">Em manutenção</span>'
    else:
        return '<span class="status-desenvolvimento">Em desenvolvimento</span>'


def gerar_excel_download(dfs: dict):
    output = BytesIO()

    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        for nome_aba, df in dfs.items():
            df.to_excel(writer, index=False, sheet_name=nome_aba[:31])

    return output.getvalue()


def mostrar_logo():
    caminho_logo = os.path.join(PASTA_ASSETS, "logo.png")

    if os.path.exists(caminho_logo):
        st.sidebar.image(caminho_logo, use_container_width=True)
    else:
        st.sidebar.markdown("### 🧩 Portal de Ferramentas")


def nome_arquivo_seguro(nome_arquivo):
    return (
        nome_arquivo
        .replace(" ", "_")
        .replace("/", "_")
        .replace("\\", "_")
        .replace(":", "_")
        .replace(";", "_")
    )


def valor_texto(valor):
    if pd.isna(valor):
        return ""
    return str(valor).strip()


# =========================================================
# INICIALIZAÇÃO
# =========================================================

inicializar_csvs()
garantir_colunas_modelos_bgr()
mostrar_logo()

# =========================================================
# MENU LATERAL
# =========================================================

st.sidebar.write("---")
st.sidebar.subheader("Menu público")

pagina_publica = st.sidebar.radio(
    "Selecione uma opção:",
    [
        "Início",
        "Conversores",
        "Relatórios BGR"
    ]
)

st.sidebar.write("---")
st.sidebar.subheader("Área administrativa")

abrir_admin = st.sidebar.checkbox("Abrir Painel Administrativo")

if abrir_admin:
    pagina = "Painel Administrativo"
else:
    pagina = pagina_publica

# =========================================================
# PÁGINA INÍCIO
# =========================================================

if pagina == "Início":
    st.title("🧩 Portal de Ferramentas")
    st.write("Central de conversores, relatórios BGR e ferramentas internas por departamento.")

    df_conversores = carregar_csv(ARQUIVO_CONVERSORES)
    df_modelos = carregar_csv(ARQUIVO_MODELOS_BGR)
    df_escolhas = carregar_csv(ARQUIVO_ESCOLHAS_BGR)

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Conversores cadastrados", len(df_conversores))

    with col2:
        st.metric("Modelos BGR cadastrados", len(df_modelos))

    with col3:
        st.metric("Escolhas registradas", len(df_escolhas))

    st.write("---")
    st.subheader("Departamentos")

    icones = {
        "Fiscal": "📊",
        "Folha de Pagamento": "👥",
        "Contabilidade": "📚",
        "Patrimônio": "🏢",
        "Honorários": "💰"
    }

    cols = st.columns(5)

    for i, dep in enumerate(DEPARTAMENTOS):
        with cols[i]:
            qtd = len(df_conversores[df_conversores["departamento"] == dep]) if not df_conversores.empty else 0
            st.markdown(f"""
            <div class="setor-card">
                <h1>{icones[dep]}</h1>
                <h4>{dep}</h4>
                <p>{qtd} ferramenta(s)</p>
            </div>
            """, unsafe_allow_html=True)

# =========================================================
# PÁGINA CONVERSORES
# =========================================================

elif pagina == "Conversores":
    st.title("🛠️ Conversores")

    df = carregar_csv(ARQUIVO_CONVERSORES)

    col1, col2 = st.columns(2)

    with col1:
        filtro_departamento = st.selectbox(
            "Filtrar por departamento:",
            ["Todos"] + DEPARTAMENTOS
        )

    with col2:
        filtro_status = st.selectbox(
            "Filtrar por status:",
            ["Todos"] + STATUS_FERRAMENTAS
        )

    df_filtrado = df.copy()

    if not df_filtrado.empty:
        if filtro_departamento != "Todos":
            df_filtrado = df_filtrado[df_filtrado["departamento"] == filtro_departamento]

        if filtro_status != "Todos":
            df_filtrado = df_filtrado[df_filtrado["status"] == filtro_status]

    if df_filtrado.empty:
        st.info("Nenhum conversor encontrado para os filtros selecionados.")
    else:
        for _, row in df_filtrado.iterrows():
            st.markdown(f"""
            <div class="card">
                <h3>{row["nome"]}</h3>
                <p><strong>Departamento:</strong> {row["departamento"]}</p>
                <p>{row["descricao"]}</p>
                <p><strong>Status:</strong> {status_html(row["status"])}</p>
            """, unsafe_allow_html=True)

            if row["status"] == "Ativo" and valor_texto(row["url"]):
                st.markdown(f"""
                    <a class="botao-link" href="{row["url"]}" target="_blank">
                        Acessar ferramenta
                    </a>
                """, unsafe_allow_html=True)
            elif row["status"] == "Em manutenção":
                st.warning("Esta ferramenta está em manutenção.")
            else:
                st.info("Esta ferramenta está em desenvolvimento.")

            st.markdown("</div>", unsafe_allow_html=True)

# =========================================================
# PÁGINA RELATÓRIOS BGR
# =========================================================

elif pagina == "Relatórios BGR":
    st.title("📄 Relatórios BGR")

    df_modelos = carregar_csv(ARQUIVO_MODELOS_BGR)

    st.write(
        "Consulte os modelos BGR disponíveis, visualize a prévia e baixe o arquivo `.bgr` correspondente."
    )

    col_filtro1, col_filtro2 = st.columns([1, 2])

    with col_filtro1:
        departamento = st.selectbox(
            "Selecione o departamento:",
            DEPARTAMENTOS
        )

    with col_filtro2:
        pesquisa = st.text_input(
            "Pesquisar no nome ou descrição do BGR:",
            placeholder="Exemplo: folha, fiscal, impostos, balancete, honorários..."
        )

    if not df_modelos.empty:
        df_dep = df_modelos[
            (df_modelos["departamento"] == departamento) &
            (df_modelos["status"] == "Ativo")
        ].copy()

        if pesquisa:
            df_dep = df_dep[
                df_dep["descricao"].str.contains(pesquisa, case=False, na=False) |
                df_dep["nome"].str.contains(pesquisa, case=False, na=False)
            ]
    else:
        df_dep = pd.DataFrame()

    st.write("---")

    if df_dep.empty:
        st.info("Nenhum modelo BGR encontrado para os filtros selecionados.")
    else:
        st.success(f"{len(df_dep)} modelo(s) BGR encontrado(s).")

        for index, modelo_info in df_dep.iterrows():
            nome_modelo = valor_texto(modelo_info.get("nome", ""))
            descricao_modelo = valor_texto(modelo_info.get("descricao", ""))
            nome_imagem = valor_texto(modelo_info.get("imagem", ""))
            nome_bgr = valor_texto(modelo_info.get("arquivo_bgr", ""))

            st.markdown("""
            <div class="card">
            """, unsafe_allow_html=True)

            col_img, col_desc, col_download = st.columns([1.2, 2.5, 1.2])

            with col_img:
                st.markdown(f"### {nome_modelo}")

                if nome_imagem:
                    caminho_imagem = os.path.join(
                        PASTA_UPLOADS_IMAGENS,
                        nome_imagem
                    )

                    if os.path.exists(caminho_imagem):
                        st.image(
                            caminho_imagem,
                            caption="Prévia",
                            width=220
                        )

                        with st.expander("🔍 Ver imagem maior"):
                            st.image(
                                caminho_imagem,
                                caption=nome_modelo,
                                use_container_width=True
                            )
                    else:
                        st.warning("Imagem não encontrada.")
                else:
                    st.info("Sem imagem cadastrada.")

            with col_desc:
                st.markdown("#### Descrição")
                st.write(descricao_modelo)

                st.markdown("#### Informações")
                st.write(f"**Departamento:** {departamento}")
                st.write(f"**Status:** {modelo_info.get('status', '')}")

                data_upload = valor_texto(modelo_info.get("data_upload", ""))
                if data_upload:
                    st.write(f"**Data de upload:** {data_upload}")

            with col_download:
                st.markdown("#### Arquivo")

                if nome_bgr:
                    caminho_bgr = os.path.join(
                        PASTA_UPLOADS_BGR,
                        nome_bgr
                    )

                    if os.path.exists(caminho_bgr):
                        with open(caminho_bgr, "rb") as file:
                            st.download_button(
                                label="📥 Baixar .BGR",
                                data=file,
                                file_name=nome_bgr,
                                mime="application/octet-stream",
                                key=f"download_bgr_{index}"
                            )
                    else:
                        st.warning("Arquivo .BGR não encontrado.")
                else:
                    st.info("Sem arquivo .BGR.")

                st.write("---")

                if st.button(
                    "Selecionar modelo",
                    key=f"selecionar_modelo_{index}"
                ):
                    st.session_state["modelo_bgr_selecionado"] = nome_modelo
                    st.session_state["departamento_bgr_selecionado"] = departamento

            st.markdown("</div>", unsafe_allow_html=True)
            st.write("")

        st.write("---")
        st.subheader("Registrar escolha do modelo")

        modelo_salvo = st.session_state.get("modelo_bgr_selecionado", "")

        if modelo_salvo:
            st.info(f"Modelo selecionado: **{modelo_salvo}**")
        else:
            st.warning("Selecione um modelo acima antes de confirmar a escolha.")

        cliente = st.text_input("Nome do cliente")
        observacao = st.text_area("Observações")

        if st.button("Confirmar escolha"):
            if not modelo_salvo:
                st.warning("Selecione um modelo BGR antes de confirmar.")
            elif not cliente:
                st.warning("Informe o nome do cliente.")
            else:
                df_escolhas = carregar_csv(ARQUIVO_ESCOLHAS_BGR)

                novo = pd.DataFrame([{
                    "data_hora": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
                    "cliente": cliente,
                    "departamento": st.session_state.get(
                        "departamento_bgr_selecionado",
                        departamento
                    ),
                    "modelo": modelo_salvo,
                    "observacao": observacao
                }])

                df_escolhas = pd.concat(
                    [df_escolhas, novo],
                    ignore_index=True
                )

                salvar_csv(df_escolhas, ARQUIVO_ESCOLHAS_BGR)

                st.success("Escolha registrada com sucesso!")

                st.session_state["modelo_bgr_selecionado"] = ""
                st.session_state["departamento_bgr_selecionado"] = ""

# =========================================================
# PAINEL ADMINISTRATIVO
# =========================================================

elif pagina == "Painel Administrativo":
    st.title("⚙️ Painel Administrativo")

    st.markdown("""
    <div class="aviso-admin">
        <strong>Atenção:</strong> esta versão está sem login. O painel administrativo está separado do menu público,
        mas ainda não possui senha.
    </div>
    """, unsafe_allow_html=True)

    st.write("")

    aba1, aba2, aba3, aba4, aba5 = st.tabs([
        "Cadastrar Conversor",
        "Upload Modelo BGR",
        "Histórico BGR",
        "Gerenciar Dados",
        "Exportações"
    ])

    with aba1:
        st.subheader("➕ Cadastrar novo conversor")

        with st.form("form_conversor"):
            nome = st.text_input("Nome do conversor")
            departamento = st.selectbox("Departamento", DEPARTAMENTOS)
            descricao = st.text_area("Descrição")
            url = st.text_input("URL do conversor")
            status = st.selectbox("Status", STATUS_FERRAMENTAS)

            enviar = st.form_submit_button("Cadastrar conversor")

            if enviar:
                if nome and departamento and descricao:
                    df = carregar_csv(ARQUIVO_CONVERSORES)

                    novo = pd.DataFrame([{
                        "nome": nome,
                        "departamento": departamento,
                        "descricao": descricao,
                        "url": url,
                        "status": status,
                        "data_cadastro": datetime.now().strftime("%d/%m/%Y %H:%M:%S")
                    }])

                    df = pd.concat([df, novo], ignore_index=True)
                    salvar_csv(df, ARQUIVO_CONVERSORES)

                    st.success("Conversor cadastrado com sucesso!")
                else:
                    st.warning("Preencha nome, departamento e descrição.")

    with aba2:
        st.subheader("📤 Upload de modelo BGR")

        st.write(
            "Cadastre uma imagem de prévia do relatório e, se desejar, o arquivo `.bgr` correspondente."
        )

        with st.form("form_bgr"):
            nome_modelo = st.text_input("Nome do modelo BGR")
            departamento_modelo = st.selectbox("Departamento do modelo", DEPARTAMENTOS)
            descricao_modelo = st.text_area("Descrição do modelo")
            status_modelo = st.selectbox("Status do modelo", STATUS_FERRAMENTAS)

            imagem = st.file_uploader(
                "Selecione a imagem de prévia do relatório",
                type=["png", "jpg", "jpeg"]
            )

            arquivo_bgr = st.file_uploader(
                "Selecione o arquivo .BGR",
                type=["bgr"]
            )

            enviar_modelo = st.form_submit_button("Enviar modelo BGR")

            if enviar_modelo:
                if nome_modelo and departamento_modelo and imagem:
                    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")

                    nome_imagem_seguro = nome_arquivo_seguro(imagem.name)
                    nome_imagem_salva = f"{timestamp}_{nome_imagem_seguro}"
                    caminho_imagem_salvar = os.path.join(
                        PASTA_UPLOADS_IMAGENS,
                        nome_imagem_salva
                    )

                    with open(caminho_imagem_salvar, "wb") as f:
                        f.write(imagem.getbuffer())

                    nome_bgr_salvo = ""

                    if arquivo_bgr is not None:
                        nome_bgr_seguro = nome_arquivo_seguro(arquivo_bgr.name)
                        nome_bgr_salvo = f"{timestamp}_{nome_bgr_seguro}"
                        caminho_bgr_salvar = os.path.join(
                            PASTA_UPLOADS_BGR,
                            nome_bgr_salvo
                        )

                        with open(caminho_bgr_salvar, "wb") as f:
                            f.write(arquivo_bgr.getbuffer())

                    df = carregar_csv(ARQUIVO_MODELOS_BGR)

                    novo = pd.DataFrame([{
                        "nome": nome_modelo,
                        "departamento": departamento_modelo,
                        "descricao": descricao_modelo,
                        "imagem": nome_imagem_salva,
                        "arquivo_bgr": nome_bgr_salvo,
                        "status": status_modelo,
                        "data_upload": datetime.now().strftime("%d/%m/%Y %H:%M:%S")
                    }])

                    df = pd.concat([df, novo], ignore_index=True)
                    salvar_csv(df, ARQUIVO_MODELOS_BGR)

                    st.success("Modelo BGR enviado com sucesso!")
                else:
                    st.warning("Preencha nome, departamento e selecione uma imagem de prévia.")

    with aba3:
        st.subheader("📑 Histórico de Escolhas BGR")

        df = carregar_csv(ARQUIVO_ESCOLHAS_BGR)

        if df.empty:
            st.info("Nenhuma escolha registrada ainda.")
        else:
            col1, col2 = st.columns(2)

            with col1:
                filtro_departamento = st.selectbox(
                    "Filtrar departamento:",
                    ["Todos"] + DEPARTAMENTOS,
                    key="hist_dep_admin"
                )

            with col2:
                busca_cliente = st.text_input(
                    "Buscar cliente:",
                    key="busca_cliente_admin"
                )

            df_filtrado = df.copy()

            if filtro_departamento != "Todos":
                df_filtrado = df_filtrado[
                    df_filtrado["departamento"] == filtro_departamento
                ]

            if busca_cliente:
                df_filtrado = df_filtrado[
                    df_filtrado["cliente"].str.contains(
                        busca_cliente,
                        case=False,
                        na=False
                    )
                ]

            st.dataframe(df_filtrado, use_container_width=True)

            excel = gerar_excel_download({
                "Historico_BGR": df_filtrado
            })

            st.download_button(
                label="📥 Exportar histórico para Excel",
                data=excel,
                file_name="historico_escolhas_bgr.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

    with aba4:
        st.subheader("📋 Gerenciar cadastros")

        tipo_dado = st.selectbox(
            "Selecione a base:",
            [
                "Conversores",
                "Modelos BGR",
                "Histórico de Escolhas"
            ]
        )

        if tipo_dado == "Conversores":
            arquivo_base = ARQUIVO_CONVERSORES
        elif tipo_dado == "Modelos BGR":
            arquivo_base = ARQUIVO_MODELOS_BGR
        else:
            arquivo_base = ARQUIVO_ESCOLHAS_BGR

        df_base = carregar_csv(arquivo_base)

        st.write("Edite os dados diretamente na tabela abaixo:")

        df_editado = st.data_editor(
            df_base,
            use_container_width=True,
            num_rows="dynamic"
        )

        if st.button("Salvar alterações"):
            salvar_csv(df_editado, arquivo_base)
            st.success("Alterações salvas com sucesso!")

    with aba5:
        st.subheader("📦 Exportar bases para Excel")

        df_conversores = carregar_csv(ARQUIVO_CONVERSORES)
        df_modelos = carregar_csv(ARQUIVO_MODELOS_BGR)
        df_escolhas = carregar_csv(ARQUIVO_ESCOLHAS_BGR)

        excel = gerar_excel_download({
            "Conversores": df_conversores,
            "Modelos_BGR": df_modelos,
            "Escolhas_BGR": df_escolhas
        })

        st.download_button(
            label="📥 Baixar todas as bases em Excel",
            data=excel,
            file_name="bases_portal_ferramentas.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
