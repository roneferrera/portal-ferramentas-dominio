import streamlit as st
import pandas as pd
import unicodedata
import re
from datetime import datetime
from io import BytesIO
from supabase import create_client, Client

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

BUCKET_IMAGENS = "imagens-bgr"
BUCKET_BGR     = "arquivos-bgr"

# =========================================================
# ESTILO VISUAL
# =========================================================

st.markdown("""
<style>
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
    --tr-danger-bg: rgba(211, 47, 47, 0.22);
    --tr-danger-text: #EF9A9A;
}
.stApp { background-color: var(--tr-bg-main); color: var(--tr-text-main); }
.block-container { padding-top: 1.5rem; padding-bottom: 3rem; }
html, body, [class*="css"] { font-family: Arial, Helvetica, sans-serif; }
p, span, label, div { color: var(--tr-text-secondary); }
h1 { color: var(--tr-text-main); font-weight: 700; border-left: 6px solid var(--tr-orange); padding-left: 14px; }
h2, h3, h4 { color: var(--tr-text-main); }
section[data-testid="stSidebar"] { background-color: var(--tr-bg-sidebar); border-right: 1px solid var(--tr-border); }
section[data-testid="stSidebar"] h1,
section[data-testid="stSidebar"] h2,
section[data-testid="stSidebar"] h3,
section[data-testid="stSidebar"] label,
section[data-testid="stSidebar"] p,
section[data-testid="stSidebar"] span,
section[data-testid="stSidebar"] div { color: var(--tr-text-secondary); }
section[data-testid="stSidebar"] hr { border-color: var(--tr-border); }
.card { padding: 24px; border-radius: 14px; background-color: var(--tr-bg-card); border: 1px solid var(--tr-border); margin-bottom: 18px; box-shadow: 0 4px 16px rgba(0,0,0,0.35); transition: all 0.2s ease-in-out; }
.card:hover { background-color: var(--tr-bg-card-hover); border-color: var(--tr-orange); box-shadow: 0 6px 20px rgba(255,128,0,0.18); }
.card h3 { margin-top: 0; color: var(--tr-text-main); }
.card p { color: var(--tr-text-secondary); }
.botao-link { display: inline-block; background-color: var(--tr-orange); color: #FFFFFF !important; padding: 10px 18px; border-radius: 8px; text-decoration: none; font-weight: 700; margin-top: 10px; }
.botao-link:hover { background-color: var(--tr-orange-dark); color: #FFFFFF !important; }
.stButton > button, .stDownloadButton > button { background-color: var(--tr-orange); color: #FFFFFF; border: 1px solid var(--tr-orange); border-radius: 8px; font-weight: 700; }
.stButton > button:hover, .stDownloadButton > button:hover { background-color: var(--tr-orange-dark); color: #FFFFFF; border-color: var(--tr-orange-dark); }
.stTextInput input, .stTextArea textarea { background-color: var(--tr-bg-input); color: var(--tr-text-main); border: 1px solid var(--tr-border-light); border-radius: 8px; }
.stTextInput input::placeholder, .stTextArea textarea::placeholder { color: var(--tr-text-muted); }
.stTextInput input:focus, .stTextArea textarea:focus { border-color: var(--tr-orange) !important; box-shadow: 0 0 0 1px var(--tr-orange) !important; }
.stSelectbox div[data-baseweb="select"] { background-color: var(--tr-bg-input); color: var(--tr-text-main); border-radius: 8px; }
.stRadio label, .stCheckbox label { color: var(--tr-text-secondary); }
.status-ativo { display: inline-block; padding: 5px 11px; border-radius: 999px; background-color: var(--tr-success-bg); color: var(--tr-success-text); font-weight: 700; font-size: 13px; }
.status-manutencao { display: inline-block; padding: 5px 11px; border-radius: 999px; background-color: var(--tr-warning-bg); color: var(--tr-warning-text); font-weight: 700; font-size: 13px; }
.status-desenvolvimento { display: inline-block; padding: 5px 11px; border-radius: 999px; background-color: var(--tr-info-bg); color: var(--tr-info-text); font-weight: 700; font-size: 13px; }
.setor-card { padding: 22px; border-radius: 14px; background-color: var(--tr-bg-card); border: 1px solid var(--tr-border); text-align: center; box-shadow: 0 4px 16px rgba(0,0,0,0.35); min-height: 140px; transition: all 0.2s ease-in-out; }
.setor-card:hover { background-color: var(--tr-bg-card-hover); border-color: var(--tr-orange); transform: translateY(-2px); box-shadow: 0 6px 20px rgba(255,128,0,0.18); }
.setor-card h1 { border-left: none; padding-left: 0; color: var(--tr-orange); }
.setor-card h4 { color: var(--tr-text-main); margin-bottom: 4px; }
.setor-card p { color: var(--tr-text-muted); }
.aviso-admin { padding: 14px; border-radius: 10px; background-color: var(--tr-warning-bg); color: var(--tr-warning-text); border: 1px solid var(--tr-orange); }
.aviso-admin strong { color: var(--tr-warning-text); }
[data-testid="stMetric"] { background-color: var(--tr-bg-card); border: 1px solid var(--tr-border); border-radius: 14px; padding: 18px; box-shadow: 0 4px 16px rgba(0,0,0,0.35); }
[data-testid="stMetricLabel"] { color: var(--tr-text-muted); }
[data-testid="stMetricValue"] { color: var(--tr-orange); font-weight: 700; }
.stTabs [data-baseweb="tab-list"] { gap: 8px; border-bottom: 1px solid var(--tr-border); }
.stTabs [data-baseweb="tab"] { background-color: var(--tr-bg-card); border-radius: 8px 8px 0 0; color: var(--tr-text-secondary); border: 1px solid var(--tr-border); padding: 10px 16px; }
.stTabs [aria-selected="true"] { background-color: var(--tr-orange-soft); color: var(--tr-orange); border-bottom: 3px solid var(--tr-orange); font-weight: 700; }
[data-testid="stDataFrame"] { border: 1px solid var(--tr-border); border-radius: 10px; background-color: var(--tr-bg-card); }
div[data-testid="stAlert"] { border-radius: 10px; border: 1px solid var(--tr-border); }
div[data-testid="stExpander"] { background-color: var(--tr-bg-card); border: 1px solid var(--tr-border); border-radius: 10px; }
[data-testid="stFileUploader"] { background-color: var(--tr-bg-card); border: 1px dashed var(--tr-border-light); border-radius: 12px; padding: 12px; }
hr { border-color: var(--tr-border); }
a { color: var(--tr-orange); }
a:hover { color: var(--tr-orange-dark); }
</style>
""", unsafe_allow_html=True)

