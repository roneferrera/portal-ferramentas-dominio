import streamlit as st
import pandas as pd
import unicodedata
import re
import json
import ast
from datetime import datetime
from io import BytesIO
from urllib.parse import quote, unquote
from supabase import create_client, Client

# =========================================================
# CONFIGURAÇÃO GERAL
# =========================================================

st.set_page_config(
    page_title="Central de Ferramentas e Relatórios",
    page_icon="🧩",
    layout="wide"
)

# =========================================================
# CONSTANTES
# =========================================================

DEPARTAMENTOS_PADRAO = [
    {"nome": "Fiscal", "icone": "📊", "ordem": 1},
    {"nome": "Folha de Pagamento", "icone": "👥", "ordem": 2},
    {"nome": "Contabilidade", "icone": "📚", "ordem": 3},
    {"nome": "Patrimônio", "icone": "🏢", "ordem": 4},
    {"nome": "Honorários", "icone": "💰", "ordem": 5},
]

STATUS_FERRAMENTAS = [
    "Ativo",
    "Em manutenção",
    "Em desenvolvimento"
]

BUCKET_IMAGENS = st.secrets["BUCKET_IMAGENS"]
BUCKET_BGR     = st.secrets["BUCKET_BGR"]

# TTL padrão do cache em segundos
CACHE_TTL = 60

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

.stApp {
    background-color: var(--tr-bg-main);
    color: var(--tr-text-main);
}

.block-container {
    padding-top: 1.5rem;
    padding-bottom: 3rem;
}

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

section[data-testid="stSidebar"] {
    background-color: var(--tr-bg-sidebar);
    border-right: 1px solid var(--tr-border);
}

.botao-link {
    display: inline-block;
    background-color: var(--tr-orange);
    color: #FFFFFF !important;
    padding: 7px 16px;
    border-radius: 8px;
    text-decoration: none;
    font-weight: 700;
    font-size: 13px;
    white-space: nowrap;
}

.botao-link:hover {
    background-color: var(--tr-orange-dark);
    color: #FFFFFF !important;
}

.stButton > button,
.stDownloadButton > button {
    background-color: var(--tr-orange);
    color: #FFFFFF;
    border: 1px solid var(--tr-orange);
    border-radius: 8px;
    font-weight: 700;
}

.stButton > button:hover,
.stDownloadButton > button:hover {
    background-color: var(--tr-orange-dark);
    color: #FFFFFF;
    border-color: var(--tr-orange-dark);
}

.stTextInput input,
.stTextArea textarea {
    background-color: var(--tr-bg-input);
    color: var(--tr-text-main);
    border: 1px solid var(--tr-border-light);
    border-radius: 8px;
}

.stSelectbox div[data-baseweb="select"] {
    background-color: var(--tr-bg-input);
    color: var(--tr-text-main);
    border-radius: 8px;
}

.status-ativo {
    display: inline-block;
    padding: 3px 10px;
    border-radius: 999px;
    background-color: var(--tr-success-bg);
    color: var(--tr-success-text);
    font-weight: 700;
    font-size: 12px;
}

.status-manutencao {
    display: inline-block;
    padding: 3px 10px;
    border-radius: 999px;
    background-color: var(--tr-warning-bg);
    color: var(--tr-warning-text);
    font-weight: 700;
    font-size: 12px;
}

.status-desenvolvimento {
    display: inline-block;
    padding: 3px 10px;
    border-radius: 999px;
    background-color: var(--tr-info-bg);
    color: var(--tr-info-text);
    font-weight: 700;
    font-size: 12px;
}

.card-link,
.card-link:visited,
.card-link:hover,
.card-link:active {
    display: block;
    text-decoration: none !important;
    color: inherit !important;
}

.setor-card {
    padding: 22px;
    border-radius: 14px;
    background-color: var(--tr-bg-card);
    border: 1px solid var(--tr-border);
    text-align: center;
    box-shadow: 0 4px 16px rgba(0,0,0,0.35);
    height: 245px;
    min-height: 245px;
    max-height: 245px;
    cursor: pointer;
    transition: all 0.2s ease-in-out;
    margin-bottom: 14px;
    box-sizing: border-box;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    overflow: hidden;
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
    margin: 0 0 16px 0;
    font-size: 38px;
    line-height: 1;
    height: 42px;
    display: flex;
    align-items: center;
    justify-content: center;
}

.setor-card h4 {
    color: var(--tr-text-main);
    margin: 0 0 14px 0;
    font-size: 21px;
    line-height: 1.25;
    min-height: 54px;
    max-height: 54px;
    display: flex;
    align-items: center;
    justify-content: center;
    text-align: center;
}

.setor-card p {
    margin: 3px 0;
    line-height: 1.25;
}

.setor-card .total-tools {
    font-size: 15px;
    font-weight: 800;
    color: #F5F5F5;
    margin-top: 4px;
    min-height: 22px;
}

.setor-card .sub-tools {
    font-size: 13px;
    color: #A8A8A8;
    min-height: 18px;
}

.tipo-badge {
    display: inline-block;
    padding: 3px 10px;
    border-radius: 999px;
    background: rgba(255, 128, 0, 0.16);
    border: 1px solid rgba(255, 128, 0, 0.45);
    color: #FFB366;
    font-size: 11px;
    font-weight: 800;
    margin-bottom: 4px;
}

.tipo-badge-bgr {
    display: inline-block;
    padding: 3px 10px;
    border-radius: 999px;
    background: rgba(66, 165, 245, 0.18);
    border: 1px solid rgba(66, 165, 245, 0.45);
    color: #90CAF9;
    font-size: 11px;
    font-weight: 800;
    margin-bottom: 4px;
}

.central-card {
    background-color: #1F1F1F;
    border: 1px solid #333333;
    border-radius: 12px;
    padding: 14px 16px;
    margin-bottom: 10px;
}

.central-card:hover {
    border-color: #FF8000;
    background-color: #252525;
}

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

[data-testid="stMetric"] {
    background-color: var(--tr-bg-card);
    border: 1px solid var(--tr-border);
    border-radius: 14px;
    padding: 18px;
}

[data-testid="stMetricValue"] {
    color: var(--tr-orange);
    font-weight: 700;
}

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

[data-testid="stDataFrame"] {
    border: 1px solid var(--tr-border);
    border-radius: 10px;
    background-color: var(--tr-bg-card);
}

div[data-testid="stExpander"] {
    background-color: var(--tr-bg-card);
    border: 1px solid var(--tr-border);
    border-radius: 10px;
}

[data-testid="stFileUploader"] {
    background-color: var(--tr-bg-card);
    border: 1px dashed var(--tr-border-light);
    border-radius: 12px;
    padding: 12px;
}

hr {
    border-color: var(--tr-border);
}

a {
    color: var(--tr-orange);
}

