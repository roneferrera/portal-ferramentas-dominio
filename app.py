import streamlit as st
import pandas as pd
import unicodedata
import re
import json
import ast
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
BUCKET_BGR = "arquivos-bgr"

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

.stRadio label,
.stCheckbox label {
    color: var(--tr-text-secondary);
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
    box-shadow: 0 4px 16px rgba(0,0,0,0.35);
}

[data-testid="stMetricLabel"] {
    color: var(--tr-text-muted);
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

div[data-testid="stAlert"] {
    border-radius: 10px;
    border: 1px solid var(--tr-border);
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

a:hover {
    color: var(--tr-orange-dark);
}

.lixeira-restaurar {
    padding: 12px 16px;
    border-radius: 10px;
    background-color: var(--tr-danger-bg);
    border: 1px solid #c62828;
    margin-bottom: 10px;
}

.lixeira-restaurar strong {
    color: var(--tr-danger-text);
}

/* Botão ➕/➖ compacto */
div[data-testid="stButton"] button[kind="secondary"] {
    padding: 2px 8px !important;
    font-size: 16px !important;
    line-height: 1 !important;
    min-height: unset !important;
    border-radius: 6px !important;
}

/* =====================================================
   MODO SELEÇÃO OTIMIZADO
   ===================================================== */

.sel-top {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 12px;
    padding-bottom: 8px;
}

.sel-title {
    font-size: 18px;
    font-weight: 800;
    color: #F5F5F5;
    margin-bottom: 2px;
}

.sel-subtitle {
    font-size: 12px;
    color: #A8A8A8;
}

.sel-pill {
    display: inline-block;
    padding: 6px 14px;
    border-radius: 999px;
    background: rgba(255, 128, 0, 0.16);
    border: 1px solid rgba(255, 128, 0, 0.45);
    color: #FFB366;
    font-size: 12px;
    font-weight: 800;
    white-space: nowrap;
}

.sel-tip {
    padding-top: 7px;
    font-size: 12px;
    color: #A8A8A8;
}

.sel-ok {
    padding-top: 7px;
    font-size: 12px;
    color: #81C784;
    font-weight: 700;
}

.row-selected-tag {
    display: inline-block;
    margin-left: 8px;
    padding: 2px 8px;
    border-radius: 999px;
    background: rgba(255, 128, 0, 0.16);
    color: #FFB366;
    border: 1px solid rgba(255, 128, 0, 0.45);
    font-size: 11px;
    font-weight: 800;
}

div[data-testid="stButton"] button {
    white-space: nowrap;
}
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
        resp = sb.table(tabela).select("*").execute()
        return pd.DataFrame(resp.data) if resp.data else pd.DataFrame()
    except Exception as e:
        st.error(f"Erro ao carregar '{tabela}': {e}")
        return pd.DataFrame()

def inserir_registro(tabela: str, dados: dict):
    try:
        get_supabase().table(tabela).insert(dados).execute()
    except Exception as e:
        st.error(f"Erro ao inserir em '{tabela}': {e}")

def atualizar_registro(tabela: str, id_registro: int, dados: dict):
    try:
        get_supabase().table(tabela).update(dados).eq("id", id_registro).execute()
    except Exception as e:
        st.error(f"Erro ao atualizar em '{tabela}': {e}")

def excluir_registro(tabela: str, id_registro: int):
    try:
        get_supabase().table(tabela).delete().eq("id", id_registro).execute()
    except Exception as e:
        st.error(f"Erro ao excluir em '{tabela}': {e}")

# =========================================================
# SUPABASE — STORAGE
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
# AUDITORIA
# =========================================================

def registrar_auditoria(acao, tabela, descricao, dados_antes="", dados_depois=""):
    try:
        inserir_registro("auditoria", {
            "data_hora": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
            "acao": acao,
            "tabela": tabela,
            "descricao": descricao,
            "dados_antes": dados_antes,
            "dados_depois": dados_depois
        })
    except Exception as e:
        st.warning(f"Auditoria não registrada: {e}")

# =========================================================
# LIXEIRA
# =========================================================

def adicionar_lixeira(tabela, registro):
    if "lixeira" not in st.session_state:
        st.session_state["lixeira"] = []

    st.session_state["lixeira"].append({
        "tabela": tabela,
        "registro": registro,
        "excluido_em": datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    })

def mostrar_lixeira():
    lixeira = st.session_state.get("lixeira", [])

    if not lixeira:
        return

    for i, item in enumerate(lixeira):
        nome_reg = item["registro"].get("nome", f"Registro #{i+1}")

        cm, cr, cf = st.columns([5, 1.5, 1])

        with cm:
            st.markdown(
                f'<div class="lixeira-restaurar">🗑️ <strong>"{nome_reg}"</strong> excluído — {item["excluido_em"]}</div>',
                unsafe_allow_html=True
            )

        with cr:
            if st.button("↩️ Restaurar", key=f"restaurar_{i}"):
                d = {k: v for k, v in item["registro"].items() if k != "id"}

                inserir_registro(item["tabela"], d)

                registrar_auditoria(
                    "RESTAURAÇÃO",
                    item["tabela"],
                    f"Restaurado: {nome_reg}",
                    dados_depois=str(d)
                )

                st.session_state["lixeira"].pop(i)
                st.success(f'"{nome_reg}" restaurado!')
                st.rerun()

        with cf:
            if st.button("✖", key=f"fechar_lixeira_{i}"):
                st.session_state["lixeira"].pop(i)
                st.rerun()

# =========================================================
# FUNÇÕES AUXILIARES
# =========================================================

def inicializar_conversores_padrao():
    df = carregar_tabela("conversores")

    if not df.empty:
        return

    for c in [
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
        },
    ]:
        c["data_cadastro"] = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        inserir_registro("conversores", c)

def status_html(status):
    if status == "Ativo":
        return '<span class="status-ativo">● Ativo</span>'
    elif status == "Em manutenção":
        return '<span class="status-manutencao">⚙ Em manutenção</span>'

    return '<span class="status-desenvolvimento">🔧 Em desenvolvimento</span>'

def gerar_excel_download(dfs: dict):
    out = BytesIO()

    with pd.ExcelWriter(out, engine="openpyxl") as w:
        for nome, df in dfs.items():
            df.to_excel(w, index=False, sheet_name=nome[:31])

    return out.getvalue()

def mostrar_logo():
    st.sidebar.markdown("### 🧩 Portal de Ferramentas")

def nome_arquivo_seguro(nome):
    nome = unicodedata.normalize("NFKD", nome)
    nome = "".join(c for c in nome if not unicodedata.combining(c))
    nome = re.sub(r"[^\w\.\-]", "_", nome)

    p = nome.rsplit(".", 1)

    return p[0].replace(".", "_") + "." + p[1] if len(p) == 2 else nome

def valor_texto(v):
    if v is None:
        return ""

    if isinstance(v, float) and pd.isna(v):
        return ""

    return str(v).strip()

def email_valido(email):
    return "@" in str(email).strip() and "." in str(email).strip()

# =========================================================
# SELEÇÃO MÚLTIPLA — CORRIGIDA E OTIMIZADA
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

    # Mantém o checkbox visual sincronizado com o set de IDs.
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
        st.markdown(
            f"""
            <div class="sel-top">
                <div>
                    <div class="sel-title">☑️ Seleção em lote</div>
                    <div class="sel-subtitle">
                        {qtd} de {total} {nome_plural} filtrado(s) selecionado(s)
                    </div>
                </div>
                <div class="sel-pill">{qtd} selecionado(s)</div>
            </div>
            """,
            unsafe_allow_html=True
        )

        b1, b2, b3, b4 = st.columns([1.5, 1.1, 1.2, 3.5])

        with b1:
            if st.button(
                "✅ Marcar filtrados",
                key=f"sel_todos_{sufixo_key}",
                use_container_width=True
            ):
                selecionar_todos_filtrados(key_ids, df_filtrado, prefixo_chk)
                st.rerun()

        with b2:
            if st.button(
                "🧹 Limpar",
                key=f"limpar_sel_{sufixo_key}",
                use_container_width=True
            ):
                limpar_selecao(key_ids, prefixo_chk)
                st.session_state.pop(f"popup_lote_{sufixo_key}", None)
                st.rerun()

        with b3:
            if st.button(
                "🗑️ Excluir",
                key=f"btn_lote_{sufixo_key}",
                disabled=qtd == 0,
                use_container_width=True
            ):
                st.session_state[f"popup_lote_{sufixo_key}"] = True
                st.rerun()

        with b4:
            if qtd > 0:
                st.markdown(
                    f"<div class='sel-ok'>Pronto para excluir {qtd} item(ns). A confirmação aparecerá abaixo da lista.</div>",
                    unsafe_allow_html=True
                )
            else:
                st.markdown(
                    '<div class="sel-tip">Marque itens individualmente ou use <strong>Marcar filtrados</strong>.</div>',
                    unsafe_allow_html=True
                )

    return qtd

# =========================================================
# LISTA PÚBLICA
# =========================================================

_COLS = [0.7, 2.8, 3.2, 2.0, 1.4, 1.3]
_CAB = ["Expandir /\nOcultar", "Nome", "Descrição", "Departamento", "Status", "Acesso"]
_CAB_STYLE = "font-size:11px;font-weight:700;color:#A8A8A8;text-transform:uppercase;letter-spacing:.05em"

def _render_lista_publica(df_filtrado: pd.DataFrame, tipo: str):
    if df_filtrado.empty:
        st.info("Nenhum item encontrado para os filtros selecionados.")
        return

    st.caption(f"{len(df_filtrado)} item(s) encontrado(s)")

    cols_cab = st.columns(_COLS)

    for col, titulo in zip(cols_cab, _CAB):
        col.markdown(f"<span style='{_CAB_STYLE}'>{titulo}</span>", unsafe_allow_html=True)

    st.markdown("<hr style='margin:4px 0 6px 0;border-color:#444'>", unsafe_allow_html=True)

    for idx, row in df_filtrado.iterrows():
        nome_i = valor_texto(row.get("nome", ""))
        dep_i = valor_texto(row.get("departamento", ""))
        desc_i = valor_texto(row.get("descricao", ""))
        stat_i = valor_texto(row.get("status", ""))
        url_i = valor_texto(row.get("url", ""))
        img_i = valor_texto(row.get("imagem", ""))
        bgr_i = valor_texto(row.get("arquivo_bgr", ""))
        data_i = valor_texto(row.get("data_cadastro", row.get("data_upload", "")))

        desc_curta = (desc_i[:45] + "…") if len(desc_i) > 45 else desc_i

        chave_exp = f"exp_{tipo}_{idx}"
        expandido = st.session_state.get(chave_exp, False)

        c0, c1, c2, c3, c4, c5 = st.columns(_COLS)

        with c0:
            btn_ico = "➖" if expandido else "➕"

            if st.button(
                btn_ico,
                key=f"toggle_{tipo}_{idx}",
                help="Expandir / Ocultar detalhes",
                use_container_width=False
            ):
                st.session_state[chave_exp] = not expandido
                st.rerun()

        with c1:
            st.markdown(
                f"<span style='font-weight:700;color:#F5F5F5;font-size:13px'>{nome_i}</span>",
                unsafe_allow_html=True
            )

        with c2:
            st.markdown(
                f"<span style='color:#A8A8A8;font-size:12px'>{desc_curta}</span>",
                unsafe_allow_html=True
            )

        with c3:
            st.markdown(
                f"<span style='color:#D0D0D0;font-size:12px'>{dep_i}</span>",
                unsafe_allow_html=True
            )

        with c4:
            st.markdown(status_html(stat_i), unsafe_allow_html=True)

        with c5:
            if tipo == "conversor":
                if stat_i == "Ativo" and url_i:
                    st.markdown(
                        f'<a class="botao-link" href="{url_i}" target="_blank">🔗 Acessar</a>',
                        unsafe_allow_html=True
                    )
                elif stat_i == "Em manutenção":
                    st.markdown('<span class="status-manutencao">⚙ Manutenção</span>', unsafe_allow_html=True)
                else:
                    st.markdown('<span class="status-desenvolvimento">🔧 Em dev.</span>', unsafe_allow_html=True)
            else:
                if bgr_i:
                    st.markdown('<span class="status-ativo">📄 BGR</span>', unsafe_allow_html=True)
                else:
                    st.markdown('<span class="status-desenvolvimento">📄 Sem arq.</span>', unsafe_allow_html=True)

        if expandido:
            st.markdown(
                "<div style='background:#1a1a1a;border:1px solid #FF8000;"
                "border-radius:10px;padding:20px 24px;margin:4px 0 10px 0'>",
                unsafe_allow_html=True
            )

            d1, d2 = st.columns([3, 1])

            with d1:
                st.markdown(f"**Nome:** {nome_i}")
                st.markdown(f"**Descrição:** {desc_i}")
                st.markdown(f"**Departamento:** {dep_i}")
                st.markdown(f"**Status:** {status_html(stat_i)}", unsafe_allow_html=True)

                if data_i:
                    st.markdown(f"**Data de cadastro:** {data_i}")

                if stat_i == "Em manutenção":
                    st.warning("Esta ferramenta está temporariamente em manutenção.")
                elif stat_i == "Em desenvolvimento":
                    st.info("Esta ferramenta está em desenvolvimento.")

            with d2:
                if img_i:
                    iu = url_publica(BUCKET_IMAGENS, img_i)

                    if iu:
                        st.image(iu, caption="Prévia", use_container_width=True)

            if tipo == "bgr" and bgr_i:
                st.write("---")
                st.markdown("**Preencha os dados para liberar o download:**")

                with st.form(f"form_bgr_pub_{idx}"):
                    fc1, fc2 = st.columns(2)

                    with fc1:
                        nome_u = st.text_input("Nome", key=f"bgr_nome_{idx}")
                        email_u = st.text_input("E-mail", key=f"bgr_email_{idx}")
                        cnpj_u = st.text_input("CNPJ", key=f"bgr_cnpj_{idx}")

                    with fc2:
                        cod_u = st.text_input("Código cliente Domínio", key=f"bgr_cod_{idx}")
                        obs_u = st.text_area("Observações", key=f"bgr_obs_{idx}", height=90)

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
                            inserir_registro("solicitacoes_bgr", {
                                "data_hora": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
                                "nome_usuario": nome_u,
                                "email_usuario": email_u,
                                "cnpj": cnpj_u,
                                "codigo_cliente_dominio": cod_u,
                                "departamento": dep_i,
                                "modelo": nome_i,
                                "arquivo_bgr": bgr_i,
                                "observacao": obs_u,
                                "status": "Liberado"
                            })

                            st.session_state[f"bgr_liberado_{idx}"] = True
                            st.success("Solicitação registrada! Download liberado.")

                if st.session_state.get(f"bgr_liberado_{idx}", False):
                    bgr_bytes = baixar_arquivo(BUCKET_BGR, bgr_i)

                    if bgr_bytes:
                        st.download_button(
                            "⬇️ Baixar .BGR",
                            data=bgr_bytes,
                            file_name=bgr_i,
                            mime="application/octet-stream",
                            key=f"dl_bgr_pub_{idx}"
                        )

            st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("<hr style='margin:2px 0 2px 0;border-color:#2a2a2a'>", unsafe_allow_html=True)

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

    df_conversores = carregar_tabela("conversores")
    df_modelos = carregar_tabela("modelos_bgr")
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
            qtd = len(df_conversores[df_conversores["departamento"] == dep]) if not df_conversores.empty else 0

            st.markdown(f"""
            <div class="setor-card">
                <h1>{icones[dep]}</h1>
                <h4>{dep}</h4>
                <p>{qtd} ferramenta(s)</p>
            </div>
            """, unsafe_allow_html=True)

# =========================================================
# CONVERSORES
# =========================================================

elif pagina == "Conversores":
    st.title("🛠️ Conversores")

    df = carregar_tabela("conversores")

    fc1, fc2, fc3 = st.columns([3, 2, 2])

    with fc1:
        busca_conv = st.text_input(
            "🔍 Buscar:",
            placeholder="Nome ou descrição...",
            key="busca_conv_pub"
        )

    with fc2:
        filtro_dep_conv = st.selectbox(
            "Departamento:",
            ["Todos"] + DEPARTAMENTOS,
            key="fdep_conv_pub"
        )

    with fc3:
        filtro_stat_conv = st.selectbox(
            "Status:",
            ["Todos"] + STATUS_FERRAMENTAS,
            key="fstat_conv_pub"
        )

    df_f = df.copy()

    if not df_f.empty:
        if busca_conv:
            df_f = df_f[
                df_f["nome"].str.contains(busca_conv, case=False, na=False) |
                df_f["descricao"].str.contains(busca_conv, case=False, na=False)
            ]

        if filtro_dep_conv != "Todos":
            df_f = df_f[df_f["departamento"] == filtro_dep_conv]

        if filtro_stat_conv != "Todos":
            df_f = df_f[df_f["status"] == filtro_stat_conv]

    st.write("---")
    _render_lista_publica(df_f, tipo="conversor")

# =========================================================
# RELATÓRIOS BGR
# =========================================================

elif pagina == "Relatórios BGR":
    st.title("📄 Relatórios BGR")
    st.write("Clique em ➕ para ver os detalhes e solicitar o arquivo `.bgr`.")

    df_modelos = carregar_tabela("modelos_bgr")

    fb1, fb2, fb3 = st.columns([3, 2, 2])

    with fb1:
        busca_bgr = st.text_input(
            "🔍 Buscar:",
            placeholder="Nome ou descrição...",
            key="busca_bgr_pub"
        )

    with fb2:
        filtro_dep_bgr = st.selectbox(
            "Departamento:",
            ["Todos"] + DEPARTAMENTOS,
            key="fdep_bgr_pub"
        )

    with fb3:
        filtro_stat_bgr = st.selectbox(
            "Status:",
            ["Todos"] + STATUS_FERRAMENTAS,
            key="fstat_bgr_pub"
        )

    df_bgr_f = pd.DataFrame()

    if not df_modelos.empty:
        df_bgr_f = df_modelos.copy()

        if busca_bgr:
            df_bgr_f = df_bgr_f[
                df_bgr_f["nome"].str.contains(busca_bgr, case=False, na=False) |
                df_bgr_f["descricao"].str.contains(busca_bgr, case=False, na=False)
            ]

        if filtro_dep_bgr != "Todos":
            df_bgr_f = df_bgr_f[df_bgr_f["departamento"] == filtro_dep_bgr]

        if filtro_stat_bgr != "Todos":
            df_bgr_f = df_bgr_f[df_bgr_f["status"] == filtro_stat_bgr]
        else:
            df_bgr_f = df_bgr_f[df_bgr_f["status"] == "Ativo"]

    st.write("---")
    _render_lista_publica(df_bgr_f, tipo="bgr")

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
    mostrar_lixeira()

    aba1, aba2, aba3, aba4, aba5 = st.tabs([
        "🛠️ Conversores",
        "📄 Modelos BGR",
        "📥 Solicitações",
        "📦 Exportações",
        "🔍 Auditoria"
    ])

    # =====================================================
    # ABA 1 — CONVERSORES
    # =====================================================

    with aba1:
        st.subheader("🛠️ Gerenciar Conversores")

        df_conv = carregar_tabela("conversores")

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
                    ["Todos"] + DEPARTAMENTOS,
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

                hc = st.columns([0.45, 3.15, 1.8, 1.4, 0.55, 0.55])

                for h, col in zip(["Sel.", "Nome", "Departamento", "Status", "", ""], hc):
                    col.markdown(f"**{h}**")

            else:
                hc = st.columns([3.6, 1.8, 1.4, 0.55, 0.55])

                for h, col in zip(["Nome", "Departamento", "Status", "", ""], hc):
                    col.markdown(f"**{h}**")

            st.markdown("<hr style='margin:4px 0 8px 0;border-color:#333'>", unsafe_allow_html=True)

            if df_conv_f.empty:
                st.info("Nenhum conversor encontrado com os filtros selecionados.")

            for _, row_c in df_conv_f.iterrows():
                id_c = int(row_c["id"])
                nome_c = valor_texto(row_c["nome"])
                dep_c = valor_texto(row_c["departamento"])
                stat_c = valor_texto(row_c["status"])

                if modo_sel_conv:
                    cc = st.columns([0.45, 3.15, 1.8, 1.4, 0.55, 0.55])

                    with cc[0]:
                        checkbox_linha_selecao("ids_sel_conv", "chk_conv_", id_c)

                    with cc[1]:
                        if id_c in st.session_state["ids_sel_conv"]:
                            st.markdown(
                                f"**{nome_c}** <span class='row-selected-tag'>Selecionado</span>",
                                unsafe_allow_html=True
                            )
                        else:
                            st.markdown(f"**{nome_c}**")

                    with cc[2]:
                        st.write(dep_c)

                    with cc[3]:
                        st.markdown(status_html(stat_c), unsafe_allow_html=True)

                    with cc[4]:
                        if st.button("✏️", key=f"edit_conv_{id_c}"):
                            st.session_state.update({
                                "modo_conv": "edicao",
                                "editando_conv": id_c,
                                "expandir_form_conv": True
                            })
                            st.rerun()

                    with cc[5]:
                        if st.button("🗑️", key=f"del_conv_{id_c}"):
                            st.session_state[f"popup_conv_{id_c}"] = True

                else:
                    cc = st.columns([3.6, 1.8, 1.4, 0.55, 0.55])

                    with cc[0]:
                        st.markdown(f"**{nome_c}**")

                    with cc[1]:
                        st.write(dep_c)

                    with cc[2]:
                        st.markdown(status_html(stat_c), unsafe_allow_html=True)

                    with cc[3]:
                        if st.button("✏️", key=f"edit_conv_{id_c}"):
                            st.session_state.update({
                                "modo_conv": "edicao",
                                "editando_conv": id_c,
                                "expandir_form_conv": True
                            })
                            st.rerun()

                    with cc[4]:
                        if st.button("🗑️", key=f"del_conv_{id_c}"):
                            st.session_state[f"popup_conv_{id_c}"] = True

                if st.session_state.get(f"popup_conv_{id_c}", False):
                    st.warning(f"⚠️ Excluir **{nome_c}**?")

                    cs, cn, _ = st.columns([1, 1, 7])

                    with cs:
                        if st.button("✅ Sim", key=f"sim_conv_{id_c}"):
                            adicionar_lixeira("conversores", row_c.to_dict())
                            excluir_registro("conversores", id_c)

                            registrar_auditoria(
                                "EXCLUSÃO",
                                "conversores",
                                f"Excluído: {nome_c}",
                                str(row_c.to_dict())
                            )

                            st.session_state.pop(f"popup_conv_{id_c}", None)
                            st.session_state["ids_sel_conv"].discard(id_c)

                            st.rerun()

                    with cn:
                        if st.button("❌ Não", key=f"nao_conv_{id_c}"):
                            st.session_state.pop(f"popup_conv_{id_c}", None)
                            st.rerun()

            ids_sel_conv = list(st.session_state.get("ids_sel_conv", set()))

            if st.session_state.get("popup_lote_conv") and ids_sel_conv:
                nomes_l = df_conv[df_conv["id"].isin(ids_sel_conv)]["nome"].tolist()

                st.warning(
                    f"⚠️ Confirmar exclusão de **{len(ids_sel_conv)} conversor(es)**: "
                    f"**{', '.join(nomes_l)}**?"
                )

                csl, cnl, _ = st.columns([1, 1, 7])

                with csl:
                    if st.button("✅ Confirmar", key="conf_lote_conv"):
                        for id_l in ids_sel_conv:
                            r = df_conv[df_conv["id"] == id_l].iloc[0]

                            adicionar_lixeira("conversores", r.to_dict())
                            excluir_registro("conversores", int(id_l))

                        registrar_auditoria(
                            "EXCLUSÃO EM LOTE",
                            "conversores",
                            f"Excluídos: {', '.join(nomes_l)}"
                        )

                        st.session_state["ids_sel_conv"] = set()
                        st.session_state["reset_chk_conv"] = True
                        st.session_state.pop("popup_lote_conv", None)

                        st.success("Conversores excluídos!")
                        st.rerun()

                with cnl:
                    if st.button("❌ Cancelar", key="canc_lote_conv"):
                        st.session_state.pop("popup_lote_conv", None)
                        st.rerun()

    # =====================================================
    # ABA 2 — MODELOS BGR
    # =====================================================

    with aba2:
        st.subheader("📄 Gerenciar Modelos BGR")

        df_bgr = carregar_tabela("modelos_bgr")

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
                    ["Todos"] + DEPARTAMENTOS,
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
                nome_b = valor_texto(row_b["nome"])
                dep_b = valor_texto(row_b["departamento"])
                stat_b = valor_texto(row_b["status"])
                img_b = valor_texto(row_b.get("imagem", ""))
                desc_b = valor_texto(row_b.get("descricao", ""))

                if modo_sel_bgr:
                    bc = st.columns([0.45, 0.7, 2.95, 1.8, 1.4, 0.55, 0.55])

                    with bc[0]:
                        checkbox_linha_selecao("ids_sel_bgr", "chk_bgr_", id_b)

                    with bc[1]:
                        if img_b:
                            iu_b = url_publica(BUCKET_IMAGENS, img_b)

                            if iu_b:
                                st.image(iu_b, width=50)

                    with bc[2]:
                        if id_b in st.session_state["ids_sel_bgr"]:
                            st.markdown(
                                f"**{nome_b}** <span class='row-selected-tag'>Selecionado</span>",
                                unsafe_allow_html=True
                            )
                        else:
                            st.markdown(f"**{nome_b}**")

                        st.caption(desc_b[:55] + "…" if len(desc_b) > 55 else desc_b)

                    with bc[3]:
                        st.write(dep_b)

                    with bc[4]:
                        st.markdown(status_html(stat_b), unsafe_allow_html=True)

                    with bc[5]:
                        if st.button("✏️", key=f"edit_bgr_{id_b}"):
                            st.session_state.update({
                                "modo_bgr": "edicao",
                                "editando_bgr": id_b,
                                "expandir_form_bgr": True
                            })
                            st.rerun()

                    with bc[6]:
                        if st.button("🗑️", key=f"del_bgr_{id_b}"):
                            st.session_state[f"popup_bgr_{id_b}"] = True

                else:
                    bc = st.columns([0.7, 3.3, 1.8, 1.4, 0.55, 0.55])

                    with bc[0]:
                        if img_b:
                            iu_b = url_publica(BUCKET_IMAGENS, img_b)

                            if iu_b:
                                st.image(iu_b, width=50)

                    with bc[1]:
                        st.markdown(f"**{nome_b}**")
                        st.caption(desc_b[:55] + "…" if len(desc_b) > 55 else desc_b)

                    with bc[2]:
                        st.write(dep_b)

                    with bc[3]:
                        st.markdown(status_html(stat_b), unsafe_allow_html=True)

                    with bc[4]:
                        if st.button("✏️", key=f"edit_bgr_{id_b}"):
                            st.session_state.update({
                                "modo_bgr": "edicao",
                                "editando_bgr": id_b,
                                "expandir_form_bgr": True
                            })
                            st.rerun()

                    with bc[5]:
                        if st.button("🗑️", key=f"del_bgr_{id_b}"):
                            st.session_state[f"popup_bgr_{id_b}"] = True

                if st.session_state.get(f"popup_bgr_{id_b}", False):
                    st.warning(f"⚠️ Excluir **{nome_b}**?")

                    csb, cnb, _ = st.columns([1, 1, 7])

                    with csb:
                        if st.button("✅ Sim", key=f"sim_bgr_{id_b}"):
                            adicionar_lixeira("modelos_bgr", row_b.to_dict())
                            excluir_registro("modelos_bgr", id_b)

                            registrar_auditoria(
                                "EXCLUSÃO",
                                "modelos_bgr",
                                f"BGR excluído: {nome_b}",
                                str(row_b.to_dict())
                            )

                            st.session_state.pop(f"popup_bgr_{id_b}", None)
                            st.session_state["ids_sel_bgr"].discard(id_b)

                            st.rerun()

                    with cnb:
                        if st.button("❌ Não", key=f"nao_bgr_{id_b}"):
                            st.session_state.pop(f"popup_bgr_{id_b}", None)
                            st.rerun()

            ids_sel_bgr = list(st.session_state.get("ids_sel_bgr", set()))

            if st.session_state.get("popup_lote_bgr") and ids_sel_bgr:
                nomes_lb = df_bgr[df_bgr["id"].isin(ids_sel_bgr)]["nome"].tolist()

                st.warning(
                    f"⚠️ Confirmar exclusão de **{len(ids_sel_bgr)} modelo(s) BGR**: "
                    f"**{', '.join(nomes_lb)}**?"
                )

                cslb, cnlb, _ = st.columns([1, 1, 7])

                with cslb:
                    if st.button("✅ Confirmar", key="conf_lote_bgr"):
                        for id_lb in ids_sel_bgr:
                            r_b = df_bgr[df_bgr["id"] == id_lb].iloc[0]

                            adicionar_lixeira("modelos_bgr", r_b.to_dict())
                            excluir_registro("modelos_bgr", int(id_lb))

                        registrar_auditoria(
                            "EXCLUSÃO EM LOTE",
                            "modelos_bgr",
                            f"Excluídos: {', '.join(nomes_lb)}"
                        )

                        st.session_state["ids_sel_bgr"] = set()
                        st.session_state["reset_chk_bgr"] = True
                        st.session_state.pop("popup_lote_bgr", None)

                        st.success("Modelos BGR excluídos!")
                        st.rerun()

                with cnlb:
                    if st.button("❌ Cancelar", key="canc_lote_bgr"):
                        st.session_state.pop("popup_lote_bgr", None)
                        st.rerun()

    # =====================================================
    # ABA 3 — SOLICITAÇÕES
    # =====================================================

    with aba3:
        st.subheader("📥 Solicitações de acesso aos BGR")

        df_sol = carregar_tabela("solicitacoes_bgr")

        if df_sol.empty:
            st.info("Nenhuma solicitação registrada.")
        else:
            s1, s2, s3 = st.columns(3)

            with s1:
                fdep_sol = st.selectbox(
                    "Departamento:",
                    ["Todos"] + DEPARTAMENTOS,
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
    # ABA 4 — EXPORTAÇÕES
    # =====================================================

    with aba4:
        st.subheader("📦 Exportar bases para Excel")
        st.info("A auditoria é registrada somente ao clicar no botão abaixo.")

        excel_all = gerar_excel_download({
            "Conversores": carregar_tabela("conversores"),
            "Modelos_BGR": carregar_tabela("modelos_bgr"),
            "Solicitacoes_BGR": carregar_tabela("solicitacoes_bgr"),
            "Auditoria": carregar_tabela("auditoria"),
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
    # ABA 5 — AUDITORIA
    # =====================================================

def registrar_auditoria(acao, tabela, descricao, dados_antes="", dados_depois=""):
    try:
        inserir_registro("auditoria", {
            "data_hora": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
            "acao": acao,
            "tabela": tabela,
            "descricao": descricao,
            "dados_antes": dados_antes,
            "dados_depois": dados_depois
        })
    except Exception as e:
        st.warning(f"Auditoria não registrada: {e}")