# =========================================================
# SUPABASE — CONEXÃO
# =========================================================

@st.cache_resource
def get_supabase() -> Client:
    return create_client(
        "https://hylhbsrckmygluiykdur.supabase.co",
        st.secrets["SUPABASE_KEY"]
    )

# =========================================================
# SUPABASE — BANCO DE DADOS
# =========================================================

def carregar_tabela(tabela: str) -> pd.DataFrame:
    try:
        sb = get_supabase()
        response = sb.table(tabela).select("*").execute()
        if response.data:
            return pd.DataFrame(response.data)
        return pd.DataFrame()
    except Exception as e:
        st.error(f"Erro ao carregar '{tabela}': {e}")
        return pd.DataFrame()


def inserir_registro(tabela: str, dados: dict):
    try:
        sb = get_supabase()
        sb.table(tabela).insert(dados).execute()
    except Exception as e:
        st.error(f"Erro ao inserir em '{tabela}': {e}")


def atualizar_registro(tabela: str, id_registro: int, dados: dict):
    try:
        sb = get_supabase()
        sb.table(tabela).update(dados).eq("id", id_registro).execute()
    except Exception as e:
        st.error(f"Erro ao atualizar em '{tabela}': {e}")


def excluir_registro(tabela: str, id_registro: int):
    try:
        sb = get_supabase()
        sb.table(tabela).delete().eq("id", id_registro).execute()
    except Exception as e:
        st.error(f"Erro ao excluir em '{tabela}': {e}")


def salvar_tabela_completa(tabela: str, df: pd.DataFrame):
    try:
        sb = get_supabase()
        existentes = sb.table(tabela).select("id").execute()
        for row in existentes.data:
            sb.table(tabela).delete().eq("id", row["id"]).execute()
        df_limpo = df.drop(columns=["id"], errors="ignore")
        for _, row in df_limpo.iterrows():
            registro = {k: (None if pd.isna(v) else v) for k, v in row.items()}
            sb.table(tabela).insert(registro).execute()
        st.success("Alterações salvas com sucesso no Supabase!")
    except Exception as e:
        st.error(f"Erro ao salvar '{tabela}': {e}")

# =========================================================
# SUPABASE — STORAGE
# =========================================================

def upload_arquivo(bucket: str, nome_arquivo: str, bytes_arquivo: bytes, content_type: str) -> str | None:
    try:
        sb = get_supabase()
        try:
            sb.storage.from_(bucket).remove([nome_arquivo])
        except Exception:
            pass
        sb.storage.from_(bucket).upload(
            path=nome_arquivo,
            file=bytes_arquivo,
            file_options={"content-type": content_type, "upsert": "true"}
        )
        return sb.storage.from_(bucket).get_public_url(nome_arquivo)
    except Exception as e:
        st.error(f"Erro no upload '{bucket}/{nome_arquivo}': {e}")
        return None