div[data-testid="stButton"] button {
    white-space: nowrap;
}
</style>
""", unsafe_allow_html=True)

# =========================================================
# SUPABASE
# =========================================================

@st.cache_resource
def get_supabase() -> Client:
    return create_client(
        "https://hylhbsrckmygluiykdur.supabase.co",
        st.secrets["SUPABASE_KEY"]
    )


# ---------------------------------------------------------
# CACHE DE LEITURA — compartilhado entre todos os usuários
# Após qualquer escrita, chamar invalidar_cache_tabela(tabela)
# ---------------------------------------------------------

@st.cache_data(ttl=CACHE_TTL, show_spinner=False)
def _carregar_tabela_cached(tabela: str) -> pd.DataFrame:
    try:
        resp = get_supabase().table(tabela).select("*").execute()
        return pd.DataFrame(resp.data) if resp.data else pd.DataFrame()
    except Exception as e:
        st.error(f"Erro ao carregar '{tabela}': {e}")
        return pd.DataFrame()


def carregar_tabela(tabela: str) -> pd.DataFrame:
    """Retorna DataFrame da tabela, usando cache compartilhado (TTL={CACHE_TTL}s)."""
    return _carregar_tabela_cached(tabela)


def invalidar_cache_tabela(tabela: str):
    """
    Limpa o cache da tabela após qualquer operação de escrita
    (insert, update, delete). Garante que o próximo acesso
    busque dados frescos do Supabase.
    """
    _carregar_tabela_cached.clear()


# ---------------------------------------------------------
# ESCRITA — sempre invalida o cache após operar
# ---------------------------------------------------------

def inserir_registro(tabela: str, dados: dict):
    try:
        get_supabase().table(tabela).insert(dados).execute()
        invalidar_cache_tabela(tabela)
        return True
    except Exception as e:
        st.error(f"Erro ao inserir em '{tabela}': {e}")
        return False


def atualizar_registro(tabela: str, id_registro: int, dados: dict):
    try:
        get_supabase().table(tabela).update(dados).eq("id", id_registro).execute()
        invalidar_cache_tabela(tabela)
        return True
    except Exception as e:
        st.error(f"Erro ao atualizar em '{tabela}': {e}")
        return False


def excluir_registro(tabela: str, id_registro: int):
    try:
        get_supabase().table(tabela).delete().eq("id", id_registro).execute()
        invalidar_cache_tabela(tabela)
        return True
    except Exception as e:
        st.error(f"Erro ao excluir em '{tabela}': {e}")
        return False

# =========================================================
# STORAGE
# =========================================================

def upload_arquivo(bucket, nome, dados_bytes, content_type):
    try:
        sb = get_supabase()

        try:
            sb.storage.from_(bucket).remove([nome])
        except Exception:
            pass

        sb.storage.from_(bucket).upload(
            path=nome,
            file=dados_bytes,
            file_options={"content-type": content_type, "upsert": "true"}
        )

        return sb.storage.from_(bucket).get_public_url(nome)

    except Exception as e:
        st.error(f"Erro no upload: {e}")
        return None


def baixar_arquivo(bucket, nome):
    try:
        return get_supabase().storage.from_(bucket).download(nome)
    except Exception:
        return None


def url_publica(bucket, nome):
    try:
        return get_supabase().storage.from_(bucket).get_public_url(nome)
    except Exception:
        return ""

# =========================================================
# AUXILIARES
# =========================================================

def valor_texto(v):
    if v is None:
        return ""

    try:
        if pd.isna(v):
            return ""
    except Exception:
        pass

    return str(v).strip()


def email_valido(email):
    email = valor_texto(email)
    return "@" in email and "." in email


def nome_arquivo_seguro(nome):
    nome = unicodedata.normalize("NFKD", nome)
    nome = "".join(c for c in nome if not unicodedata.combining(c))
    nome = re.sub(r"[^\w\.\-]", "_", nome)

    p = nome.rsplit(".", 1)

    return p[0].replace(".", "_") + "." + p[1] if len(p) == 2 else nome


def mostrar_logo():
    st.sidebar.markdown("### 🧩 Central de Ferramentas e Relatórios")


def status_html(status):
    if status == "Ativo":
        return '<span class="status-ativo">● Ativo</span>'

    if status == "Em manutenção":
        return '<span class="status-manutencao">⚙ Em manutenção</span>'

    return '<span class="status-desenvolvimento">🔧 Em desenvolvimento</span>'


def gerar_excel_download(dfs: dict):
    out = BytesIO()

    with pd.ExcelWriter(out, engine="openpyxl") as w:
        for nome, df in dfs.items():
            if df is None:
                df = pd.DataFrame()

            df_temp = df.copy()

            for col in df_temp.columns:
                df_temp[col] = df_temp[col].apply(
                    lambda x: json.dumps(x, ensure_ascii=False, default=str)
                    if isinstance(x, (dict, list, tuple, set))
                    else x
                )

            df_temp.to_excel(w, index=False, sheet_name=nome[:31])

    return out.getvalue()


def _limpar_objeto_para_json(obj):
    if obj is None:
        return None

    if isinstance(obj, pd.Series):
        return _limpar_objeto_para_json(obj.to_dict())

    if isinstance(obj, dict):
        return {str(k): _limpar_objeto_para_json(v) for k, v in obj.items()}

    if isinstance(obj, (list, tuple, set)):
        return [_limpar_objeto_para_json(v) for v in obj]

    if isinstance(obj, (datetime, pd.Timestamp)):
        return obj.strftime("%d/%m/%Y %H:%M:%S")

    try:
        if pd.isna(obj):
            return None
    except Exception:
        pass

    if hasattr(obj, "item"):
        try:
            return obj.item()
        except Exception:
            pass

    return obj


def _parse_dict(valor):
    if valor is None:
        return {}

    if isinstance(valor, pd.Series):
        valor = valor.to_dict()

    if isinstance(valor, dict):
        return _limpar_objeto_para_json(valor)

    try:
        if pd.isna(valor):
            return {}
    except Exception:
        pass

    texto = str(valor).strip()

    if not texto or texto.lower() in ["none", "null", "nan", "nat"]:
        return {}

    try:
        obj = json.loads(texto)

        if isinstance(obj, dict):
            return _limpar_objeto_para_json(obj)
    except Exception:
        pass

    try:
        texto_sanitizado = re.sub(r"\bnan\b", "None", texto, flags=re.IGNORECASE)
        texto_sanitizado = re.sub(r"\bNaT\b", "None", texto_sanitizado)

        obj = ast.literal_eval(texto_sanitizado)

        if isinstance(obj, dict):
            return _limpar_objeto_para_json(obj)
    except Exception:
        pass

    return {}


def _bool_supabase(v):
    if isinstance(v, bool):
        return v

    return str(v).strip().lower() in ["true", "1", "sim", "yes", "y"]


def rerun():
    st.rerun()

# =========================================================
# DEPARTAMENTOS
# =========================================================

def carregar_departamentos(apenas_ativos=True) -> pd.DataFrame:
    df = carregar_tabela("departamentos")

    if df.empty:
        return df

    if apenas_ativos and "ativo" in df.columns:
        df = df[df["ativo"].apply(_bool_supabase)]

    if "ordem" in df.columns:
        df["ordem_num"] = pd.to_numeric(df["ordem"], errors="coerce").fillna(999)
        df = df.sort_values(["ordem_num", "nome"]).drop(columns=["ordem_num"])
    elif "nome" in df.columns:
        df = df.sort_values("nome")

    return df.reset_index(drop=True)


def listar_departamentos(apenas_ativos=True):
    df = carregar_departamentos(apenas_ativos=apenas_ativos)

    if df.empty or "nome" not in df.columns:
        return [d["nome"] for d in DEPARTAMENTOS_PADRAO]

    return df["nome"].dropna().astype(str).tolist()


def mapa_icones_departamentos(apenas_ativos=True):
    df = carregar_departamentos(apenas_ativos=apenas_ativos)
    mapa = {d["nome"]: d["icone"] for d in DEPARTAMENTOS_PADRAO}

    if df.empty:
        return mapa

    for _, row in df.iterrows():
        nome = valor_texto(row.get("nome", ""))
        icone = valor_texto(row.get("icone", "")) or "📁"

        if nome:
            mapa[nome] = icone

    return mapa


def inicializar_departamentos_padrao():
    df = carregar_tabela("departamentos")

    if not df.empty:
        return

    for dep in DEPARTAMENTOS_PADRAO:
        inserir_registro("departamentos", {
            "nome": dep["nome"],
            "icone": dep["icone"],
            "ativo": True,
            "ordem": dep["ordem"],
            "data_cadastro": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
            "data_alteracao": ""
        })


def nome_departamento_valido(nome):
    return bool(valor_texto(nome))

# =========================================================
# AUDITORIA
# =========================================================

def serializar_dados_auditoria(dados):
    if dados is None:
        return ""

    if isinstance(dados, str):
        return dados

    try:
        return json.dumps(
            _limpar_objeto_para_json(dados),
            ensure_ascii=False,
            default=str
        )
    except Exception:
        return str(dados)


def _parse_dados_auditoria(valor):
    return _parse_dict(valor)


def _formatar_valor_auditoria(valor):
    if valor is None:
        return ""

    try:
        if pd.isna(valor):
            return ""
    except Exception:
        pass

    valor = _limpar_objeto_para_json(valor)

    if valor is None:
        return ""

    if isinstance(valor, (dict, list, tuple, set)):
        try:
            return json.dumps(valor, ensure_ascii=False, default=str)
        except Exception:
            return str(valor)

    return str(valor)


def expandir_colunas_auditoria(df_auditoria: pd.DataFrame) -> pd.DataFrame:
    if df_auditoria is None or df_auditoria.empty:
        return pd.DataFrame()

    df = df_auditoria.copy()

    lista_antes = []
    lista_depois = []
    campos = set()

    for _, row in df.iterrows():
        antes = _parse_dados_auditoria(row.get("dados_antes", ""))
        depois = _parse_dados_auditoria(row.get("dados_depois", ""))

        lista_antes.append(antes)
        lista_depois.append(depois)

        campos.update(str(k) for k in antes.keys())
        campos.update(str(k) for k in depois.keys())

    campos_preferidos = [
        "id",
        "nome",
        "icone",
        "ativo",
        "ordem",
        "departamento",
        "descricao",
        "url",
        "status",
        "imagem",
        "arquivo_bgr",
        "data_cadastro",
        "data_alteracao",
        "data_upload"
    ]

    campos_ordenados = [c for c in campos_preferidos if c in campos]
    campos_ordenados.extend(
        sorted([c for c in campos if c not in campos_ordenados], key=lambda x: x.lower())
    )

    colunas_base = [
        c for c in df.columns
        if c not in ["dados_antes", "dados_depois"]
    ]

    df_saida = df[colunas_base].copy()

    for campo in campos_ordenados:
        df_saida[f"{campo}_antes"] = [
            _formatar_valor_auditoria(antes.get(campo, ""))
            for antes in lista_antes
        ]

        df_saida[f"{campo}_depois"] = [
            _formatar_valor_auditoria(depois.get(campo, ""))
            for depois in lista_depois
        ]

    return df_saida


def registrar_auditoria(acao, tabela, descricao, dados_antes="", dados_depois=""):
    payload = {
        "data_hora": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
        "acao": acao,
        "tabela": tabela,
        "descricao": descricao,
        "dados_antes": serializar_dados_auditoria(dados_antes),
        "dados_depois": serializar_dados_auditoria(dados_depois)
    }

    try:
        get_supabase().table("auditoria").insert(payload).execute()
        # Invalida cache da auditoria para exibir o novo registro imediatamente
        invalidar_cache_tabela("auditoria")
        st.session_state.pop("_erro_auditoria", None)
        return True
    except Exception as e:
        st.session_state["_erro_auditoria"] = str(e)
        return False

# =========================================================
# LIXEIRA
# =========================================================

def adicionar_lixeira(tabela, registro):
    try:
        registro_limpo = _limpar_objeto_para_json(registro)

        if not isinstance(registro_limpo, dict):
            registro_limpo = {}

        nome = valor_texto(registro_limpo.get("nome", ""))

        payload = {
            "data_hora": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
            "tabela": tabela,
            "nome": nome,
            "registro": registro_limpo,
            "restaurado": False,
            "restaurado_em": ""
        }

        get_supabase().table("lixeira").insert(payload).execute()
        invalidar_cache_tabela("lixeira")
        return True

    except Exception as e:
        st.error(f"Erro ao enviar item para a lixeira: {e}")
        return False


def carregar_lixeira(apenas_nao_restaurados=True):
    try:
        df = carregar_tabela("lixeira")

        if df.empty:
            return df

        if apenas_nao_restaurados and "restaurado" in df.columns:
            df = df[~df["restaurado"].apply(_bool_supabase)]

        if "id" in df.columns:
            df = df.sort_values("id", ascending=False)

        return df

    except Exception as e:
        st.error(f"Erro ao carregar lixeira: {e}")
        return pd.DataFrame()


def restaurar_item_lixeira(item, acao_auditoria="RESTAURAÇÃO"):
    try:
        if isinstance(item, pd.Series):
            item = item.to_dict()

        id_lixeira = int(item.get("id"))
        tabela = valor_texto(item.get("tabela", ""))
        registro = _parse_dict(item.get("registro", {}))

        if tabela not in ["conversores", "modelos_bgr"]:
            st.error("A tabela de origem da lixeira não é válida para restauração.")
            return False

        if not registro:
            st.error("Registro da lixeira vazio ou inválido.")
            return False

        dados_restaurar = {
            k: v for k, v in registro.items()
            if k != "id"
        }

        nome = valor_texto(registro.get("nome", item.get("nome", "registro")))

        if not inserir_registro(tabela, dados_restaurar):
            return False

        get_supabase().table("lixeira").update({
            "restaurado": True,
            "restaurado_em": datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        }).eq("id", id_lixeira).execute()

        invalidar_cache_tabela("lixeira")

        registrar_auditoria(
            acao_auditoria,
            tabela,
            f"Restaurado da lixeira: {nome}",
            dados_depois=dados_restaurar
        )

        return True

    except Exception as e:
        st.error(f"Erro ao restaurar item da lixeira: {e}")
        return False


def excluir_lixeira_definitivo(item, acao_auditoria="EXCLUSÃO DEFINITIVA"):
    try:
        if isinstance(item, pd.Series):
            item = item.to_dict()

        id_lixeira = int(item.get("id"))
        tabela = valor_texto(item.get("tabela", ""))
        nome = valor_texto(item.get("nome", "registro"))
        registro = _parse_dict(item.get("registro", {}))

        get_supabase().table("lixeira").delete().eq("id", id_lixeira).execute()
        invalidar_cache_tabela("lixeira")

        registrar_auditoria(
            acao_auditoria,
            "lixeira",
            f"Item removido definitivamente da lixeira: {nome}",
            dados_antes={
                "id_lixeira": id_lixeira,
                "tabela_origem": tabela,
                "registro": registro
            }
        )

        return True

    except Exception as e:
        st.error(f"Erro ao excluir definitivamente da lixeira: {e}")
        return False

# =========================================================
# SELEÇÃO MÚLTIPLA
# =========================================================

def inicializar_selecao(key):
    if key not in st.session_state or not isinstance(st.session_state[key], set):
        try:
            st.session_state[key] = set(st.session_state.get(key, []))
        except Exception:
            st.session_state[key] = set()


def _atualizar_checkboxes_por_prefixo(prefixo_chk, valor=False):
    if not prefixo_chk:
        return

    for k in list(st.session_state.keys()):
        if str(k).startswith(prefixo_chk):
            st.session_state[k] = bool(valor)


def limpar_selecao(key, prefixo_chk=None):
    inicializar_selecao(key)
    st.session_state[key] = set()
    _atualizar_checkboxes_por_prefixo(prefixo_chk, False)


def selecionar_todos_filtrados(key, df_filtrado, prefixo_chk=None):
    inicializar_selecao(key)

    ids = set()

    if df_filtrado is not None and not df_filtrado.empty and "id" in df_filtrado.columns:
        ids = set(df_filtrado["id"].dropna().astype(int).tolist())

    st.session_state[key] = ids

    _atualizar_checkboxes_por_prefixo(prefixo_chk, False)

    if prefixo_chk:
        for id_item in ids:
            st.session_state[f"{prefixo_chk}{int(id_item)}"] = True


def sincronizar_checkbox_selecao(key_ids, key_checkbox, id_item):
    inicializar_selecao(key_ids)

    id_item = int(id_item)

    if st.session_state.get(key_checkbox, False):
        st.session_state[key_ids].add(id_item)
    else:
        st.session_state[key_ids].discard(id_item)


def checkbox_linha_selecao(key_ids, prefixo_chk, id_item):
    inicializar_selecao(key_ids)

    id_item = int(id_item)
    key_checkbox = f"{prefixo_chk}{id_item}"

    st.session_state[key_checkbox] = id_item in st.session_state[key_ids]

    st.checkbox(
        "Selecionar",
        key=key_checkbox,
        label_visibility="collapsed",
        on_change=sincronizar_checkbox_selecao,
        args=(key_ids, key_checkbox, id_item),
        help="Selecionar para ação em lote"
    )

    return st.session_state.get(key_checkbox, False)


def controle_modo_selecao(label, key, help_text):
    if hasattr(st, "toggle"):
        return st.toggle(label, key=key, help=help_text)

    return st.checkbox(label, key=key, help=help_text)


def container_com_borda():
    try:
        return st.container(border=True)
    except TypeError:
        return st.container()


def barra_selecao_lote(key_ids, df_filtrado, prefixo_chk, sufixo_key, nome_plural):
    inicializar_selecao(key_ids)

    qtd = len(st.session_state[key_ids])
    total = 0 if df_filtrado is None else len(df_filtrado)

    with container_com_borda():
        st.markdown(f"**☑️ Seleção em lote:** {qtd} de {total} {nome_plural} selecionado(s)")

        b1, b2, b3, _ = st.columns([1.5, 1.1, 1.2, 4])

        with b1:
            if st.button("✅ Marcar filtrados", key=f"sel_todos_{sufixo_key}", use_container_width=True):
                selecionar_todos_filtrados(key_ids, df_filtrado, prefixo_chk)
                rerun()

        with b2:
            if st.button("🧹 Limpar", key=f"limpar_sel_{sufixo_key}", use_container_width=True):
                limpar_selecao(key_ids, prefixo_chk)
                st.session_state.pop(f"popup_lote_{sufixo_key}", None)
                rerun()

        with b3:
            if st.button(
                "🗑️ Excluir",
                key=f"btn_lote_{sufixo_key}",
                disabled=qtd == 0,
                use_container_width=True
            ):
                st.session_state[f"popup_lote_{sufixo_key}"] = True
                rerun()

    return qtd

# =========================================================
# CENTRAL
# =========================================================

def montar_df_central_ferramentas(df_conversores, df_modelos):
    lista = []

    if df_conversores is not None and not df_conversores.empty:
        for _, row in df_conversores.iterrows():
            lista.append({
                "tipo": "Conversor",
                "id_origem": row.get("id", ""),
                "nome": valor_texto(row.get("nome", "")),
                "departamento": valor_texto(row.get("departamento", "")),
                "descricao": valor_texto(row.get("descricao", "")),
                "status": valor_texto(row.get("status", "")),
                "url": valor_texto(row.get("url", "")),
                "imagem": "",
                "arquivo_bgr": "",
                "data": valor_texto(row.get("data_cadastro", "")),
                "origem": "conversores"
            })

    if df_modelos is not None and not df_modelos.empty:
        for _, row in df_modelos.iterrows():
            lista.append({
                "tipo": "Relatório BGR",
                "id_origem": row.get("id", ""),
                "nome": valor_texto(row.get("nome", "")),
                "departamento": valor_texto(row.get("departamento", "")),
                "descricao": valor_texto(row.get("descricao", "")),
                "status": valor_texto(row.get("status", "")),
                "url": "",
                "imagem": valor_texto(row.get("imagem", "")),
                "arquivo_bgr": valor_texto(row.get("arquivo_bgr", "")),
                "data": valor_texto(row.get("data_upload", "")),
                "origem": "modelos_bgr"
            })

    df = pd.DataFrame(lista)

    if df.empty:
        return df

    df["nome_ordem"] = df["nome"].astype(str).str.lower()
    df = df.sort_values(["departamento", "tipo", "nome_ordem"]).drop(columns=["nome_ordem"])

    return df


def render_central_ferramentas():
    st.title("🧩 Central de Ferramentas e Relatórios")
    st.write("Consulte conversores e relatórios BGR em uma única tela, organizados por departamento.")

    departamentos = listar_departamentos(apenas_ativos=True)

    df_conversores = carregar_tabela("conversores")
    df_modelos = carregar_tabela("modelos_bgr")

    df_central = montar_df_central_ferramentas(df_conversores, df_modelos)

    if df_central.empty:
        st.info("Nenhuma ferramenta ou relatório cadastrado.")
        return

    opcoes_dep = ["Todos"] + departamentos

    departamento_pre = st.session_state.get("departamento_central", "Todos")

    if departamento_pre not in opcoes_dep:
        departamento_pre = "Todos"

    idx_dep = opcoes_dep.index(departamento_pre)

    f1, f2, f3, f4 = st.columns([2.4, 1.8, 1.8, 3])

    with f1:
        filtro_departamento = st.selectbox(
            "Departamento:",
            opcoes_dep,
            index=idx_dep,
            key="filtro_dep_central"
        )

    with f2:
        filtro_tipo = st.selectbox(
            "Tipo:",
            ["Todos", "Conversor", "Relatório BGR"],
            key="filtro_tipo_central"
        )

    with f3:
        filtro_status = st.selectbox(
            "Status:",
            ["Todos"] + STATUS_FERRAMENTAS,
            key="filtro_status_central"
        )

    with f4:
        busca = st.text_input(
            "Buscar:",
            placeholder="Nome ou descrição...",
            key="busca_central"
        )

    df_f = df_central.copy()

    if filtro_departamento != "Todos":
        df_f = df_f[df_f["departamento"] == filtro_departamento]

    if filtro_tipo != "Todos":
        df_f = df_f[df_f["tipo"] == filtro_tipo]

    if filtro_status != "Todos":
        df_f = df_f[df_f["status"] == filtro_status]

    if busca:
        df_f = df_f[
            df_f["nome"].astype(str).str.contains(busca, case=False, na=False) |
            df_f["descricao"].astype(str).str.contains(busca, case=False, na=False)
        ]

    st.write("---")

    c1, c2, c3 = st.columns(3)

    with c1:
        st.metric("Total encontrado", len(df_f))

    with c2:
        st.metric("Conversores", len(df_f[df_f["tipo"] == "Conversor"]) if not df_f.empty else 0)

    with c3:
        st.metric("Relatórios BGR", len(df_f[df_f["tipo"] == "Relatório BGR"]) if not df_f.empty else 0)

    st.write("---")

    if df_f.empty:
        st.info("Nenhum item encontrado com os filtros selecionados.")
        return

    for _, row in df_f.iterrows():
        tipo = valor_texto(row.get("tipo", ""))
        id_origem = valor_texto(row.get("id_origem", ""))
        nome = valor_texto(row.get("nome", ""))
        departamento = valor_texto(row.get("departamento", ""))
        descricao = valor_texto(row.get("descricao", ""))
        status = valor_texto(row.get("status", ""))
        url = valor_texto(row.get("url", ""))
        imagem = valor_texto(row.get("imagem", ""))
        arquivo_bgr = valor_texto(row.get("arquivo_bgr", ""))
        data = valor_texto(row.get("data", ""))
        origem = valor_texto(row.get("origem", ""))

        chave = f"{origem}_{id_origem}"

        badge = "tipo-badge" if tipo == "Conversor" else "tipo-badge-bgr"
        label_tipo = "🛠️ Conversor" if tipo == "Conversor" else "📄 Relatório BGR"

        st.markdown("<div class='central-card'>", unsafe_allow_html=True)

        l1, l2, l3, l4, l5 = st.columns([3.0, 1.5, 1.35, 1.2, 1.2])

        with l1:
            st.markdown(
                f"<span class='{badge}'>{label_tipo}</span>",
                unsafe_allow_html=True
            )
            st.markdown(f"### {nome}")
            st.caption(descricao[:120] + "…" if len(descricao) > 120 else descricao)

        with l2:
            st.markdown("**Departamento**")
            st.write(departamento)

        with l3:
            st.markdown("**Status**")
            st.markdown(status_html(status), unsafe_allow_html=True)

        with l4:
            st.markdown("**Ação**")

            if tipo == "Conversor":
                if status == "Ativo" and url:
                    st.markdown(
                        f'<a class="botao-link" href="{url}" target="_blank">🔗 Acessar</a>',
                        unsafe_allow_html=True
                    )
                elif status == "Em manutenção":
                    st.markdown('<span class="status-manutencao">⚙ Manutenção</span>', unsafe_allow_html=True)
                else:
                    st.markdown('<span class="status-desenvolvimento">🔧 Em dev.</span>', unsafe_allow_html=True)

            else:
                if status == "Ativo" and arquivo_bgr:
                    st.markdown('<span class="status-ativo">📄 Disponível</span>', unsafe_allow_html=True)
                elif status == "Em manutenção":
                    st.markdown('<span class="status-manutencao">⚙ Manutenção</span>', unsafe_allow_html=True)
                else:
                    st.markdown('<span class="status-desenvolvimento">🔧 Em dev.</span>', unsafe_allow_html=True)

        with l5:
            st.markdown("**Detalhes**")

            if st.button("🔎 Ver", key=f"btn_ver_detalhes_{chave}", use_container_width=True):
                st.session_state[f"detalhes_aberto_{chave}"] = not st.session_state.get(
                    f"detalhes_aberto_{chave}",
                    False
                )
                rerun()

        if st.session_state.get(f"detalhes_aberto_{chave}", False):
            st.write("---")

            d1, d2 = st.columns([3, 1])

            with d1:
                st.markdown(f"**Tipo:** {label_tipo}")
                st.markdown(f"**Nome:** {nome}")
                st.markdown(f"**Departamento:** {departamento}")
                st.markdown(f"**Status:** {status_html(status)}", unsafe_allow_html=True)
                st.markdown(f"**Descrição:** {descricao}")

                if data:
                    st.markdown(f"**Data:** {data}")

                if tipo == "Conversor":
                    if status == "Ativo" and url:
                        st.markdown(
                            f'<a class="botao-link" href="{url}" target="_blank">🔗 Acessar conversor</a>',
                            unsafe_allow_html=True
                        )
                    elif status == "Em manutenção":
                        st.warning("Este conversor está temporariamente em manutenção.")
                    else:
                        st.info("Este conversor está em desenvolvimento.")

            with d2:
                if tipo == "Relatório BGR" and imagem:
                    img_url = url_publica(BUCKET_IMAGENS, imagem)

                    if img_url:
                        st.image(img_url, caption="Prévia", use_container_width=True)

            if tipo == "Relatório BGR":
                if status != "Ativo":
                    st.info("Este relatório BGR ainda não está disponível para download.")
                elif not arquivo_bgr:
                    st.warning("Este relatório BGR não possui arquivo vinculado.")
                else:
                    st.write("---")
                    st.markdown("**Preencha os dados para liberar o download:**")

                    if f"nonce_central_bgr_{chave}" not in st.session_state:
                        st.session_state[f"nonce_central_bgr_{chave}"] = 0

                    nonce_central = st.session_state[f"nonce_central_bgr_{chave}"]

                    with st.form(f"form_bgr_central_{chave}_{nonce_central}"):
                        fc1, fc2 = st.columns(2)

                        with fc1:
                            nome_u = st.text_input("Nome", key=f"central_nome_{chave}_{nonce_central}")
                            email_u = st.text_input("E-mail", key=f"central_email_{chave}_{nonce_central}")
                            cnpj_u = st.text_input("CNPJ", key=f"central_cnpj_{chave}_{nonce_central}")

                        with fc2:
                            cod_u = st.text_input(
                                "Código cliente Domínio",
                                key=f"central_cod_{chave}_{nonce_central}"
                            )
                            obs_u = st.text_area(
                                "Observações",
                                key=f"central_obs_{chave}_{nonce_central}",
                                height=90
                            )

                        sub = st.form_submit_button("📥 Registrar e liberar download")

                        if sub:
                            if not nome_u:
                                st.warning("Informe o nome.")
                            elif not email_valido(email_u):
                                st.warning("Informe um e-mail válido.")
                            elif not cnpj_u:
                                st.warning("Informe o CNPJ.")
                            elif not cod_u:
                                st.warning("Informe o código cliente Domínio.")
                            else:
                                ok = inserir_registro("solicitacoes_bgr", {
                                    "data_hora": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
                                    "nome_usuario": nome_u,
                                    "email_usuario": email_u,
                                    "cnpj": cnpj_u,
                                    "codigo_cliente_dominio": cod_u,
                                    "departamento": departamento,
                                    "modelo": nome,
                                    "arquivo_bgr": arquivo_bgr,
                                    "observacao": obs_u,
                                    "status": "Liberado"
                                })

                                if ok:
                                    st.session_state[f"central_bgr_liberado_{chave}"] = True
                                    st.session_state[f"nonce_central_bgr_{chave}"] += 1
                                    st.success("Solicitação registrada! Download liberado.")

                    if st.session_state.get(f"central_bgr_liberado_{chave}", False):
                        bgr_bytes = baixar_arquivo(BUCKET_BGR, arquivo_bgr)

                        if bgr_bytes:
                            st.download_button(
                                "⬇️ Baixar .BGR",
                                data=bgr_bytes,
                                file_name=arquivo_bgr,
                                mime="application/octet-stream",
                                key=f"central_dl_bgr_{chave}"
                            )

        st.markdown("</div>", unsafe_allow_html=True)

# =========================================================
# LIXEIRA — ABA
# =========================================================

def _tipo_lixeira(tabela):
    if tabela == "conversores":
        return "Conversor"

    if tabela == "modelos_bgr":
        return "Relatório BGR"

    return tabela


def render_card_lixeira(item):
    if isinstance(item, pd.Series):
        item = item.to_dict()

    id_lixeira = int(item.get("id"))
    tabela = valor_texto(item.get("tabela", ""))
    nome = valor_texto(item.get("nome", "")) or "Sem nome"
    data_hora = valor_texto(item.get("data_hora", ""))
    registro = _parse_dict(item.get("registro", {}))
    tipo_item = _tipo_lixeira(tabela)

    with st.expander(
        f"🗑️ {tipo_item}: {nome} — excluído em {data_hora}",
        expanded=False
    ):
        c1, c2, c3 = st.columns(3)

        with c1:
            st.markdown(f"**Tipo:** {tipo_item}")

        with c2:
            st.markdown(f"**Tabela:** `{tabela}`")

        with c3:
            st.markdown(f"**ID na lixeira:** `{id_lixeira}`")

        st.write("**Dados armazenados:**")
        st.json(registro)

        b1, b2, _ = st.columns([1.4, 1.8, 5])

        with b1:
            if st.button(
                "↩️ Restaurar",
                key=f"restaurar_lixeira_{id_lixeira}",
                use_container_width=True
            ):
                if restaurar_item_lixeira(item):
                    st.success(f'"{nome}" restaurado com sucesso!')
                    rerun()

        with b2:
            if st.button(
                "🧨 Excluir definitivo",
                key=f"pedir_deldef_lixeira_{id_lixeira}",
                use_container_width=True
            ):
                st.session_state[f"confirmar_deldef_lixeira_{id_lixeira}"] = True

        if st.session_state.get(f"confirmar_deldef_lixeira_{id_lixeira}", False):
            st.warning(
                f"Tem certeza que deseja excluir definitivamente **{nome}** da lixeira? "
                "Essa ação não poderá ser desfeita."
            )

            cdel1, cdel2, _ = st.columns([1, 1, 5])

            with cdel1:
                if st.button(
                    "✅ Sim",
                    key=f"sim_deldef_lixeira_{id_lixeira}",
                    use_container_width=True
                ):
                    if excluir_lixeira_definitivo(item):
                        st.session_state.pop(f"confirmar_deldef_lixeira_{id_lixeira}", None)
                        st.success("Item removido definitivamente.")
                        rerun()

            with cdel2:
                if st.button(
                    "❌ Não",
                    key=f"nao_deldef_lixeira_{id_lixeira}",
                    use_container_width=True
                ):
                    st.session_state.pop(f"confirmar_deldef_lixeira_{id_lixeira}", None)
                    rerun()


def render_aba_lixeira():
    st.subheader("🗑️ Lixeira")

    df_lix = carregar_lixeira(apenas_nao_restaurados=True)

    if df_lix.empty:
        st.info("Nenhum item na lixeira.")
        return

    f1, f2, f3 = st.columns([2, 3, 2])

    with f1:
        filtro_tipo_lix = st.selectbox(
            "Tipo:",
            ["Todos", "conversores", "modelos_bgr"],
            key="filtro_tipo_lixeira"
        )

    with f2:
        busca_lix = st.text_input(
            "Buscar:",
            placeholder="Nome, tabela ou conteúdo...",
            key="busca_lixeira"
        )

    with f3:
        mostrar_restaurados = st.checkbox(
            "Mostrar já restaurados",
            value=False,
            key="mostrar_restaurados_lixeira"
        )

    df_lix = carregar_lixeira(apenas_nao_restaurados=not mostrar_restaurados)

    df_lix_f = df_lix.copy()

    if filtro_tipo_lix != "Todos" and "tabela" in df_lix_f.columns:
        df_lix_f = df_lix_f[df_lix_f["tabela"] == filtro_tipo_lix]

    if busca_lix:
        busca = busca_lix.strip()
        cond = pd.Series(False, index=df_lix_f.index)

        if "nome" in df_lix_f.columns:
            cond = cond | df_lix_f["nome"].astype(str).str.contains(busca, case=False, na=False)

        if "tabela" in df_lix_f.columns:
            cond = cond | df_lix_f["tabela"].astype(str).str.contains(busca, case=False, na=False)

        if "registro" in df_lix_f.columns:
            cond = cond | df_lix_f["registro"].astype(str).str.contains(busca, case=False, na=False)

        df_lix_f = df_lix_f[cond]

    st.caption(f"{len(df_lix_f)} item(ns) encontrado(s).")

    if df_lix_f.empty:
        st.info("Nenhum item encontrado com os filtros selecionados.")
        return

    for _, item in df_lix_f.iterrows():
        render_card_lixeira(item)

    st.write("---")

    df_export_lix = df_lix_f.copy()

    if "registro" in df_export_lix.columns:
        df_export_lix["registro"] = df_export_lix["registro"].apply(
            lambda x: json.dumps(_parse_dict(x), ensure_ascii=False, default=str)
        )

    excel_lixeira = gerar_excel_download({"Lixeira": df_export_lix})

    st.download_button(
        "📥 Exportar lixeira",
        data=excel_lixeira,
        file_name="lixeira.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        key="dl_lixeira"
    )

# =========================================================
# DADOS INICIAIS
# =========================================================

def inicializar_conversores_padrao():
    df = carregar_tabela("conversores")

    if not df.empty:
        return

    departamentos_ativos = listar_departamentos(apenas_ativos=True)

    conversores_padrao = [
        {
            "nome": "Gerador RPA TXT",
            "departamento": "Folha de Pagamento",
            "descricao": "Gera arquivos TXT para processamento por RPA.",
            "url": "https://gerador-rpa-txt.streamlit.app/",
            "status": "Ativo"
        },
        {
            "nome": "Converte Bens Domínio",
            "departamento": "Patrimônio",
            "descricao": "Conversor de bens patrimoniais para leiaute Domínio.",
            "url": "https://convertebensdominio.streamlit.app/",
            "status": "Ativo"
        },
        {
            "nome": "Eventos Com Plano / Sem Plano",
            "departamento": "Fiscal",
            "descricao": "Ferramenta para tratar eventos com plano e sem plano.",
            "url": "https://eventos-complano-semplano.streamlit.app/",
            "status": "Ativo"
        },
        {
            "nome": "Clientes e Fornecedores - Conta Patrimonial",
            "departamento": "Contabilidade",
            "descricao": "Tratamento de clientes, fornecedores e contas patrimoniais.",
            "url": "https://clientes-fornecedores-conta-patrimonial.streamlit.app/",
            "status": "Ativo"
        },
        {
            "nome": "Conversor Leiaute com Separador Domínio",
            "departamento": "Fiscal",
            "descricao": "Conversor de leiaute com separador para o sistema Domínio.",
            "url": "https://conversorleiautecomseparadordominio.streamlit.app/",
            "status": "Ativo"
        }
    ]

    for c in conversores_padrao:
        if c["departamento"] not in departamentos_ativos:
            continue

        c["data_cadastro"] = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        inserir_registro("conversores", c)

# =========================================================
# INICIALIZAÇÃO
# =========================================================

inicializar_departamentos_padrao()
inicializar_conversores_padrao()
mostrar_logo()

# =========================================================
# TRATAMENTO DO CLIQUE NOS CARDS VIA URL
# =========================================================

opcoes_publicas = [
    "Início",
    "Central de Ferramentas e Relatórios"
]

query_params = st.query_params

if query_params.get("pagina") == "central":
    dep_url = query_params.get("departamento", "Todos")

    if isinstance(dep_url, list):
        dep_url = dep_url[0]

    dep_url = unquote(str(dep_url))

    departamentos_ativos_qp = listar_departamentos(apenas_ativos=True)

    if dep_url not in ["Todos"] + departamentos_ativos_qp:
        dep_url = "Todos"

    st.session_state["departamento_central"] = dep_url
    st.session_state["filtro_dep_central"] = dep_url
    st.session_state["menu_publico"] = "Central de Ferramentas e Relatórios"

    try:
        st.query_params.clear()
    except Exception:
        pass

if st.session_state.get("menu_publico") not in opcoes_publicas:
    st.session_state["menu_publico"] = "Início"

# =========================================================
# MENU
# =========================================================

st.sidebar.write("---")
st.sidebar.subheader("Menu público")

pagina_publica = st.sidebar.radio(
    "Selecione uma opção:",
    opcoes_publicas,
    key="menu_publico"
)

st.sidebar.write("---")
st.sidebar.subheader("Área administrativa")

abrir_admin = st.sidebar.checkbox("Abrir Painel Administrativo")

pagina = "Painel Administrativo" if abrir_admin else pagina_publica

# =========================================================
# INÍCIO
# =========================================================

if pagina == "Início":
    st.title("🧩 Central de Ferramentas e Relatórios")
    st.write("Central de conversores, relatórios BGR e ferramentas internas por departamento.")

    df_conversores = carregar_tabela("conversores")
    df_modelos = carregar_tabela("modelos_bgr")
    df_solicitacoes = carregar_tabela("solicitacoes_bgr")

    total_conversores = len(df_conversores)
    total_bgr = len(df_modelos)

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Conversores cadastrados", total_conversores)

    with col2:
        st.metric("Relatórios BGR cadastrados", total_bgr)

    with col3:
        st.metric("Solicitações BGR", len(df_solicitacoes))

    st.write("---")
    st.subheader("Departamentos")

    st.caption(
        "Clique em um departamento para abrir a Central de Ferramentas e Relatórios "
        "com conversores e BGRs juntos."
    )

    departamentos = listar_departamentos(apenas_ativos=True)
    icones = mapa_icones_departamentos(apenas_ativos=True)

    if not departamentos:
        st.info("Nenhum departamento ativo cadastrado.")
    else:
        qtd_colunas = min(len(departamentos), 5)
        cols = st.columns(qtd_colunas)

        for i, dep in enumerate(departamentos):
            with cols[i % qtd_colunas]:
                qtd_conv = 0
                qtd_bgr = 0

                if not df_conversores.empty and "departamento" in df_conversores.columns:
                    qtd_conv = len(df_conversores[df_conversores["departamento"] == dep])

                if not df_modelos.empty and "departamento" in df_modelos.columns:
                    qtd_bgr = len(df_modelos[df_modelos["departamento"] == dep])

                qtd_total = qtd_conv + qtd_bgr
                dep_url = quote(dep, safe="")

                st.markdown(f"""
                <a class="card-link" href="?pagina=central&departamento={dep_url}" target="_self">
                    <div class="setor-card">
                        <h1>{icones.get(dep, "📁")}</h1>
                        <h4>{dep}</h4>
                        <p class="total-tools">{qtd_total} ferramenta(s)</p>
                        <p class="sub-tools">{qtd_conv} conversor(es)</p>
                        <p class="sub-tools">{qtd_bgr} BGR</p>
                    </div>
                </a>
                """, unsafe_allow_html=True)

    st.write("---")

    st.markdown(
        """
        <a class="botao-link" href="?pagina=central&departamento=Todos" target="_self">
            🔎 Ver todas as ferramentas e relatórios
        </a>
        """,
        unsafe_allow_html=True
    )

# =========================================================
# CENTRAL
# =========================================================

elif pagina == "Central de Ferramentas e Relatórios":
    render_central_ferramentas()

# =========================================================
# PAINEL ADMINISTRATIVO
# =========================================================

elif pagina == "Painel Administrativo":
    st.title("⚙️ Painel Administrativo")

    st.markdown("""
    <div class="aviso-admin">
        <strong>Atenção:</strong> esta versão está sem login. O painel ainda não possui senha.
    </div>
    """, unsafe_allow_html=True)

    st.write("")

    aba1, aba2, aba3, aba4, aba5, aba6, aba7 = st.tabs([
        "🛠️ Conversores",
        "📄 Modelos BGR",
        "🏷️ Departamentos",
        "📥 Solicitações",
        "📦 Exportações",
        "🔍 Auditoria",
        "🗑️ Lixeira"
    ])

    # =====================================================
    # ABA 1 — CONVERSORES
    # =====================================================

    with aba1:
        st.subheader("🛠️ Gerenciar Conversores")

        departamentos = listar_departamentos(apenas_ativos=True)
        df_conv = carregar_tabela("conversores")

        if "modo_conv" not in st.session_state:
            st.session_state["modo_conv"] = "cadastro"

        if "editando_conv" not in st.session_state:
            st.session_state["editando_conv"] = None

        if "expandir_form_conv" not in st.session_state:
            st.session_state["expandir_form_conv"] = False

        if "nonce_conv" not in st.session_state:
            st.session_state["nonce_conv"] = 0

        modo_conv = st.session_state.get("modo_conv", "cadastro")
        id_edit_conv = st.session_state.get("editando_conv")
        dados_conv_edicao = {}

        if modo_conv == "edicao" and id_edit_conv is not None:
            if not df_conv.empty and "id" in df_conv.columns:
                registro_conv = df_conv[df_conv["id"] == int(id_edit_conv)]

                if not registro_conv.empty:
                    dados_conv_edicao = registro_conv.iloc[0].to_dict()
                else:
                    st.warning("Conversor não encontrado para edição.")
                    st.session_state["modo_conv"] = "cadastro"
                    st.session_state["editando_conv"] = None
                    modo_conv = "cadastro"
                    id_edit_conv = None

        titulo_form_conv = "➕ Cadastrar novo conversor"

        if modo_conv == "edicao":
            titulo_form_conv = f"✏️ Editar conversor: {valor_texto(dados_conv_edicao.get('nome', ''))}"

        with st.expander(
            titulo_form_conv,
            expanded=st.session_state.get("expandir_form_conv", False)
        ):
            sufixo_conv = f"{modo_conv}_{id_edit_conv if id_edit_conv is not None else 'novo'}_{st.session_state['nonce_conv']}"

            nome_atual_conv = valor_texto(dados_conv_edicao.get("nome", ""))
            dep_atual_conv = valor_texto(dados_conv_edicao.get("departamento", departamentos[0] if departamentos else ""))
            desc_atual_conv = valor_texto(dados_conv_edicao.get("descricao", ""))
            url_atual_conv = valor_texto(dados_conv_edicao.get("url", ""))
            status_atual_conv = valor_texto(dados_conv_edicao.get("status", STATUS_FERRAMENTAS[0]))

            idx_dep_conv = departamentos.index(dep_atual_conv) if dep_atual_conv in departamentos else 0
            idx_status_conv = STATUS_FERRAMENTAS.index(status_atual_conv) if status_atual_conv in STATUS_FERRAMENTAS else 0

            if not departamentos:
                st.warning("Cadastre pelo menos um departamento ativo antes de cadastrar conversores.")
            else:
                with st.form(f"form_conv_{sufixo_conv}"):
                    cform1, cform2 = st.columns(2)

                    with cform1:
                        nome_conv_form = st.text_input(
                            "Nome do conversor",
                            value=nome_atual_conv,
                            key=f"nome_conv_form_{sufixo_conv}"
                        )

                        departamento_conv_form = st.selectbox(
                            "Departamento",
                            departamentos,
                            index=idx_dep_conv,
                            key=f"dep_conv_form_{sufixo_conv}"
                        )

                        status_conv_form = st.selectbox(
                            "Status",
                            STATUS_FERRAMENTAS,
                            index=idx_status_conv,
                            key=f"status_conv_form_{sufixo_conv}"
                        )

                    with cform2:
                        url_conv_form = st.text_input(
                            "URL de acesso",
                            value=url_atual_conv,
                            key=f"url_conv_form_{sufixo_conv}"
                        )

                        descricao_conv_form = st.text_area(
                            "Descrição",
                            value=desc_atual_conv,
                            height=120,
                            key=f"desc_conv_form_{sufixo_conv}"
                        )

                    bsalvar_conv, bcancelar_conv = st.columns([1, 1])

                    with bsalvar_conv:
                        salvar_conv = st.form_submit_button(
                            "💾 Salvar conversor",
                            use_container_width=True
                        )

                    with bcancelar_conv:
                        cancelar_conv = st.form_submit_button(
                            "❌ Cancelar",
                            use_container_width=True
                        )

                if cancelar_conv:
                    st.session_state["modo_conv"] = "cadastro"
                    st.session_state["editando_conv"] = None
                    st.session_state["expandir_form_conv"] = False
                    st.session_state["nonce_conv"] += 1
                    rerun()

                if salvar_conv:
                    if not valor_texto(nome_conv_form):
                        st.warning("Informe o nome do conversor.")
                    elif not valor_texto(descricao_conv_form):
                        st.warning("Informe a descrição do conversor.")
                    elif status_conv_form == "Ativo" and not valor_texto(url_conv_form):
                        st.warning("Informe a URL do conversor ativo.")
                    else:
                        dados_salvar_conv = {
                            "nome": valor_texto(nome_conv_form),
                            "departamento": departamento_conv_form,
                            "descricao": valor_texto(descricao_conv_form),
                            "url": valor_texto(url_conv_form),
                            "status": status_conv_form
                        }

                        if modo_conv == "cadastro":
                            dados_salvar_conv["data_cadastro"] = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

                            if inserir_registro("conversores", dados_salvar_conv):
                                registrar_auditoria(
                                    "CADASTRO",
                                    "conversores",
                                    f"Conversor cadastrado: {dados_salvar_conv['nome']}",
                                    dados_depois=dados_salvar_conv
                                )

                                st.success("Conversor cadastrado com sucesso!")

                        else:
                            dados_antes_conv = dados_conv_edicao.copy()

                            dados_depois_conv = dados_antes_conv.copy()
                            dados_depois_conv.update(dados_salvar_conv)

                            if atualizar_registro(
                                "conversores",
                                int(id_edit_conv),
                                dados_salvar_conv
                            ):
                                registrar_auditoria(
                                    "ALTERAÇÃO",
                                    "conversores",
                                    f"Conversor alterado: {dados_depois_conv['nome']}",
                                    dados_antes=dados_antes_conv,
                                    dados_depois=dados_depois_conv
                                )

                                st.success("Conversor alterado com sucesso!")

                        st.session_state["modo_conv"] = "cadastro"
                        st.session_state["editando_conv"] = None
                        st.session_state["expandir_form_conv"] = False
                        st.session_state["nonce_conv"] += 1
                        rerun()

        if df_conv.empty:
            st.info("Nenhum conversor cadastrado.")
        else:
            fc1, fc2, fc3 = st.columns([3, 2, 2])

            with fc1:
                busca_admin_conv = st.text_input(
                    "🔍 Buscar conversor:",
                    key="busca_admin_conv"
                )

            with fc2:
                filtro_dep_admin_conv = st.selectbox(
                    "Departamento:",
                    ["Todos"] + departamentos,
                    key="fdep_admin_conv"
                )

            with fc3:
                filtro_status_admin_conv = st.selectbox(
                    "Status:",
                    ["Todos"] + STATUS_FERRAMENTAS,
                    key="fstatus_admin_conv"
                )

            df_conv_f = df_conv.copy()

            if busca_admin_conv:
                df_conv_f = df_conv_f[
                    df_conv_f["nome"].astype(str).str.contains(busca_admin_conv, case=False, na=False) |
                    df_conv_f["descricao"].astype(str).str.contains(busca_admin_conv, case=False, na=False)
                ]

            if filtro_dep_admin_conv != "Todos":
                df_conv_f = df_conv_f[df_conv_f["departamento"] == filtro_dep_admin_conv]

            if filtro_status_admin_conv != "Todos":
                df_conv_f = df_conv_f[df_conv_f["status"] == filtro_status_admin_conv]

            st.write("---")

            inicializar_selecao("ids_sel_conv")

            if st.session_state.pop("reset_chk_conv", False):
                limpar_selecao("ids_sel_conv", "chk_conv_")

            modo_sel_conv = controle_modo_selecao(
                "Modo seleção em lote",
                key="modo_sel_conv",
                help_text="Ative para selecionar vários conversores e excluir em lote."
            )

            if not modo_sel_conv:
                limpar_selecao("ids_sel_conv", "chk_conv_")
                st.session_state.pop("popup_lote_conv", None)

            if modo_sel_conv:
                barra_selecao_lote(
                    key_ids="ids_sel_conv",
                    df_filtrado=df_conv_f,
                    prefixo_chk="chk_conv_",
                    sufixo_key="conv",
                    nome_plural="conversor(es)"
                )

                st.markdown("<hr style='margin:14px 0 8px 0;border-color:#333'>", unsafe_allow_html=True)

                hc = st.columns([0.45, 3.5, 1.8, 1.4, 0.8, 0.55, 0.55])

                for h, col in zip(["Sel.", "Nome", "Departamento", "Status", "Acesso", "", ""], hc):
                    col.markdown(f"**{h}**")

            else:
                hc = st.columns([3.5, 1.8, 1.4, 0.8, 0.55, 0.55])

                for h, col in zip(["Nome", "Departamento", "Status", "Acesso", "", ""], hc):
                    col.markdown(f"**{h}**")

            st.markdown("<hr style='margin:4px 0 8px 0;border-color:#333'>", unsafe_allow_html=True)

            if df_conv_f.empty:
                st.info("Nenhum conversor encontrado com os filtros selecionados.")

            for _, row_c in df_conv_f.iterrows():
                id_c = int(row_c["id"])
                nome_c = valor_texto(row_c.get("nome", ""))
                dep_c = valor_texto(row_c.get("departamento", ""))
                stat_c = valor_texto(row_c.get("status", ""))
                desc_c = valor_texto(row_c.get("descricao", ""))
                url_c = valor_texto(row_c.get("url", ""))

                if modo_sel_conv:
                    cc = st.columns([0.45, 3.5, 1.8, 1.4, 0.8, 0.55, 0.55])

                    with cc[0]:
                        checkbox_linha_selecao("ids_sel_conv", "chk_conv_", id_c)
                else:
                    cc = st.columns([3.5, 1.8, 1.4, 0.8, 0.55, 0.55])

                offset = 1 if modo_sel_conv else 0

                with cc[0 + offset]:
                    st.markdown(f"**{nome_c}**")
                    st.caption(desc_c[:55] + "…" if len(desc_c) > 55 else desc_c)

                with cc[1 + offset]:
                    st.write(dep_c)

                with cc[2 + offset]:
                    st.markdown(status_html(stat_c), unsafe_allow_html=True)

                with cc[3 + offset]:
                    if stat_c == "Ativo" and url_c:
                        st.markdown(
                            f'<a class="botao-link" href="{url_c}" target="_blank">Abrir</a>',
                            unsafe_allow_html=True
                        )
                    else:
                        st.caption("-")

                with cc[4 + offset]:
                    if st.button("✏️", key=f"edit_conv_{id_c}"):
                        st.session_state.update({
                            "modo_conv": "edicao",
                            "editando_conv": id_c,
                            "expandir_form_conv": True
                        })
                        rerun()

                with cc[5 + offset]:
                    if st.button("🗑️", key=f"del_conv_{id_c}"):
                        st.session_state[f"popup_conv_{id_c}"] = True

                if st.session_state.get(f"popup_conv_{id_c}", False):
                    st.warning(f"⚠️ Excluir **{nome_c}**?")

                    csc, cnc, _ = st.columns([1, 1, 7])

                    with csc:
                        if st.button("✅ Sim", key=f"sim_conv_{id_c}"):
                            dados_antes = row_c.to_dict()

                            if adicionar_lixeira("conversores", dados_antes):
                                if excluir_registro("conversores", id_c):
                                    registrar_auditoria(
                                        "EXCLUSÃO",
                                        "conversores",
                                        f"Conversor excluído: {nome_c}",
                                        dados_antes=dados_antes
                                    )

                            st.session_state.pop(f"popup_conv_{id_c}", None)
                            st.session_state["ids_sel_conv"].discard(id_c)
                            rerun()

                    with cnc:
                        if st.button("❌ Não", key=f"nao_conv_{id_c}"):
                            st.session_state.pop(f"popup_conv_{id_c}", None)
                            rerun()

            ids_sel_conv = list(st.session_state.get("ids_sel_conv", set()))

            if st.session_state.get("popup_lote_conv") and ids_sel_conv:
                nomes_l = df_conv[df_conv["id"].isin(ids_sel_conv)]["nome"].astype(str).tolist()

                st.warning(
                    f"⚠️ Confirmar exclusão de **{len(ids_sel_conv)} conversor(es)**: "
                    f"**{', '.join(nomes_l)}**?"
                )

                cslc, cnlc, _ = st.columns([1, 1, 7])

                with cslc:
                    if st.button("✅ Confirmar", key="conf_lote_conv"):
                        for id_l in ids_sel_conv:
                            registro_lote = df_conv[df_conv["id"] == int(id_l)]

                            if registro_lote.empty:
                                continue

                            r = registro_lote.iloc[0]
                            nome_item = valor_texto(r.get("nome", ""))
                            dados_antes = r.to_dict()

                            if adicionar_lixeira("conversores", dados_antes):
                                if excluir_registro("conversores", int(id_l)):
                                    registrar_auditoria(
                                        "EXCLUSÃO EM LOTE",
                                        "conversores",
                                        f"Conversor excluído em lote: {nome_item}",
                                        dados_antes=dados_antes
                                    )

                        st.session_state["ids_sel_conv"] = set()
                        st.session_state["reset_chk_conv"] = True
                        st.session_state.pop("popup_lote_conv", None)

                        st.success("Conversores excluídos!")
                        rerun()

                with cnlc:
                    if st.button("❌ Cancelar", key="canc_lote_conv"):
                        st.session_state.pop("popup_lote_conv", None)
                        rerun()

    # =====================================================
    # ABA 2 — MODELOS BGR
    # =====================================================

    with aba2:
        st.subheader("📄 Gerenciar Modelos BGR")

        departamentos = listar_departamentos(apenas_ativos=True)
        df_bgr = carregar_tabela("modelos_bgr")

        if "modo_bgr" not in st.session_state:
            st.session_state["modo_bgr"] = "cadastro"

        if "editando_bgr" not in st.session_state:
            st.session_state["editando_bgr"] = None

        if "expandir_form_bgr" not in st.session_state:
            st.session_state["expandir_form_bgr"] = False

        if "nonce_bgr" not in st.session_state:
            st.session_state["nonce_bgr"] = 0

        modo_bgr = st.session_state.get("modo_bgr", "cadastro")
        id_edit_bgr = st.session_state.get("editando_bgr")
        dados_bgr_edicao = {}

        if modo_bgr == "edicao" and id_edit_bgr is not None:
            if not df_bgr.empty and "id" in df_bgr.columns:
                registro_bgr = df_bgr[df_bgr["id"] == int(id_edit_bgr)]

                if not registro_bgr.empty:
                    dados_bgr_edicao = registro_bgr.iloc[0].to_dict()
                else:
                    st.warning("Modelo BGR não encontrado para edição.")
                    st.session_state["modo_bgr"] = "cadastro"
                    st.session_state["editando_bgr"] = None
                    modo_bgr = "cadastro"
                    id_edit_bgr = None

        titulo_form_bgr = "➕ Cadastrar novo modelo BGR"

        if modo_bgr == "edicao":
            titulo_form_bgr = f"✏️ Editar modelo BGR: {valor_texto(dados_bgr_edicao.get('nome', ''))}"

        with st.expander(
            titulo_form_bgr,
            expanded=st.session_state.get("expandir_form_bgr", False)
        ):
            sufixo_bgr = f"{modo_bgr}_{id_edit_bgr if id_edit_bgr is not None else 'novo'}_{st.session_state['nonce_bgr']}"

            nome_atual_bgr = valor_texto(dados_bgr_edicao.get("nome", ""))
            dep_atual_bgr = valor_texto(dados_bgr_edicao.get("departamento", departamentos[0] if departamentos else ""))
            desc_atual_bgr = valor_texto(dados_bgr_edicao.get("descricao", ""))
            status_atual_bgr = valor_texto(dados_bgr_edicao.get("status", STATUS_FERRAMENTAS[0]))
            imagem_atual_bgr = valor_texto(dados_bgr_edicao.get("imagem", ""))
            arquivo_atual_bgr = valor_texto(dados_bgr_edicao.get("arquivo_bgr", ""))

            idx_dep_bgr = departamentos.index(dep_atual_bgr) if dep_atual_bgr in departamentos else 0
            idx_status_bgr = STATUS_FERRAMENTAS.index(status_atual_bgr) if status_atual_bgr in STATUS_FERRAMENTAS else 0

            if not departamentos:
                st.warning("Cadastre pelo menos um departamento ativo antes de cadastrar modelos BGR.")
            else:
                with st.form(f"form_bgr_{sufixo_bgr}"):
                    bform1, bform2 = st.columns(2)

                    with bform1:
                        nome_bgr_form = st.text_input(
                            "Nome do relatório BGR",
                            value=nome_atual_bgr,
                            key=f"nome_bgr_form_{sufixo_bgr}"
                        )

                        departamento_bgr_form = st.selectbox(
                            "Departamento",
                            departamentos,
                            index=idx_dep_bgr,
                            key=f"dep_bgr_form_{sufixo_bgr}"
                        )

                        status_bgr_form = st.selectbox(
                            "Status",
                            STATUS_FERRAMENTAS,
                            index=idx_status_bgr,
                            key=f"status_bgr_form_{sufixo_bgr}"
                        )

                        descricao_bgr_form = st.text_area(
                            "Descrição",
                            value=desc_atual_bgr,
                            height=120,
                            key=f"desc_bgr_form_{sufixo_bgr}"
                        )

                    with bform2:
                        if imagem_atual_bgr:
                            st.caption(f"Imagem atual: {imagem_atual_bgr}")

                        imagem_upload_bgr = st.file_uploader(
                            "Imagem de prévia",
                            type=["png", "jpg", "jpeg", "webp"],
                            key=f"imagem_bgr_form_{sufixo_bgr}"
                        )

                        if arquivo_atual_bgr:
                            st.caption(f"Arquivo BGR atual: {arquivo_atual_bgr}")

                        arquivo_upload_bgr = st.file_uploader(
                            "Arquivo .BGR",
                            type=["bgr"],
                            key=f"arquivo_bgr_form_{sufixo_bgr}"
                        )

                    bsalvar_bgr, bcancelar_bgr = st.columns([1, 1])

                    with bsalvar_bgr:
                        salvar_bgr = st.form_submit_button(
                            "💾 Salvar modelo BGR",
                            use_container_width=True
                        )

                    with bcancelar_bgr:
                        cancelar_bgr = st.form_submit_button(
                            "❌ Cancelar",
                            use_container_width=True
                        )

                if cancelar_bgr:
                    st.session_state["modo_bgr"] = "cadastro"
                    st.session_state["editando_bgr"] = None
                    st.session_state["expandir_form_bgr"] = False
                    st.session_state["nonce_bgr"] += 1
                    rerun()

                if salvar_bgr:
                    if not valor_texto(nome_bgr_form):
                        st.warning("Informe o nome do relatório BGR.")
                    elif not valor_texto(descricao_bgr_form):
                        st.warning("Informe a descrição do relatório BGR.")
                    elif modo_bgr == "cadastro" and arquivo_upload_bgr is None:
                        st.warning("Envie o arquivo .BGR.")
                    else:
                        imagem_nome_final = imagem_atual_bgr
                        arquivo_bgr_nome_final = arquivo_atual_bgr

                        agora_nome = datetime.now().strftime("%Y%m%d%H%M%S")

                        if imagem_upload_bgr is not None:
                            imagem_nome_final = nome_arquivo_seguro(
                                f"{agora_nome}_{imagem_upload_bgr.name}"
                            )

                            upload_img_ok = upload_arquivo(
                                BUCKET_IMAGENS,
                                imagem_nome_final,
                                imagem_upload_bgr.getvalue(),
                                imagem_upload_bgr.type or "application/octet-stream"
                            )

                            if not upload_img_ok:
                                st.stop()

                        if arquivo_upload_bgr is not None:
                            arquivo_bgr_nome_final = nome_arquivo_seguro(
                                f"{agora_nome}_{arquivo_upload_bgr.name}"
                            )

                            upload_bgr_ok = upload_arquivo(
                                BUCKET_BGR,
                                arquivo_bgr_nome_final,
                                arquivo_upload_bgr.getvalue(),
                                arquivo_upload_bgr.type or "application/octet-stream"
                            )

                            if not upload_bgr_ok:
                                st.stop()

                        dados_salvar_bgr = {
                            "nome": valor_texto(nome_bgr_form),
                            "departamento": departamento_bgr_form,
                            "descricao": valor_texto(descricao_bgr_form),
                            "status": status_bgr_form,
                            "imagem": imagem_nome_final,
                            "arquivo_bgr": arquivo_bgr_nome_final
                        }

                        if modo_bgr == "cadastro":
                            dados_salvar_bgr["data_upload"] = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

                            if inserir_registro("modelos_bgr", dados_salvar_bgr):
                                registrar_auditoria(
                                    "CADASTRO",
                                    "modelos_bgr",
                                    f"Relatório BGR cadastrado: {dados_salvar_bgr['nome']}",
                                    dados_depois=dados_salvar_bgr
                                )

                                st.success("Modelo BGR cadastrado com sucesso!")

                        else:
                            dados_antes_bgr = dados_bgr_edicao.copy()

                            if arquivo_upload_bgr is not None:
                                dados_salvar_bgr["data_upload"] = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

                            dados_depois_bgr = dados_antes_bgr.copy()
                            dados_depois_bgr.update(dados_salvar_bgr)

                            if atualizar_registro(
                                "modelos_bgr",
                                int(id_edit_bgr),
                                dados_salvar_bgr
                            ):
                                registrar_auditoria(
                                    "ALTERAÇÃO",
                                    "modelos_bgr",
                                    f"Relatório BGR alterado: {dados_depois_bgr['nome']}",
                                    dados_antes=dados_antes_bgr,
                                    dados_depois=dados_depois_bgr
                                )

                                st.success("Modelo BGR alterado com sucesso!")

                        st.session_state["modo_bgr"] = "cadastro"
                        st.session_state["editando_bgr"] = None
                        st.session_state["expandir_form_bgr"] = False
                        st.session_state["nonce_bgr"] += 1
                        rerun()

        if df_bgr.empty:
            st.info("Nenhum modelo BGR cadastrado.")
        else:
            fb1, fb2, fb3 = st.columns([3, 2, 2])

            with fb1:
                busca_admin_bgr = st.text_input(
                    "🔍 Buscar modelo BGR:",
                    key="busca_admin_bgr"
                )

            with fb2:
                filtro_dep_admin_bgr = st.selectbox(
                    "Departamento:",
                    ["Todos"] + departamentos,
                    key="fdep_admin_bgr"
                )

            with fb3:
                filtro_status_admin_bgr = st.selectbox(
                    "Status:",
                    ["Todos"] + STATUS_FERRAMENTAS,
                    key="fstatus_admin_bgr"
                )

            df_bgr_f = df_bgr.copy()

            if busca_admin_bgr:
                df_bgr_f = df_bgr_f[
                    df_bgr_f["nome"].astype(str).str.contains(busca_admin_bgr, case=False, na=False) |
                    df_bgr_f["descricao"].astype(str).str.contains(busca_admin_bgr, case=False, na=False)
                ]

            if filtro_dep_admin_bgr != "Todos":
                df_bgr_f = df_bgr_f[df_bgr_f["departamento"] == filtro_dep_admin_bgr]

            if filtro_status_admin_bgr != "Todos":
                df_bgr_f = df_bgr_f[df_bgr_f["status"] == filtro_status_admin_bgr]

            st.write("---")

            inicializar_selecao("ids_sel_bgr")

            if st.session_state.pop("reset_chk_bgr", False):
                limpar_selecao("ids_sel_bgr", "chk_bgr_")

            modo_sel_bgr = controle_modo_selecao(
                "Modo seleção em lote",
                key="modo_sel_bgr",
                help_text="Ative para selecionar vários modelos BGR e excluir em lote."
            )

            if not modo_sel_bgr:
                limpar_selecao("ids_sel_bgr", "chk_bgr_")
                st.session_state.pop("popup_lote_bgr", None)

            if modo_sel_bgr:
                barra_selecao_lote(
                    key_ids="ids_sel_bgr",
                    df_filtrado=df_bgr_f,
                    prefixo_chk="chk_bgr_",
                    sufixo_key="bgr",
                    nome_plural="modelo(s) BGR"
                )

                st.markdown("<hr style='margin:14px 0 8px 0;border-color:#333'>", unsafe_allow_html=True)

                hb = st.columns([0.45, 0.7, 2.95, 1.8, 1.4, 0.55, 0.55])

                for h, col in zip(["Sel.", "", "Nome", "Departamento", "Status", "", ""], hb):
                    col.markdown(f"**{h}**")

            else:
                hb = st.columns([0.7, 3.3, 1.8, 1.4, 0.55, 0.55])

                for h, col in zip(["", "Nome", "Departamento", "Status", "", ""], hb):
                    col.markdown(f"**{h}**")

            st.markdown("<hr style='margin:4px 0 8px 0;border-color:#333'>", unsafe_allow_html=True)

            if df_bgr_f.empty:
                st.info("Nenhum modelo BGR encontrado com os filtros selecionados.")

            for _, row_b in df_bgr_f.iterrows():
                id_b = int(row_b["id"])
                nome_b = valor_texto(row_b.get("nome", ""))
                dep_b = valor_texto(row_b.get("departamento", ""))
                stat_b = valor_texto(row_b.get("status", ""))
                img_b = valor_texto(row_b.get("imagem", ""))
                desc_b = valor_texto(row_b.get("descricao", ""))

                if modo_sel_bgr:
                    bc = st.columns([0.45, 0.7, 2.95, 1.8, 1.4, 0.55, 0.55])

                    with bc[0]:
                        checkbox_linha_selecao("ids_sel_bgr", "chk_bgr_", id_b)

                    offset = 1
                else:
                    bc = st.columns([0.7, 3.3, 1.8, 1.4, 0.55, 0.55])
                    offset = 0

                with bc[0 + offset]:
                    if img_b:
                        iu_b = url_publica(BUCKET_IMAGENS, img_b)

                        if iu_b:
                            st.image(iu_b, width=50)

                with bc[1 + offset]:
                    st.markdown(f"**{nome_b}**")
                    st.caption(desc_b[:55] + "…" if len(desc_b) > 55 else desc_b)

                with bc[2 + offset]:
                    st.write(dep_b)

                with bc[3 + offset]:
                    st.markdown(status_html(stat_b), unsafe_allow_html=True)

                with bc[4 + offset]:
                    if st.button("✏️", key=f"edit_bgr_{id_b}"):
                        st.session_state.update({
                            "modo_bgr": "edicao",
                            "editando_bgr": id_b,
                            "expandir_form_bgr": True
                        })
                        rerun()

                with bc[5 + offset]:
                    if st.button("🗑️", key=f"del_bgr_{id_b}"):
                        st.session_state[f"popup_bgr_{id_b}"] = True

                if st.session_state.get(f"popup_bgr_{id_b}", False):
                    st.warning(f"⚠️ Excluir **{nome_b}**?")

                    csb, cnb, _ = st.columns([1, 1, 7])

                    with csb:
                        if st.button("✅ Sim", key=f"sim_bgr_{id_b}"):
                            dados_antes = row_b.to_dict()

                            if adicionar_lixeira("modelos_bgr", dados_antes):
                                if excluir_registro("modelos_bgr", id_b):
                                    registrar_auditoria(
                                        "EXCLUSÃO",
                                        "modelos_bgr",
                                        f"Relatório BGR excluído: {nome_b}",
                                        dados_antes=dados_antes
                                    )

                            st.session_state.pop(f"popup_bgr_{id_b}", None)
                            st.session_state["ids_sel_bgr"].discard(id_b)
                            rerun()

                    with cnb:
                        if st.button("❌ Não", key=f"nao_bgr_{id_b}"):
                            st.session_state.pop(f"popup_bgr_{id_b}", None)
                            rerun()

            ids_sel_bgr = list(st.session_state.get("ids_sel_bgr", set()))

            if st.session_state.get("popup_lote_bgr") and ids_sel_bgr:
                nomes_lb = df_bgr[df_bgr["id"].isin(ids_sel_bgr)]["nome"].astype(str).tolist()

                st.warning(
                    f"⚠️ Confirmar exclusão de **{len(ids_sel_bgr)} modelo(s) BGR**: "
                    f"**{', '.join(nomes_lb)}**?"
                )

                cslb, cnlb, _ = st.columns([1, 1, 7])

                with cslb:
                    if st.button("✅ Confirmar", key="conf_lote_bgr"):
                        for id_lb in ids_sel_bgr:
                            registro_lote_bgr = df_bgr[df_bgr["id"] == int(id_lb)]

                            if registro_lote_bgr.empty:
                                continue

                            r_b = registro_lote_bgr.iloc[0]
                            nome_item = valor_texto(r_b.get("nome", ""))
                            dados_antes = r_b.to_dict()

                            if adicionar_lixeira("modelos_bgr", dados_antes):
                                if excluir_registro("modelos_bgr", int(id_lb)):
                                    registrar_auditoria(
                                        "EXCLUSÃO EM LOTE",
                                        "modelos_bgr",
                                        f"Relatório BGR excluído em lote: {nome_item}",
                                        dados_antes=dados_antes
                                    )

                        st.session_state["ids_sel_bgr"] = set()
                        st.session_state["reset_chk_bgr"] = True
                        st.session_state.pop("popup_lote_bgr", None)

                        st.success("Modelos BGR excluídos!")
                        rerun()

                with cnlb:
                    if st.button("❌ Cancelar", key="canc_lote_bgr"):
                        st.session_state.pop("popup_lote_bgr", None)
                        rerun()

    # =====================================================
    # ABA 3 — DEPARTAMENTOS
    # =====================================================

    with aba3:
        st.subheader("🏷️ Manutenção de Departamentos")

        df_dep = carregar_tabela("departamentos")

        if "modo_dep" not in st.session_state:
            st.session_state["modo_dep"] = "cadastro"

        if "editando_dep" not in st.session_state:
            st.session_state["editando_dep"] = None

        if "expandir_form_dep" not in st.session_state:
            st.session_state["expandir_form_dep"] = False

        if "nonce_dep" not in st.session_state:
            st.session_state["nonce_dep"] = 0

        modo_dep = st.session_state.get("modo_dep", "cadastro")
        id_edit_dep = st.session_state.get("editando_dep")
        dados_dep_edicao = {}

        if modo_dep == "edicao" and id_edit_dep is not None:
            if not df_dep.empty and "id" in df_dep.columns:
                registro_dep = df_dep[df_dep["id"] == int(id_edit_dep)]

                if not registro_dep.empty:
                    dados_dep_edicao = registro_dep.iloc[0].to_dict()
                else:
                    st.warning("Departamento não encontrado para edição.")
                    st.session_state["modo_dep"] = "cadastro"
                    st.session_state["editando_dep"] = None
                    modo_dep = "cadastro"
                    id_edit_dep = None

        titulo_form_dep = "➕ Cadastrar novo departamento"

        if modo_dep == "edicao":
            titulo_form_dep = f"✏️ Editar departamento: {valor_texto(dados_dep_edicao.get('nome', ''))}"

        with st.expander(
            titulo_form_dep,
            expanded=st.session_state.get("expandir_form_dep", True)
        ):
            sufixo_dep = f"{modo_dep}_{id_edit_dep if id_edit_dep is not None else 'novo'}_{st.session_state['nonce_dep']}"

            nome_atual_dep = valor_texto(dados_dep_edicao.get("nome", ""))
            icone_atual_dep = valor_texto(dados_dep_edicao.get("icone", "📁")) or "📁"
            ativo_atual_dep = _bool_supabase(dados_dep_edicao.get("ativo", True))
            ordem_atual_dep = dados_dep_edicao.get("ordem", 999)

            try:
                ordem_atual_dep = int(ordem_atual_dep)
            except Exception:
                ordem_atual_dep = 999

            with st.form(f"form_dep_{sufixo_dep}"):
                dform1, dform2, dform3, dform4 = st.columns([3, 1.2, 1.2, 1.2])

                with dform1:
                    nome_dep_form = st.text_input(
                        "Nome do departamento",
                        value=nome_atual_dep,
                        key=f"nome_dep_form_{sufixo_dep}"
                    )

                with dform2:
                    icone_dep_form = st.text_input(
                        "Ícone",
                        value=icone_atual_dep,
                        key=f"icone_dep_form_{sufixo_dep}"
                    )

                with dform3:
                    ordem_dep_form = st.number_input(
                        "Ordem",
                        min_value=1,
                        max_value=9999,
                        value=ordem_atual_dep,
                        step=1,
                        key=f"ordem_dep_form_{sufixo_dep}"
                    )

                with dform4:
                    ativo_dep_form = st.checkbox(
                        "Ativo",
                        value=ativo_atual_dep,
                        key=f"ativo_dep_form_{sufixo_dep}"
                    )

                bsalvar_dep, bcancelar_dep = st.columns([1, 1])

                with bsalvar_dep:
                    salvar_dep = st.form_submit_button(
                        "💾 Salvar departamento",
                        use_container_width=True
                    )

                with bcancelar_dep:
                    cancelar_dep = st.form_submit_button(
                        "❌ Cancelar",
                        use_container_width=True
                    )

            if cancelar_dep:
                st.session_state["modo_dep"] = "cadastro"
                st.session_state["editando_dep"] = None
                st.session_state["expandir_form_dep"] = False
                st.session_state["nonce_dep"] += 1
                rerun()

            if salvar_dep:
                nome_dep_form = valor_texto(nome_dep_form)
                icone_dep_form = valor_texto(icone_dep_form) or "📁"

                if not nome_departamento_valido(nome_dep_form):
                    st.warning("Informe o nome do departamento.")
                else:
                    dados_salvar_dep = {
                        "nome": nome_dep_form,
                        "icone": icone_dep_form,
                        "ativo": bool(ativo_dep_form),
                        "ordem": int(ordem_dep_form),
                        "data_alteracao": datetime.now().strftime("%d/%m/%Y %H:%M:%S")
                    }

                    if modo_dep == "cadastro":
                        dados_salvar_dep["data_cadastro"] = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

                        if inserir_registro("departamentos", dados_salvar_dep):
                            registrar_auditoria(
                                "CADASTRO",
                                "departamentos",
                                f"Departamento cadastrado: {dados_salvar_dep['nome']}",
                                dados_depois=dados_salvar_dep
                            )

                            st.success("Departamento cadastrado com sucesso!")

                    else:
                        dados_antes_dep = dados_dep_edicao.copy()

                        dados_depois_dep = dados_antes_dep.copy()
                        dados_depois_dep.update(dados_salvar_dep)

                        if atualizar_registro(
                            "departamentos",
                            int(id_edit_dep),
                            dados_salvar_dep
                        ):
                            registrar_auditoria(
                                "ALTERAÇÃO",
                                "departamentos",
                                f"Departamento alterado: {dados_depois_dep['nome']}",
                                dados_antes=dados_antes_dep,
                                dados_depois=dados_depois_dep
                            )

                            st.success("Departamento alterado com sucesso!")

                    st.session_state["modo_dep"] = "cadastro"
                    st.session_state["editando_dep"] = None
                    st.session_state["expandir_form_dep"] = True
                    st.session_state["nonce_dep"] += 1
                    rerun()

        st.write("---")

        df_dep = carregar_tabela("departamentos")

        if df_dep.empty:
            st.info("Nenhum departamento cadastrado.")
        else:
            if "ordem" in df_dep.columns:
                df_dep["ordem_num"] = pd.to_numeric(df_dep["ordem"], errors="coerce").fillna(999)
                df_dep = df_dep.sort_values(["ordem_num", "nome"]).drop(columns=["ordem_num"])

            busca_dep = st.text_input(
                "🔍 Buscar departamento:",
                key="busca_admin_dep"
            )

            filtro_ativo_dep = st.selectbox(
                "Situação:",
                ["Todos", "Ativos", "Inativos"],
                key="filtro_ativo_dep"
            )

            df_dep_f = df_dep.copy()

            if busca_dep:
                df_dep_f = df_dep_f[
                    df_dep_f["nome"].astype(str).str.contains(busca_dep, case=False, na=False)
                ]

            if filtro_ativo_dep == "Ativos" and "ativo" in df_dep_f.columns:
                df_dep_f = df_dep_f[df_dep_f["ativo"].apply(_bool_supabase)]

            if filtro_ativo_dep == "Inativos" and "ativo" in df_dep_f.columns:
                df_dep_f = df_dep_f[~df_dep_f["ativo"].apply(_bool_supabase)]

            st.caption(f"{len(df_dep_f)} departamento(s) encontrado(s).")

            hdep = st.columns([0.7, 3, 1.1, 1.1, 1.4, 0.6, 0.6])

            for h, col in zip(
                ["Ícone", "Nome", "Ordem", "Ativo", "Cadastro", "", ""],
                hdep
            ):
                col.markdown(f"**{h}**")

            st.markdown("<hr style='margin:4px 0 8px 0;border-color:#333'>", unsafe_allow_html=True)

            for _, row_d in df_dep_f.iterrows():
                id_d = int(row_d["id"])
                nome_d = valor_texto(row_d.get("nome", ""))
                icone_d = valor_texto(row_d.get("icone", "")) or "📁"
                ordem_d = valor_texto(row_d.get("ordem", ""))
                ativo_d = _bool_supabase(row_d.get("ativo", True))
                data_cad_d = valor_texto(row_d.get("data_cadastro", ""))

                cd = st.columns([0.7, 3, 1.1, 1.1, 1.4, 0.6, 0.6])

                with cd[0]:
                    st.markdown(f"### {icone_d}")

                with cd[1]:
                    st.markdown(f"**{nome_d}**")

                with cd[2]:
                    st.write(ordem_d)

                with cd[3]:
                    if ativo_d:
                        st.markdown('<span class="status-ativo">● Ativo</span>', unsafe_allow_html=True)
                    else:
                        st.markdown('<span class="status-manutencao">Inativo</span>', unsafe_allow_html=True)

                with cd[4]:
                    st.caption(data_cad_d or "-")

                with cd[5]:
                    if st.button("✏️", key=f"edit_dep_{id_d}"):
                        st.session_state.update({
                            "modo_dep": "edicao",
                            "editando_dep": id_d,
                            "expandir_form_dep": True
                        })
                        rerun()

                with cd[6]:
                    if st.button("🗑️", key=f"del_dep_{id_d}"):
                        st.session_state[f"popup_dep_{id_d}"] = True

                if st.session_state.get(f"popup_dep_{id_d}", False):
                    usado_conv = False
                    usado_bgr = False

                    df_conv_dep = carregar_tabela("conversores")
                    df_bgr_dep = carregar_tabela("modelos_bgr")

                    if not df_conv_dep.empty and "departamento" in df_conv_dep.columns:
                        usado_conv = not df_conv_dep[df_conv_dep["departamento"] == nome_d].empty

                    if not df_bgr_dep.empty and "departamento" in df_bgr_dep.columns:
                        usado_bgr = not df_bgr_dep[df_bgr_dep["departamento"] == nome_d].empty

                    if usado_conv or usado_bgr:
                        st.warning(
                            f"⚠️ O departamento **{nome_d}** possui vínculos com conversores ou relatórios. "
                            "Ele será inativado em vez de excluído."
                        )
                    else:
                        st.warning(f"⚠️ Excluir o departamento **{nome_d}**?")

                    cdep1, cdep2, _ = st.columns([1, 1, 7])

                    with cdep1:
                        if st.button("✅ Sim", key=f"sim_dep_{id_d}"):
                            dados_antes_dep = row_d.to_dict()

                            if usado_conv or usado_bgr:
                                dados_depois_dep = dados_antes_dep.copy()
                                dados_depois_dep["ativo"] = False
                                dados_depois_dep["data_alteracao"] = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

                                if atualizar_registro(
                                    "departamentos",
                                    id_d,
                                    {
                                        "ativo": False,
                                        "data_alteracao": dados_depois_dep["data_alteracao"]
                                    }
                                ):
                                    registrar_auditoria(
                                        "ALTERAÇÃO",
                                        "departamentos",
                                        f"Departamento inativado por possuir vínculos: {nome_d}",
                                        dados_antes=dados_antes_dep,
                                        dados_depois=dados_depois_dep
                                    )
                                    st.success("Departamento inativado.")
                            else:
                                if excluir_registro("departamentos", id_d):
                                    registrar_auditoria(
                                        "EXCLUSÃO",
                                        "departamentos",
                                        f"Departamento excluído: {nome_d}",
                                        dados_antes=dados_antes_dep
                                    )
                                    st.success("Departamento excluído.")

                            st.session_state.pop(f"popup_dep_{id_d}", None)
                            rerun()

                    with cdep2:
                        if st.button("❌ Não", key=f"nao_dep_{id_d}"):
                            st.session_state.pop(f"popup_dep_{id_d}", None)
                            rerun()

            excel_dep = gerar_excel_download({"Departamentos": df_dep_f})

            st.download_button(
                "📥 Exportar departamentos",
                data=excel_dep,
                file_name="departamentos.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                key="dl_dep"
            )

    # =====================================================
    # ABA 4 — SOLICITAÇÕES
    # =====================================================

    with aba4:
        st.subheader("📥 Solicitações de acesso aos BGR")

        departamentos = listar_departamentos(apenas_ativos=True)
        df_sol = carregar_tabela("solicitacoes_bgr")

        if df_sol.empty:
            st.info("Nenhuma solicitação registrada.")
        else:
            s1, s2, s3 = st.columns(3)

            with s1:
                fdep_sol = st.selectbox(
                    "Departamento:",
                    ["Todos"] + departamentos,
                    key="fdep_sol"
                )

            with s2:
                busca_cnpj = st.text_input("CNPJ:", key="busca_cnpj_sol")

            with s3:
                busca_email_sol = st.text_input("E-mail:", key="busca_email_sol")

            df_sol_f = df_sol.copy()

            if fdep_sol != "Todos":
                df_sol_f = df_sol_f[df_sol_f["departamento"] == fdep_sol]

            if busca_cnpj:
                df_sol_f = df_sol_f[
                    df_sol_f["cnpj"].astype(str).str.contains(busca_cnpj, case=False, na=False)
                ]

            if busca_email_sol:
                df_sol_f = df_sol_f[
                    df_sol_f["email_usuario"].astype(str).str.contains(busca_email_sol, case=False, na=False)
                ]

            st.dataframe(df_sol_f, use_container_width=True)

            excel_sol = gerar_excel_download({"Solicitacoes_BGR": df_sol_f})

            st.download_button(
                "📥 Exportar para Excel",
                data=excel_sol,
                file_name="solicitacoes_bgr.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                key="dl_sol"
            )

    # =====================================================
    # ABA 5 — EXPORTAÇÕES
    # =====================================================

    with aba5:
        st.subheader("📦 Exportar bases para Excel")
        st.info("A auditoria é registrada somente ao clicar no botão abaixo.")

        df_lixeira_export = carregar_lixeira(apenas_nao_restaurados=False)

        excel_all = gerar_excel_download({
            "Conversores": carregar_tabela("conversores"),
            "Modelos_BGR": carregar_tabela("modelos_bgr"),
            "Departamentos": carregar_tabela("departamentos"),
            "Solicitacoes_BGR": carregar_tabela("solicitacoes_bgr"),
            "Auditoria": carregar_tabela("auditoria"),
            "Lixeira": df_lixeira_export
        })

        if st.button("📥 Gerar Excel completo", key="btn_gerar_excel"):
            registrar_auditoria(
                "EXPORTAÇÃO",
                "todas",
                "Exportação completa das bases para Excel"
            )

            st.session_state["excel_pronto"] = excel_all
            st.success("Pronto! Clique em Download abaixo.")

        if st.session_state.get("excel_pronto") is not None:
            st.download_button(
                "⬇️ Download Excel",
                data=st.session_state["excel_pronto"],
                file_name="bases_portal_ferramentas.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                key="dl_excel_all"
            )

    # =====================================================
    # ABA 6 — AUDITORIA
    # =====================================================

    with aba6:
        st.subheader("🔍 Auditoria de Movimentações")

        if st.session_state.get("_erro_auditoria"):
            st.error(f"Erro ao registrar auditoria: {st.session_state['_erro_auditoria']}")

        df_aud = carregar_tabela("auditoria")

        if df_aud.empty:
            st.info("Nenhuma movimentação registrada.")
        else:
            if "id" in df_aud.columns:
                df_aud = df_aud.sort_values("id", ascending=False)

            au1, au2, au3 = st.columns(3)

            with au1:
                f_acao = st.selectbox(
                    "Ação:",
                    [
                        "Todas",
                        "CADASTRO",
                        "ALTERAÇÃO",
                        "EDIÇÃO",
                        "EXCLUSÃO",
                        "EXCLUSÃO EM LOTE",
                        "RESTAURAÇÃO",
                        "RESTAURAÇÃO EM LOTE",
                        "EXCLUSÃO DEFINITIVA",
                        "EXCLUSÃO DEFINITIVA EM LOTE",
                        "EXPORTAÇÃO"
                    ],
                    key="f_acao_aud"
                )

            with au2:
                f_tab_aud = st.selectbox(
                    "Tabela:",
                    [
                        "Todas",
                        "conversores",
                        "modelos_bgr",
                        "departamentos",
                        "solicitacoes_bgr",
                        "lixeira",
                        "todas"
                    ],
                    key="f_tab_aud"
                )

            with au3:
                busca_aud = st.text_input(
                    "Buscar descrição:",
                    key="busca_aud"
                )

            df_aud_f = df_aud.copy()

            if f_acao != "Todas" and "acao" in df_aud_f.columns:
                df_aud_f = df_aud_f[df_aud_f["acao"] == f_acao]

            if f_tab_aud != "Todas" and "tabela" in df_aud_f.columns:
                df_aud_f = df_aud_f[df_aud_f["tabela"] == f_tab_aud]

            if busca_aud and "descricao" in df_aud_f.columns:
                df_aud_f = df_aud_f[
                    df_aud_f["descricao"].astype(str).str.contains(
                        busca_aud,
                        case=False,
                        na=False
                    )
                ]

            df_aud_visual = expandir_colunas_auditoria(df_aud_f)

            st.caption(f"{len(df_aud_visual)} registro(s)")
            st.dataframe(df_aud_visual, use_container_width=True)

            excel_aud = gerar_excel_download({"Auditoria": df_aud_visual})

            st.download_button(
                "📥 Exportar auditoria",
                data=excel_aud,
                file_name="auditoria.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                key="dl_aud"
            )

    # =====================================================
    # ABA 7 — LIXEIRA
    # =====================================================

    with aba7:
        render_aba_lixeira()
