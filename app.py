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
.lixeira-restaurar { padding: 12px 16px; border-radius: 10px; background-color: var(--tr-danger-bg); border: 1px solid #c62828; margin-bottom: 10px; }
.lixeira-restaurar strong { color: var(--tr-danger-text); }
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


def excluir_varios(tabela: str, ids: list):
    for id_reg in ids:
        excluir_registro(tabela, id_reg)


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
# LIXEIRA — RESTAURAÇÃO
# =========================================================

def adicionar_lixeira(tabela: str, registro: dict):
    """Salva o registro na session_state para possível restauração."""
    if "lixeira" not in st.session_state:
        st.session_state["lixeira"] = []
    st.session_state["lixeira"].append({
        "tabela":    tabela,
        "registro":  registro,
        "excluido_em": datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    })


def mostrar_lixeira():
    """Exibe banner de restauração para exclusões recentes."""
    lixeira = st.session_state.get("lixeira", [])
    if not lixeira:
        return
    for i, item in enumerate(lixeira):
        nome_reg = item["registro"].get("nome", f"Registro #{i+1}")
        col_msg, col_restaurar, col_fechar = st.columns([5, 1.5, 1])
        with col_msg:
            st.markdown(
                f'<div class="lixeira-restaurar">🗑️ <strong>"{nome_reg}"</strong> foi excluído. '
                f'Excluído em: {item["excluido_em"]}</div>',
                unsafe_allow_html=True
            )
        with col_restaurar:
            if st.button("↩️ Restaurar", key=f"restaurar_{i}"):
                dados_sem_id = {k: v for k, v in item["registro"].items() if k != "id"}
                inserir_registro(item["tabela"], dados_sem_id)
                registrar_auditoria(
                    "RESTAURAÇÃO",
                    item["tabela"],
                    f"Registro restaurado: {nome_reg}",
                    dados_depois=str(dados_sem_id)
                )
                st.session_state["lixeira"].pop(i)
                st.success(f'"{nome_reg}" restaurado com sucesso!')
                st.rerun()
        with col_fechar:
            if st.button("✖ Fechar", key=f"fechar_lixeira_{i}"):
                st.session_state["lixeira"].pop(i)
                st.rerun()

# =========================================================
# FUNÇÕES AUXILIARES
# =========================================================

def inicializar_conversores_padrao():
    df = carregar_tabela("conversores")
    if not df.empty:
        return
    conversores_padrao = [
        {"nome": "Gerador RPA TXT", "departamento": "Folha de Pagamento", "descricao": "Gera arquivos TXT para processamento por RPA.", "url": "https://gerador-rpa-txt.streamlit.app/", "status": "Ativo", "data_cadastro": datetime.now().strftime("%d/%m/%Y %H:%M:%S")},
        {"nome": "Converte Bens Domínio", "departamento": "Patrimônio", "descricao": "Conversor de bens patrimoniais para leiaute compatível com Domínio.", "url": "https://convertebensdominio.streamlit.app/", "status": "Ativo", "data_cadastro": datetime.now().strftime("%d/%m/%Y %H:%M:%S")},
        {"nome": "Eventos Com Plano / Sem Plano", "departamento": "Fiscal", "descricao": "Ferramenta para tratar eventos com plano e sem plano.", "url": "https://eventos-complano-semplano.streamlit.app/", "status": "Ativo", "data_cadastro": datetime.now().strftime("%d/%m/%Y %H:%M:%S")},
        {"nome": "Clientes e Fornecedores - Conta Patrimonial", "departamento": "Contabilidade", "descricao": "Tratamento de clientes, fornecedores e contas patrimoniais.", "url": "https://clientes-fornecedores-conta-patrimonial.streamlit.app/", "status": "Ativo", "data_cadastro": datetime.now().strftime("%d/%m/%Y %H:%M:%S")},
        {"nome": "Conversor Leiaute com Separador Domínio", "departamento": "Fiscal", "descricao": "Conversor de leiaute com separador para o sistema Domínio.", "url": "https://conversorleiautecomseparadordominio.streamlit.app/", "status": "Ativo", "data_cadastro": datetime.now().strftime("%d/%m/%Y %H:%M:%S")},
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

    icones = {"Fiscal": "📊", "Folha de Pagamento": "👥", "Contabilidade": "📚", "Patrimônio": "🏢", "Honorários": "💰"}

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
                st.markdown(f'<a class="botao-link" href="{row["url"]}" target="_blank">Acessar ferramenta</a>', unsafe_allow_html=True)
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
    st.write("Consulte os modelos BGR disponíveis. Para baixar o arquivo `.bgr`, informe seus dados para registro da solicitação.")

    col_filtro1, col_filtro2 = st.columns([1, 2])
    with col_filtro1:
        departamento = st.selectbox("Selecione o departamento:", DEPARTAMENTOS)
    with col_filtro2:
        pesquisa = st.text_input("Pesquisar no nome ou descrição do BGR:", placeholder="Exemplo: folha, fiscal, impostos...")

    if not df_modelos.empty:
        df_dep = df_modelos[(df_modelos["departamento"] == departamento) & (df_modelos["status"] == "Ativo")].copy()
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
                        "data_hora": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
                        "nome_usuario": nome_usuario,
                        "email_usuario": email_usuario,
                        "cnpj": cnpj,
                        "codigo_cliente_dominio": codigo_cliente_dominio,
                        "departamento": departamento_solicitado,
                        "modelo": modelo_solicitado,
                        "arquivo_bgr": arquivo_solicitado,
                        "observacao": observacao,
                        "status": "Liberado"
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
        <strong>Atenção:</strong> esta versão está sem login. O painel administrativo está separado do menu público, mas ainda não possui senha.
    </div>
    """, unsafe_allow_html=True)

    st.write("")

    # Exibe banners de restauração no topo do painel
    mostrar_lixeira()

    aba1, aba2, aba3, aba4, aba5 = st.tabs([
        "🛠️ Conversores",
        "📄 Modelos BGR",
        "📥 Solicitações BGR",
        "📦 Exportações",
        "🔍 Auditoria"
    ])

    # =====================================================
    # ABA 1 — CONVERSORES
    # =====================================================

    with aba1:
        st.subheader("🛠️ Gerenciar Conversores")

        modo_conv     = st.session_state.get("modo_conv", "cadastro")
        editando_conv = st.session_state.get("editando_conv", None)

        # ---------- FORMULÁRIO EXPANSÍVEL ----------
        label_expander_conv = "✏️ Editando conversor — clique para expandir/recolher" if modo_conv == "edicao" else "➕ Cadastrar novo conversor — clique para expandir/recolher"
        expanded_conv       = st.session_state.get("expandir_form_conv", False)

        with st.expander(label_expander_conv, expanded=expanded_conv):

            if modo_conv == "edicao" and editando_conv is not None:
                df_conv_atual = carregar_tabela("conversores")
                linha = df_conv_atual[df_conv_atual["id"] == editando_conv]
                if linha.empty:
                    st.warning("Registro não encontrado.")
                    st.session_state["modo_conv"]    = "cadastro"
                    st.session_state["editando_conv"] = None
                    st.rerun()
                linha = linha.iloc[0]
            else:
                linha = None

            with st.form("form_conversor_principal"):
                col_f1, col_f2 = st.columns(2)
                with col_f1:
                    f_nome = st.text_input("Nome do conversor", value=valor_texto(linha["nome"]) if linha is not None else "")
                    f_dep  = st.selectbox("Departamento", DEPARTAMENTOS,
                        index=DEPARTAMENTOS.index(linha["departamento"]) if linha is not None and linha["departamento"] in DEPARTAMENTOS else 0)
                    f_url  = st.text_input("URL do conversor", value=valor_texto(linha.get("url", "")) if linha is not None else "")
                with col_f2:
                    f_desc   = st.text_area("Descrição", value=valor_texto(linha["descricao"]) if linha is not None else "", height=120)
                    f_status = st.selectbox("Status", STATUS_FERRAMENTAS,
                        index=STATUS_FERRAMENTAS.index(linha["status"]) if linha is not None and linha["status"] in STATUS_FERRAMENTAS else 0)

                col_btn1, col_btn2 = st.columns([1, 3])
                with col_btn1:
                    enviar_conv = st.form_submit_button("💾 Salvar" if modo_conv == "edicao" else "➕ Cadastrar")
                with col_btn2:
                    if modo_conv == "edicao":
                        cancelar_conv = st.form_submit_button("✖ Cancelar edição")
                        if cancelar_conv:
                            st.session_state["modo_conv"]        = "cadastro"
                            st.session_state["editando_conv"]     = None
                            st.session_state["expandir_form_conv"] = False
                            st.rerun()

                if enviar_conv:
                    if f_nome and f_dep and f_desc:
                        dados = {"nome": f_nome, "departamento": f_dep, "descricao": f_desc, "url": f_url, "status": f_status}
                        if modo_conv == "edicao" and editando_conv is not None:
                            dados_antes = str(linha.to_dict())
                            atualizar_registro("conversores", int(editando_conv), dados)
                            registrar_auditoria("EDIÇÃO", "conversores", f"Conversor editado: {f_nome}", dados_antes, str(dados))
                            st.success("Conversor atualizado com sucesso!")
                            st.session_state["modo_conv"]        = "cadastro"
                            st.session_state["editando_conv"]     = None
                            st.session_state["expandir_form_conv"] = False
                        else:
                            dados["data_cadastro"] = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
                            inserir_registro("conversores", dados)
                            registrar_auditoria("CADASTRO", "conversores", f"Novo conversor: {f_nome}", dados_depois=str(dados))
                            st.success("Conversor cadastrado com sucesso!")
                            st.session_state["expandir_form_conv"] = False
                        st.rerun()
                    else:
                        st.warning("Preencha nome, departamento e descrição.")

        st.write("---")

        # ---------- LISTA ----------
        st.markdown("#### 📋 Lista de Conversores")

        df_conv = carregar_tabela("conversores")

        if df_conv.empty:
            st.info("Nenhum conversor cadastrado ainda.")
        else:
            # Modo seleção múltipla
            modo_selecao_conv = st.checkbox("☑️ Selecionar múltiplos para exclusão em lote", key="modo_sel_conv")

            ids_selecionados_conv = []

            if modo_selecao_conv:
                col_marcar, _ = st.columns([2, 8])
                with col_marcar:
                    marcar_todos_conv = st.checkbox("✅ Marcar todos / Desmarcar todos", key="marcar_todos_conv")

            # Cabeçalho da lista
            if modo_selecao_conv:
                cab = st.columns([0.4, 3.2, 2, 1.5, 0.8, 0.8])
            else:
                cab = st.columns([3.6, 2, 1.5, 0.8, 0.8])

            headers = ["Nome / URL", "Departamento", "Status", "Editar", "Excluir"] if not modo_selecao_conv else ["", "Nome / URL", "Departamento", "Status", "Editar", "Excluir"]
            for h, c in zip(headers, cab):
                c.markdown(f"**{h}**")

            st.markdown("<hr style='margin:4px 0 10px 0'>", unsafe_allow_html=True)

            for _, row_c in df_conv.iterrows():
                id_c   = int(row_c["id"])
                nome_c = valor_texto(row_c["nome"])
                dep_c  = valor_texto(row_c["departamento"])
                stat_c = valor_texto(row_c["status"])
                url_c  = valor_texto(row_c.get("url", ""))

                if modo_selecao_conv:
                    col_chk, col_info, col_dep, col_stat, col_edit, col_del = st.columns([0.4, 3.2, 2, 1.5, 0.8, 0.8])
                    with col_chk:
                        marcado = st.checkbox("", key=f"chk_conv_{id_c}", value=marcar_todos_conv)
                        if marcado:
                            ids_selecionados_conv.append(id_c)
                else:
                    col_info, col_dep, col_stat, col_edit, col_del = st.columns([3.6, 2, 1.5, 0.8, 0.8])

                with col_info:
                    st.markdown(f"**{nome_c}**")
                    if url_c:
                        st.markdown(f"[🔗 Acessar]({url_c})")

                with col_dep:
                    st.write(dep_c)

                with col_stat:
                    st.markdown(status_html(stat_c), unsafe_allow_html=True)

                with col_edit:
                    if st.button("✏️", key=f"edit_conv_{id_c}", help="Editar"):
                        st.session_state["modo_conv"]         = "edicao"
                        st.session_state["editando_conv"]      = id_c
                        st.session_state["expandir_form_conv"] = True
                        st.rerun()

                with col_del:
                    if st.button("🗑️", key=f"del_conv_{id_c}", help="Excluir"):
                        st.session_state[f"popup_del_conv_{id_c}"] = True

                # Pop-up de confirmação de exclusão
                if st.session_state.get(f"popup_del_conv_{id_c}", False):
                    with st.container():
                        st.warning(f"⚠️ Tem certeza que deseja excluir **{nome_c}**? Esta ação pode ser desfeita logo após.")
                        col_sim, col_nao, _ = st.columns([1.2, 1.2, 6])
                        with col_sim:
                            if st.button("✅ Sim, excluir", key=f"sim_conv_{id_c}"):
                                adicionar_lixeira("conversores", row_c.to_dict())
                                excluir_registro("conversores", id_c)
                                registrar_auditoria("EXCLUSÃO", "conversores", f"Conversor excluído: {nome_c}", dados_antes=str(row_c.to_dict()))
                                st.session_state.pop(f"popup_del_conv_{id_c}", None)
                                st.rerun()
                        with col_nao:
                            if st.button("❌ Cancelar", key=f"nao_conv_{id_c}"):
                                st.session_state.pop(f"popup_del_conv_{id_c}", None)
                                st.rerun()

            # Exclusão em lote
            if modo_selecao_conv and ids_selecionados_conv:
                st.write("")
                st.error(f"⚠️ {len(ids_selecionados_conv)} conversor(es) selecionado(s) para exclusão em lote.")
                if st.button("🗑️ Excluir selecionados", key="excluir_lote_conv"):
                    st.session_state["popup_lote_conv"] = True

            if st.session_state.get("popup_lote_conv", False) and ids_selecionados_conv:
                nomes_lote = df_conv[df_conv["id"].isin(ids_selecionados_conv)]["nome"].tolist()
                st.warning(f"⚠️ Confirmar exclusão em lote de: **{', '.join(nomes_lote)}**?")
                col_sl, col_nl, _ = st.columns([1.2, 1.2, 6])
                with col_sl:
                    if st.button("✅ Confirmar exclusão", key="confirmar_lote_conv"):
                        for id_lote in ids_selecionados_conv:
                            row_lote = df_conv[df_conv["id"] == id_lote].iloc[0]
                            adicionar_lixeira("conversores", row_lote.to_dict())
                            excluir_registro("conversores", id_lote)
                        registrar_auditoria("EXCLUSÃO EM LOTE", "conversores", f"Excluídos: {', '.join(nomes_lote)}")
                        st.session_state.pop("popup_lote_conv", None)
                        st.success(f"{len(ids_selecionados_conv)} conversor(es) excluído(s)!")
                        st.rerun()
                with col_nl:
                    if st.button("❌ Cancelar", key="cancelar_lote_conv"):
                        st.session_state.pop("popup_lote_conv", None)
                        st.rerun()

    # =====================================================
    # ABA 2 — MODELOS BGR
    # =====================================================

    with aba2:
        st.subheader("📄 Gerenciar Modelos BGR")

        modo_bgr     = st.session_state.get("modo_bgr", "cadastro")
        editando_bgr = st.session_state.get("editando_bgr", None)

        label_expander_bgr = "✏️ Editando modelo BGR — clique para expandir/recolher" if modo_bgr == "edicao" else "➕ Cadastrar novo modelo BGR — clique para expandir/recolher"
        expanded_bgr       = st.session_state.get("expandir_form_bgr", False)

        with st.expander(label_expander_bgr, expanded=expanded_bgr):

            if modo_bgr == "edicao" and editando_bgr is not None:
                df_bgr_atual = carregar_tabela("modelos_bgr")
                linha_bgr    = df_bgr_atual[df_bgr_atual["id"] == editando_bgr]
                if linha_bgr.empty:
                    st.warning("Registro não encontrado.")
                    st.session_state["modo_bgr"]    = "cadastro"
                    st.session_state["editando_bgr"] = None
                    st.rerun()
                linha_bgr      = linha_bgr.iloc[0]
                nome_img_atual = valor_texto(linha_bgr.get("imagem", ""))
                if nome_img_atual:
                    img_url_atual = url_publica(BUCKET_IMAGENS, nome_img_atual)
                    if img_url_atual:
                        st.image(img_url_atual, caption="Imagem atual", width=160)
            else:
                linha_bgr      = None
                nome_img_atual = ""

            with st.form("form_bgr_principal"):
                col_b1, col_b2 = st.columns(2)
                with col_b1:
                    b_nome   = st.text_input("Nome do modelo BGR", value=valor_texto(linha_bgr["nome"]) if linha_bgr is not None else "")
                    b_dep    = st.selectbox("Departamento", DEPARTAMENTOS,
                        index=DEPARTAMENTOS.index(linha_bgr["departamento"]) if linha_bgr is not None and linha_bgr["departamento"] in DEPARTAMENTOS else 0)
                    b_status = st.selectbox("Status", STATUS_FERRAMENTAS,
                        index=STATUS_FERRAMENTAS.index(linha_bgr["status"]) if linha_bgr is not None and linha_bgr["status"] in STATUS_FERRAMENTAS else 0)
                with col_b2:
                    b_desc = st.text_area("Descrição", value=valor_texto(linha_bgr["descricao"]) if linha_bgr is not None else "", height=120)

                b_imagem  = st.file_uploader("Substituir imagem (opcional)" if modo_bgr == "edicao" else "Imagem de prévia *", type=["png", "jpg", "jpeg"])
                b_arquivo = st.file_uploader("Substituir arquivo .BGR (opcional)" if modo_bgr == "edicao" else "Arquivo .BGR", type=["bgr"])

                col_bbtn1, col_bbtn2 = st.columns([1, 3])
                with col_bbtn1:
                    enviar_bgr = st.form_submit_button("💾 Salvar" if modo_bgr == "edicao" else "➕ Cadastrar")
                with col_bbtn2:
                    if modo_bgr == "edicao":
                        cancelar_bgr = st.form_submit_button("✖ Cancelar edição")
                        if cancelar_bgr:
                            st.session_state["modo_bgr"]        = "cadastro"
                            st.session_state["editando_bgr"]     = None
                            st.session_state["expandir_form_bgr"] = False
                            st.rerun()

                if enviar_bgr:
                    if b_nome and b_dep:
                        if modo_bgr == "cadastro" and b_imagem is None:
                            st.warning("Selecione uma imagem de prévia para cadastrar.")
                        else:
                            timestamp      = datetime.now().strftime("%Y%m%d%H%M%S")
                            nome_img_final = nome_img_atual

                            if b_imagem is not None:
                                nome_img_final = f"{timestamp}_{nome_arquivo_seguro(b_imagem.name)}"
                                ext_i = b_imagem.name.split(".")[-1].lower()
                                ct_i  = "image/jpeg" if ext_i == "jpg" else f"image/{ext_i}"
                                upload_arquivo(BUCKET_IMAGENS, nome_img_final, b_imagem.getbuffer().tobytes(), ct_i)

                            nome_bgr_final = valor_texto(linha_bgr.get("arquivo_bgr", "")) if linha_bgr is not None else ""
                            if b_arquivo is not None:
                                nome_bgr_final = f"{timestamp}_{nome_arquivo_seguro(b_arquivo.name)}"
                                upload_arquivo(BUCKET_BGR, nome_bgr_final, b_arquivo.getbuffer().tobytes(), "application/octet-stream")

                            dados_bgr = {
                                "nome": b_nome, "departamento": b_dep, "descricao": b_desc,
                                "status": b_status, "imagem": nome_img_final, "arquivo_bgr": nome_bgr_final
                            }

                            if modo_bgr == "edicao" and editando_bgr is not None:
                                dados_antes_bgr = str(linha_bgr.to_dict())
                                atualizar_registro("modelos_bgr", int(editando_bgr), dados_bgr)
                                registrar_auditoria("EDIÇÃO", "modelos_bgr", f"Modelo BGR editado: {b_nome}", dados_antes_bgr, str(dados_bgr))
                                st.success("Modelo BGR atualizado com sucesso!")
                                st.session_state["modo_bgr"]        = "cadastro"
                                st.session_state["editando_bgr"]     = None
                                st.session_state["expandir_form_bgr"] = False
                            else:
                                dados_bgr["data_upload"] = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
                                inserir_registro("modelos_bgr", dados_bgr)
                                registrar_auditoria("UPLOAD", "modelos_bgr", f"Novo modelo BGR: {b_nome}", dados_depois=str(dados_bgr))
                                st.success("Modelo BGR cadastrado com sucesso!")
                                st.session_state["expandir_form_bgr"] = False
                            st.rerun()
                    else:
                        st.warning("Preencha nome e departamento.")

        st.write("---")

        # ---------- LISTA ----------
        st.markdown("#### 📋 Lista de Modelos BGR")

        df_bgr_lista = carregar_tabela("modelos_bgr")

        if df_bgr_lista.empty:
            st.info("Nenhum modelo BGR cadastrado ainda.")
        else:
            modo_selecao_bgr = st.checkbox("☑️ Selecionar múltiplos para exclusão em lote", key="modo_sel_bgr")

            ids_selecionados_bgr = []

            if modo_selecao_bgr:
                col_marcar_bgr, _ = st.columns([2, 8])
                with col_marcar_bgr:
                    marcar_todos_bgr = st.checkbox("✅ Marcar todos / Desmarcar todos", key="marcar_todos_bgr")

            for _, row_b in df_bgr_lista.iterrows():
                id_b   = int(row_b["id"])
                nome_b = valor_texto(row_b["nome"])
                dep_b  = valor_texto(row_b["departamento"])
                stat_b = valor_texto(row_b["status"])
                img_b  = valor_texto(row_b.get("imagem", ""))
                desc_b = valor_texto(row_b.get("descricao", ""))

                if modo_selecao_bgr:
                    col_chk_b, col_img_b, col_info_b, col_dep_b, col_stat_b, col_edit_b, col_del_b = st.columns([0.4, 0.9, 3, 1.8, 1.5, 0.7, 0.7])
                    with col_chk_b:
                        marcado_b = st.checkbox("", key=f"chk_bgr_{id_b}", value=marcar_todos_bgr)
                        if marcado_b:
                            ids_selecionados_bgr.append(id_b)
                else:
                    col_img_b, col_info_b, col_dep_b, col_stat_b, col_edit_b, col_del_b = st.columns([0.9, 3.4, 1.8, 1.5, 0.7, 0.7])

                with col_img_b:
                    if img_b:
                        img_url_b = url_publica(BUCKET_IMAGENS, img_b)
                        if img_url_b:
                            st.image(img_url_b, width=65)

                with col_info_b:
                    st.markdown(f"**{nome_b}**")
                    st.caption(desc_b[:80] + "..." if len(desc_b) > 80 else desc_b)

                with col_dep_b:
                    st.write(dep_b)

                with col_stat_b:
                    st.markdown(status_html(stat_b), unsafe_allow_html=True)

                with col_edit_b:
                    if st.button("✏️", key=f"edit_bgr_{id_b}", help="Editar"):
                        st.session_state["modo_bgr"]         = "edicao"
                        st.session_state["editando_bgr"]      = id_b
                        st.session_state["expandir_form_bgr"] = True
                        st.rerun()

                with col_del_b:
                    if st.button("🗑️", key=f"del_bgr_{id_b}", help="Excluir"):
                        st.session_state[f"popup_del_bgr_{id_b}"] = True

                # Pop-up de confirmação
                if st.session_state.get(f"popup_del_bgr_{id_b}", False):
                    with st.container():
                        st.warning(f"⚠️ Tem certeza que deseja excluir **{nome_b}**? Esta ação pode ser desfeita logo após.")
                        col_sim_b, col_nao_b, _ = st.columns([1.2, 1.2, 6])
                        with col_sim_b:
                            if st.button("✅ Sim, excluir", key=f"sim_bgr_{id_b}"):
                                adicionar_lixeira("modelos_bgr", row_b.to_dict())
                                excluir_registro("modelos_bgr", id_b)
                                registrar_auditoria("EXCLUSÃO", "modelos_bgr", f"Modelo BGR excluído: {nome_b}", dados_antes=str(row_b.to_dict()))
                                st.session_state.pop(f"popup_del_bgr_{id_b}", None)
                                st.rerun()
                        with col_nao_b:
                            if st.button("❌ Cancelar", key=f"nao_bgr_{id_b}"):
                                st.session_state.pop(f"popup_del_bgr_{id_b}", None)
                                st.rerun()

            # Exclusão em lote BGR
            if modo_selecao_bgr and ids_selecionados_bgr:
                st.write("")
                st.error(f"⚠️ {len(ids_selecionados_bgr)} modelo(s) selecionado(s) para exclusão em lote.")
                if st.button("🗑️ Excluir selecionados", key="excluir_lote_bgr"):
                    st.session_state["popup_lote_bgr"] = True

            if st.session_state.get("popup_lote_bgr", False) and ids_selecionados_bgr:
                nomes_lote_bgr = df_bgr_lista[df_bgr_lista["id"].isin(ids_selecionados_bgr)]["nome"].tolist()
                st.warning(f"⚠️ Confirmar exclusão em lote de: **{', '.join(nomes_lote_bgr)}**?")
                col_sl_b, col_nl_b, _ = st.columns([1.2, 1.2, 6])
                with col_sl_b:
                    if st.button("✅ Confirmar exclusão", key="confirmar_lote_bgr"):
                        for id_lote_b in ids_selecionados_bgr:
                            row_lote_b = df_bgr_lista[df_bgr_lista["id"] == id_lote_b].iloc[0]
                            adicionar_lixeira("modelos_bgr", row_lote_b.to_dict())
                            excluir_registro("modelos_bgr", id_lote_b)
                        registrar_auditoria("EXCLUSÃO EM LOTE", "modelos_bgr", f"Excluídos: {', '.join(nomes_lote_bgr)}")
                        st.session_state.pop("popup_lote_bgr", None)
                        st.success(f"{len(ids_selecionados_bgr)} modelo(s) excluído(s)!")
                        st.rerun()
                with col_nl_b:
                    if st.button("❌ Cancelar", key="cancelar_lote_bgr"):
                        st.session_state.pop("popup_lote_bgr", None)
                        st.rerun()

    # =====================================================
    # ABA 3 — SOLICITAÇÕES BGR
    # =====================================================

    with aba3:
        st.subheader("📥 Solicitações de acesso aos BGR")

        df_sol = carregar_tabela("solicitacoes_bgr")

        if df_sol.empty:
            st.info("Nenhuma solicitação registrada ainda.")
        else:
            col1, col2, col3 = st.columns(3)
            with col1:
                filtro_dep_sol = st.selectbox("Filtrar departamento:", ["Todos"] + DEPARTAMENTOS, key="sol_dep_admin")
            with col2:
                busca_cnpj = st.text_input("Buscar CNPJ:", key="sol_cnpj_admin")
            with col3:
                busca_email = st.text_input("Buscar e-mail:", key="sol_email_admin")

            df_sol_f = df_sol.copy()
            if filtro_dep_sol != "Todos":
                df_sol_f = df_sol_f[df_sol_f["departamento"] == filtro_dep_sol]
            if busca_cnpj:
                df_sol_f = df_sol_f[df_sol_f["cnpj"].astype(str).str.contains(busca_cnpj, case=False, na=False)]
            if busca_email:
                df_sol_f = df_sol_f[df_sol_f["email_usuario"].astype(str).str.contains(busca_email, case=False, na=False)]

            st.dataframe(df_sol_f, use_container_width=True)

            excel_sol = gerar_excel_download({"Solicitacoes_BGR": df_sol_f})
            st.download_button(
                label="📥 Exportar solicitações para Excel",
                data=excel_sol,
                file_name="solicitacoes_bgr.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

    # =====================================================
    # ABA 4 — EXPORTAÇÕES
    # =====================================================

    with aba4:
        st.subheader("📦 Exportar bases para Excel")

        df_exp_conv = carregar_tabela("conversores")
        df_exp_bgr  = carregar_tabela("modelos_bgr")
        df_exp_sol  = carregar_tabela("solicitacoes_bgr")
        df_exp_aud  = carregar_tabela("auditoria")

        excel_completo = gerar_excel_download({
            "Conversores":      df_exp_conv,
            "Modelos_BGR":      df_exp_bgr,
            "Solicitacoes_BGR": df_exp_sol,
            "Auditoria":        df_exp_aud
        })

        st.download_button(
            label="📥 Baixar todas as bases em Excel",
            data=excel_completo,
            file_name="bases_portal_ferramentas.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

        registrar_auditoria("EXPORTAÇÃO", "todas", "Exportação completa das bases para Excel")

    # =====================================================
    # ABA 5 — AUDITORIA
    # =====================================================

    with aba5:
        st.subheader("🔍 Auditoria de Movimentações")

        df_audit = carregar_tabela("auditoria")

        if df_audit.empty:
            st.info("Nenhuma movimentação registrada ainda.")
        else:
            col_a1, col_a2, col_a3 = st.columns(3)
            with col_a1:
                filtro_acao = st.selectbox(
                    "Filtrar por ação:",
                    ["Todas", "CADASTRO", "UPLOAD", "EDIÇÃO", "EXCLUSÃO", "EXCLUSÃO EM LOTE", "RESTAURAÇÃO", "EXPORTAÇÃO"],
                    key="audit_acao"
                )
            with col_a2:
                filtro_tab_aud = st.selectbox(
                    "Filtrar por tabela:",
                    ["Todas", "conversores", "modelos_bgr", "solicitacoes_bgr", "todas"],
                    key="audit_tabela"
                )
            with col_a3:
                busca_desc_aud = st.text_input("Buscar na descrição:", key="audit_desc")

            df_aud_f = df_audit.copy()
            if filtro_acao != "Todas":
                df_aud_f = df_aud_f[df_aud_f["acao"] == filtro_acao]
            if filtro_tab_aud != "Todas":
                df_aud_f = df_aud_f[df_aud_f["tabela"] == filtro_tab_aud]
            if busca_desc_aud:
                df_aud_f = df_aud_f[df_aud_f["descricao"].astype(str).str.contains(busca_desc_aud, case=False, na=False)]

            st.write(f"**{len(df_aud_f)} registro(s) encontrado(s)**")
            st.dataframe(df_aud_f, use_container_width=True)

            st.write("---")
            excel_aud = gerar_excel_download({"Auditoria": df_aud_f})
            st.download_button(
                label="📥 Exportar auditoria para Excel",
                data=excel_aud,
                file_name="auditoria_portal_ferramentas.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