def baixar_arquivo(bucket: str, nome_arquivo: str) -> bytes | None:
    try:
        sb = get_supabase()
        return sb.storage.from_(bucket).download(nome_arquivo)
    except Exception:
        return None


def url_publica(bucket: str, nome_arquivo: str) -> str:
    try:
        sb = get_supabase()
        return sb.storage.from_(bucket).get_public_url(nome_arquivo)
    except Exception:
        return ""

# =========================================================
# AUDITORIA
# =========================================================

def registrar_auditoria(acao: str, tabela: str, descricao: str, dados_antes: str = "", dados_depois: str = ""):
    try:
        inserir_registro("auditoria", {
            "data_hora":    datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
            "acao":         acao,
            "tabela":       tabela,
            "descricao":    descricao,
            "dados_antes":  dados_antes,
            "dados_depois": dados_depois
        })
    except Exception as e:
        st.warning(f"Auditoria não registrada: {e}")

# =========================================================
# FUNÇÕES AUXILIARES
# =========================================================

def inicializar_conversores_padrao():
    df = carregar_tabela("conversores")
    if not df.empty:
        return
    conversores_padrao = [
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
        },
    ]
    for c in conversores_padrao:
        inserir_registro("conversores", c)


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
    st.sidebar.markdown("### 🧩 Portal de Ferramentas")


def nome_arquivo_seguro(nome_arquivo: str) -> str:
    nome = unicodedata.normalize("NFKD", nome_arquivo)
    nome = "".join(c for c in nome if not unicodedata.combining(c))
    nome = re.sub(r"[^\w\.\-]", "_", nome)
    partes = nome.rsplit(".", 1)
    if len(partes) == 2:
        nome = partes[0].replace(".", "_") + "." + partes[1]
    return nome


def valor_texto(valor):
    if valor is None:
        return ""
    if isinstance(valor, float) and pd.isna(valor):
        return ""
    return str(valor).strip()


def email_valido(email):
    email = str(email).strip()
    return "@" in email and "." in email

# =========================================================
# INICIALIZAÇÃO
# =========================================================

inicializar_conversores_padrao()
mostrar_logo()

# =========================================================
# MENU LATERAL
# =========================================================

st.sidebar.write("---")
st.sidebar.subheader("Menu público")

pagina_publica = st.sidebar.radio(
    "Selecione uma opção:",
    ["Início", "Conversores", "Relatórios BGR"]
)

st.sidebar.write("---")
st.sidebar.subheader("Área administrativa")

abrir_admin = st.sidebar.checkbox("Abrir Painel Administrativo")

pagina = "Painel Administrativo" if abrir_admin else pagina_publica

# =========================================================
# PÁGINA INÍCIO
# =========================================================

if pagina == "Início":
    st.title("🧩 Portal de Ferramentas")
    st.write("Central de conversores, relatórios BGR e ferramentas internas por departamento.")

    df_conversores  = carregar_tabela("conversores")
    df_modelos      = carregar_tabela("modelos_bgr")
    df_solicitacoes = carregar_tabela("solicitacoes_bgr")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Conversores cadastrados", len(df_conversores))
    with col2:
        st.metric("Modelos BGR cadastrados", len(df_modelos))
    with col3:
        st.metric("Solicitações BGR", len(df_solicitacoes))

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
            qtd = (
                len(df_conversores[df_conversores["departamento"] == dep])
                if not df_conversores.empty else 0
            )
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

    df = carregar_tabela("conversores")

    col1, col2 = st.columns(2)
    with col1:
        filtro_departamento = st.selectbox("Filtrar por departamento:", ["Todos"] + DEPARTAMENTOS)
    with col2:
        filtro_status = st.selectbox("Filtrar por status:", ["Todos"] + STATUS_FERRAMENTAS)

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

            if row["status"] == "Ativo" and valor_texto(row.get("url", "")):
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

    df_modelos = carregar_tabela("modelos_bgr")

    st.write(
        "Consulte os modelos BGR disponíveis. Para baixar o arquivo `.bgr`, "
        "informe seus dados para registro da solicitação."
    )

    col_filtro1, col_filtro2 = st.columns([1, 2])
    with col_filtro1:
        departamento = st.selectbox("Selecione o departamento:", DEPARTAMENTOS)
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
            nome_modelo      = valor_texto(modelo_info.get("nome", ""))
            descricao_modelo = valor_texto(modelo_info.get("descricao", ""))
            nome_imagem      = valor_texto(modelo_info.get("imagem", ""))
            nome_bgr         = valor_texto(modelo_info.get("arquivo_bgr", ""))

            st.markdown("<div class='card'>", unsafe_allow_html=True)
            col_img, col_desc, col_acao = st.columns([1.2, 2.5, 1.2])

            with col_img:
                st.markdown(f"### {nome_modelo}")
                if nome_imagem:
                    img_url = url_publica(BUCKET_IMAGENS, nome_imagem)
                    if img_url:
                        st.image(img_url, caption="Prévia", width=220)
                        with st.expander("🔍 Ver imagem maior"):
                            st.image(img_url, caption=nome_modelo, use_container_width=True)
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

            with col_acao:
                st.markdown("#### Acesso")
                if nome_bgr:
                    if st.button("Solicitar acesso", key=f"solicitar_modelo_{index}"):
                        st.session_state["modelo_bgr_solicitado"]       = nome_modelo
                        st.session_state["arquivo_bgr_solicitado"]      = nome_bgr
                        st.session_state["departamento_bgr_solicitado"] = departamento
                        st.session_state["download_bgr_liberado"]       = False
                        st.success("Modelo selecionado. Preencha os dados abaixo.")
                else:
                    st.info("Sem arquivo .BGR cadastrado.")

            st.markdown("</div>", unsafe_allow_html=True)
            st.write("")

        st.write("---")
        st.subheader("Solicitar acesso ao modelo BGR")

        modelo_solicitado       = st.session_state.get("modelo_bgr_solicitado", "")
        arquivo_solicitado      = st.session_state.get("arquivo_bgr_solicitado", "")
        departamento_solicitado = st.session_state.get("departamento_bgr_solicitado", "")

        if modelo_solicitado:
            st.info(f"Modelo selecionado: **{modelo_solicitado}**")
        else:
            st.warning("Selecione um modelo acima antes de solicitar o acesso.")

        with st.form("form_solicitacao_bgr"):
            nome_usuario           = st.text_input("Nome")
            email_usuario          = st.text_input("E-mail")
            cnpj                   = st.text_input("CNPJ")
            codigo_cliente_dominio = st.text_input("Código cliente Domínio")
            observacao             = st.text_area("Observações")

            confirmar = st.form_submit_button("Registrar e liberar download")

            if confirmar:
                if not modelo_solicitado:
                    st.warning("Selecione um modelo BGR antes de confirmar.")
                elif not nome_usuario:
                    st.warning("Informe o nome.")
                elif not email_usuario:
                    st.warning("Informe o e-mail.")
                elif not email_valido(email_usuario):
                    st.warning("Informe um e-mail válido.")
                elif not cnpj:
                    st.warning("Informe o CNPJ.")
                elif not codigo_cliente_dominio:
                    st.warning("Informe o código cliente Domínio.")
                else:
                    inserir_registro("solicitacoes_bgr", {
                        "data_hora":               datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
                        "nome_usuario":            nome_usuario,
                        "email_usuario":           email_usuario,
                        "cnpj":                    cnpj,
                        "codigo_cliente_dominio":  codigo_cliente_dominio,
                        "departamento":            departamento_solicitado,
                        "modelo":                  modelo_solicitado,
                        "arquivo_bgr":             arquivo_solicitado,
                        "observacao":              observacao,
                        "status":                  "Liberado"
                    })
                    st.session_state["download_bgr_liberado"] = True
                    st.success("Solicitação registrada com sucesso. Download liberado.")

        if st.session_state.get("download_bgr_liberado", False) and arquivo_solicitado:
            bgr_bytes = baixar_arquivo(BUCKET_BGR, arquivo_solicitado)
            if bgr_bytes:
                st.download_button(
                    label="📥 Baixar .BGR",
                    data=bgr_bytes,
                    file_name=arquivo_solicitado,
                    mime="application/octet-stream",
                    key="download_bgr_liberado_btn"
                )
            else:
                st.warning("Arquivo .BGR não encontrado no storage.")

# =========================================================
# PAINEL ADMINISTRATIVO
# =========================================================

elif pagina == "Painel Administrativo":
    st.title("⚙️ Painel Administrativo")

    st.markdown("""
    <div class="aviso-admin">
        <strong>Atenção:</strong> esta versão está sem login. O painel administrativo está separado
        do menu público, mas ainda não possui senha.
    </div>
    """, unsafe_allow_html=True)

    st.write("")

    aba1, aba2, aba3, aba4, aba5, aba6, aba7, aba8 = st.tabs([
        "Cadastrar Conversor",
        "Upload Modelo BGR",
        "Editar / Excluir Conversores",
        "Editar / Excluir BGR",
        "Solicitações BGR",
        "Gerenciar Dados",
        "Exportações",
        "Auditoria"
    ])

    # -----------------------------------------------------
    # ABA 1 - CADASTRAR CONVERSOR
    # -----------------------------------------------------

    with aba1:
        st.subheader("➕ Cadastrar novo conversor")

        with st.form("form_conversor"):
            nome         = st.text_input("Nome do conversor")
            departamento = st.selectbox("Departamento", DEPARTAMENTOS)
            descricao    = st.text_area("Descrição")
            url          = st.text_input("URL do conversor")
            status       = st.selectbox("Status", STATUS_FERRAMENTAS)

            enviar = st.form_submit_button("Cadastrar conversor")

            if enviar:
                if nome and departamento and descricao:
                    dados = {
                        "nome":          nome,
                        "departamento":  departamento,
                        "descricao":     descricao,
                        "url":           url,
                        "status":        status,
                        "data_cadastro": datetime.now().strftime("%d/%m/%Y %H:%M:%S")
                    }
                    inserir_registro("conversores", dados)
                    registrar_auditoria(
                        acao="CADASTRO",
                        tabela="conversores",
                        descricao=f"Novo conversor cadastrado: {nome}",
                        dados_depois=str(dados)
                    )
                    st.success("Conversor cadastrado com sucesso!")
                else:
                    st.warning("Preencha nome, departamento e descrição.")

    # -----------------------------------------------------
    # ABA 2 - UPLOAD MODELO BGR
    # -----------------------------------------------------

    with aba2:
        st.subheader("📤 Upload de modelo BGR")
        st.write(
            "Cadastre uma imagem de prévia do relatório e, se desejar, "
            "o arquivo `.bgr` correspondente."
        )

        with st.form("form_bgr"):
            nome_modelo         = st.text_input("Nome do modelo BGR")
            departamento_modelo = st.selectbox("Departamento do modelo", DEPARTAMENTOS)
            descricao_modelo    = st.text_area("Descrição do modelo")
            status_modelo       = st.selectbox("Status do modelo", STATUS_FERRAMENTAS)

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

                    nome_imagem_salva = f"{timestamp}_{nome_arquivo_seguro(imagem.name)}"
                    ext               = imagem.name.split(".")[-1].lower()
                    content_type_img  = "image/jpeg" if ext == "jpg" else f"image/{ext}"

                    url_img = upload_arquivo(
                        BUCKET_IMAGENS,
                        nome_imagem_salva,
                        imagem.getbuffer().tobytes(),
                        content_type_img
                    )

                    nome_bgr_salvo = ""
                    if arquivo_bgr is not None:
                        nome_bgr_salvo = f"{timestamp}_{nome_arquivo_seguro(arquivo_bgr.name)}"
                        upload_arquivo(
                            BUCKET_BGR,
                            nome_bgr_salvo,
                            arquivo_bgr.getbuffer().tobytes(),
                            "application/octet-stream"
                        )

                    if url_img:
                        dados_bgr = {
                            "nome":         nome_modelo,
                            "departamento": departamento_modelo,
                            "descricao":    descricao_modelo,
                            "imagem":       nome_imagem_salva,
                            "arquivo_bgr":  nome_bgr_salvo,
                            "status":       status_modelo,
                            "data_upload":  datetime.now().strftime("%d/%m/%Y %H:%M:%S")
                        }
                        inserir_registro("modelos_bgr", dados_bgr)
                        registrar_auditoria(
                            acao="UPLOAD",
                            tabela="modelos_bgr",
                            descricao=f"Novo modelo BGR cadastrado: {nome_modelo}",
                            dados_depois=str(dados_bgr)
                        )
                        st.success("Modelo BGR enviado com sucesso!")
                    else:
                        st.error("Falha no upload da imagem. Verifique o bucket no Supabase.")
                else:
                    st.warning("Preencha nome, departamento e selecione uma imagem de prévia.")

    # -----------------------------------------------------
    # ABA 3 - EDITAR / EXCLUIR CONVERSORES
    # -----------------------------------------------------

    with aba3:
        st.subheader("✏️ Editar ou Excluir Conversores")

        df_conv = carregar_tabela("conversores")

        if df_conv.empty:
            st.info("Nenhum conversor cadastrado.")
        else:
            nomes_conv = df_conv["nome"].tolist()
            selecionado_conv = st.selectbox(
                "Selecione o conversor:",
                nomes_conv,
                key="sel_editar_conv"
            )

            linha_conv = df_conv[df_conv["nome"] == selecionado_conv].iloc[0]
            id_conv    = int(linha_conv["id"])

            st.write("---")
            col_edit, col_excluir = st.columns([3, 1])

            with col_edit:
                st.markdown("#### ✏️ Editar conversor")
                with st.form("form_editar_conversor"):
                    novo_nome  = st.text_input("Nome", value=valor_texto(linha_conv["nome"]))
                    novo_dep   = st.selectbox(
                        "Departamento",
                        DEPARTAMENTOS,
                        index=DEPARTAMENTOS.index(linha_conv["departamento"])
                        if linha_conv["departamento"] in DEPARTAMENTOS else 0
                    )
                    nova_desc  = st.text_area("Descrição", value=valor_texto(linha_conv["descricao"]))
                    nova_url   = st.text_input("URL", value=valor_texto(linha_conv.get("url", "")))
                    novo_status = st.selectbox(
                        "Status",
                        STATUS_FERRAMENTAS,
                        index=STATUS_FERRAMENTAS.index(linha_conv["status"])
                        if linha_conv["status"] in STATUS_FERRAMENTAS else 0
                    )
                    salvar_conv = st.form_submit_button("💾 Salvar alterações")

                    if salvar_conv:
                        dados_antes  = str(linha_conv.to_dict())
                        dados_novos  = {
                            "nome":         novo_nome,
                            "departamento": novo_dep,
                            "descricao":    nova_desc,
                            "url":          nova_url,
                            "status":       novo_status
                        }
                        atualizar_registro("conversores", id_conv, dados_novos)
                        registrar_auditoria(
                            acao="EDIÇÃO",
                            tabela="conversores",
                            descricao=f"Conversor editado: {selecionado_conv}",
                            dados_antes=dados_antes,
                            dados_depois=str(dados_novos)
                        )
                        st.success("Conversor atualizado com sucesso!")
                        st.rerun()

            with col_excluir:
                st.markdown("#### 🗑️ Excluir conversor")
                st.warning(f"Você está prestes a excluir:\n\n**{selecionado_conv}**")
                confirmar_excluir = st.checkbox("Confirmar exclusão", key="confirm_excluir_conv")
                if st.button("🗑️ Excluir", key="btn_excluir_conv"):
                    if confirmar_excluir:
                        dados_antes = str(linha_conv.to_dict())
                        excluir_registro("conversores", id_conv)
                        registrar_auditoria(
                            acao="EXCLUSÃO",
                            tabela="conversores",
                            descricao=f"Conversor excluído: {selecionado_conv}",
                            dados_antes=dados_antes
                        )
                        st.success("Conversor excluído com sucesso!")
                        st.rerun()
                    else:
                        st.error("Marque a caixa de confirmação antes de excluir.")

    # -----------------------------------------------------
    # ABA 4 - EDITAR / EXCLUIR BGR
    # -----------------------------------------------------

    with aba4:
        st.subheader("✏️ Editar ou Excluir Modelos BGR")

        df_bgr = carregar_tabela("modelos_bgr")

        if df_bgr.empty:
            st.info("Nenhum modelo BGR cadastrado.")
        else:
            nomes_bgr = df_bgr["nome"].tolist()
            selecionado_bgr = st.selectbox(
                "Selecione o modelo BGR:",
                nomes_bgr,
                key="sel_editar_bgr"
            )

            linha_bgr = df_bgr[df_bgr["nome"] == selecionado_bgr].iloc[0]
            id_bgr    = int(linha_bgr["id"])

            st.write("---")
            col_edit_bgr, col_excluir_bgr = st.columns([3, 1])

            with col_edit_bgr:
                st.markdown("#### ✏️ Editar modelo BGR")

                # Mostra imagem atual
                nome_img_atual = valor_texto(linha_bgr.get("imagem", ""))
                if nome_img_atual:
                    img_url_atual = url_publica(BUCKET_IMAGENS, nome_img_atual)
                    if img_url_atual:
                        st.image(img_url_atual, caption="Imagem atual", width=200)

                with st.form("form_editar_bgr"):
                    novo_nome_bgr  = st.text_input("Nome", value=valor_texto(linha_bgr["nome"]))
                    novo_dep_bgr   = st.selectbox(
                        "Departamento",
                        DEPARTAMENTOS,
                        index=DEPARTAMENTOS.index(linha_bgr["departamento"])
                        if linha_bgr["departamento"] in DEPARTAMENTOS else 0
                    )
                    nova_desc_bgr  = st.text_area("Descrição", value=valor_texto(linha_bgr["descricao"]))
                    novo_status_bgr = st.selectbox(
                        "Status",
                        STATUS_FERRAMENTAS,
                        index=STATUS_FERRAMENTAS.index(linha_bgr["status"])
                        if linha_bgr["status"] in STATUS_FERRAMENTAS else 0
                    )

                    st.markdown("**Substituir imagem** (opcional — deixe em branco para manter a atual):")
                    nova_imagem = st.file_uploader(
                        "Nova imagem de prévia",
                        type=["png", "jpg", "jpeg"],
                        key="nova_img_bgr"
                    )

                    st.markdown("**Substituir arquivo .BGR** (opcional — deixe em branco para manter o atual):")
                    novo_arquivo_bgr = st.file_uploader(
                        "Novo arquivo .BGR",
                        type=["bgr"],
                        key="novo_arquivo_bgr"
                    )

                    salvar_bgr = st.form_submit_button("💾 Salvar alterações")

                    if salvar_bgr:
                        dados_antes   = str(linha_bgr.to_dict())
                        timestamp     = datetime.now().strftime("%Y%m%d%H%M%S")

                        nome_imagem_final = nome_img_atual
                        if nova_imagem is not None:
                            nome_imagem_final = f"{timestamp}_{nome_arquivo_seguro(nova_imagem.name)}"
                            ext_img           = nova_imagem.name.split(".")[-1].lower()
                            ct_img            = "image/jpeg" if ext_img == "jpg" else f"image/{ext_img}"
                            upload_arquivo(BUCKET_IMAGENS, nome_imagem_final, nova_imagem.getbuffer().tobytes(), ct_img)

                        nome_bgr_final = valor_texto(linha_bgr.get("arquivo_bgr", ""))
                        if novo_arquivo_bgr is not None:
                            nome_bgr_final = f"{timestamp}_{nome_arquivo_seguro(novo_arquivo_bgr.name)}"
                            upload_arquivo(BUCKET_BGR, nome_bgr_final, novo_arquivo_bgr.getbuffer().tobytes(), "application/octet-stream")

                        dados_novos_bgr = {
                            "nome":         novo_nome_bgr,
                            "departamento": novo_dep_bgr,
                            "descricao":    nova_desc_bgr,
                            "status":       novo_status_bgr,
                            "imagem":       nome_imagem_final,
                            "arquivo_bgr":  nome_bgr_final
                        }
                        atualizar_registro("modelos_bgr", id_bgr, dados_novos_bgr)
                        registrar_auditoria(
                            acao="EDIÇÃO",
                            tabela="modelos_bgr",
                            descricao=f"Modelo BGR editado: {selecionado_bgr}",
                            dados_antes=dados_antes,
                            dados_depois=str(dados_novos_bgr)
                        )
                        st.success("Modelo BGR atualizado com sucesso!")
                        st.rerun()

            with col_excluir_bgr:
                st.markdown("#### 🗑️ Excluir modelo BGR")
                st.warning(f"Você está prestes a excluir:\n\n**{selecionado_bgr}**")
                confirmar_excluir_bgr = st.checkbox("Confirmar exclusão", key="confirm_excluir_bgr")
                if st.button("🗑️ Excluir", key="btn_excluir_bgr"):
                    if confirmar_excluir_bgr:
                        dados_antes = str(linha_bgr.to_dict())
                        excluir_registro("modelos_bgr", id_bgr)
                        registrar_auditoria(
                            acao="EXCLUSÃO",
                            tabela="modelos_bgr",
                            descricao=f"Modelo BGR excluído: {selecionado_bgr}",
                            dados_antes=dados_antes
                        )
                        st.success("Modelo BGR excluído com sucesso!")
                        st.rerun()
                    else:
                        st.error("Marque a caixa de confirmação antes de excluir.")

    # -----------------------------------------------------
    # ABA 5 - SOLICITAÇÕES BGR
    # -----------------------------------------------------

    with aba5:
        st.subheader("📥 Solicitações de acesso aos BGR")

        df = carregar_tabela("solicitacoes_bgr")

        if df.empty:
            st.info("Nenhuma solicitação registrada ainda.")
        else:
            col1, col2, col3 = st.columns(3)
            with col1:
                filtro_departamento = st.selectbox(
                    "Filtrar departamento:",
                    ["Todos"] + DEPARTAMENTOS,
                    key="sol_dep_admin"
                )
            with col2:
                busca_cnpj = st.text_input("Buscar CNPJ:", key="sol_cnpj_admin")
            with col3:
                busca_email = st.text_input("Buscar e-mail:", key="sol_email_admin")

            df_filtrado = df.copy()
            if filtro_departamento != "Todos":
                df_filtrado = df_filtrado[df_filtrado["departamento"] == filtro_departamento]
            if busca_cnpj:
                df_filtrado = df_filtrado[
                    df_filtrado["cnpj"].astype(str).str.contains(busca_cnpj, case=False, na=False)
                ]
            if busca_email:
                df_filtrado = df_filtrado[
                    df_filtrado["email_usuario"].astype(str).str.contains(busca_email, case=False, na=False)
                ]

            st.dataframe(df_filtrado, use_container_width=True)

            excel = gerar_excel_download({"Solicitacoes_BGR": df_filtrado})
            st.download_button(
                label="📥 Exportar solicitações para Excel",
                data=excel,
                file_name="solicitacoes_bgr.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

    # -----------------------------------------------------
    # ABA 6 - GERENCIAR DADOS
    # -----------------------------------------------------

    with aba6:
        st.subheader("📋 Gerenciar cadastros")

        tipo_dado = st.selectbox(
            "Selecione a base:",
            ["Conversores", "Modelos BGR", "Solicitações BGR"]
        )

        mapa_tabelas = {
            "Conversores":      "conversores",
            "Modelos BGR":      "modelos_bgr",
            "Solicitações BGR": "solicitacoes_bgr",
        }

        nome_tabela = mapa_tabelas[tipo_dado]
        df_base     = carregar_tabela(nome_tabela)

        st.write("Edite os dados diretamente na tabela abaixo:")

        df_editado = st.data_editor(
            df_base,
            use_container_width=True,
            num_rows="dynamic"
        )

        if st.button("Salvar alterações"):
            salvar_tabela_completa(nome_tabela, df_editado)
            registrar_auditoria(
                acao="EDIÇÃO EM MASSA",
                tabela=nome_tabela,
                descricao=f"Edição em massa via Gerenciar Dados na tabela: {nome_tabela}"
            )

    # -----------------------------------------------------
    # ABA 7 - EXPORTAÇÕES
    # -----------------------------------------------------

    with aba7:
        st.subheader("📦 Exportar bases para Excel")

        df_conversores  = carregar_tabela("conversores")
        df_modelos      = carregar_tabela("modelos_bgr")
        df_solicitacoes = carregar_tabela("solicitacoes_bgr")
        df_auditoria    = carregar_tabela("auditoria")

        excel = gerar_excel_download({
            "Conversores":      df_conversores,
            "Modelos_BGR":      df_modelos,
            "Solicitacoes_BGR": df_solicitacoes,
            "Auditoria":        df_auditoria
        })

        st.download_button(
            label="📥 Baixar todas as bases em Excel",
            data=excel,
            file_name="bases_portal_ferramentas.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

        registrar_auditoria(
            acao="EXPORTAÇÃO",
            tabela="todas",
            descricao="Exportação completa das bases para Excel"
        )

    # -----------------------------------------------------
    # ABA 8 - AUDITORIA
    # -----------------------------------------------------

    with aba8:
        st.subheader("🔍 Auditoria de Movimentações")

        df_audit = carregar_tabela("auditoria")

        if df_audit.empty:
            st.info("Nenhuma movimentação registrada ainda.")
        else:
            col1, col2, col3 = st.columns(3)
            with col1:
                filtro_acao = st.selectbox(
                    "Filtrar por ação:",
                    ["Todas", "CADASTRO", "UPLOAD", "EDIÇÃO", "EDIÇÃO EM MASSA", "EXCLUSÃO", "EXPORTAÇÃO"],
                    key="audit_acao"
                )
            with col2:
                filtro_tabela_audit = st.selectbox(
                    "Filtrar por tabela:",
                    ["Todas", "conversores", "modelos_bgr", "solicitacoes_bgr", "todas"],
                    key="audit_tabela"
                )
            with col3:
                busca_descricao = st.text_input("Buscar na descrição:", key="audit_desc")

            df_audit_filtrado = df_audit.copy()

            if filtro_acao != "Todas":
                df_audit_filtrado = df_audit_filtrado[df_audit_filtrado["acao"] == filtro_acao]
            if filtro_tabela_audit != "Todas":
                df_audit_filtrado = df_audit_filtrado[df_audit_filtrado["tabela"] == filtro_tabela_audit]
            if busca_descricao:
                df_audit_filtrado = df_audit_filtrado[
                    df_audit_filtrado["descricao"].astype(str).str.contains(busca_descricao, case=False, na=False)
                ]

            st.write(f"**{len(df_audit_filtrado)} registro(s) encontrado(s)**")
            st.dataframe(df_audit_filtrado, use_container_width=True)

            st.write("---")
            excel_audit = gerar_excel_download({"Auditoria": df_audit_filtrado})
            st.download_button(
                label="📥 Exportar auditoria para Excel",
                data=excel_audit,
                file_name="auditoria_portal_ferramentas.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
