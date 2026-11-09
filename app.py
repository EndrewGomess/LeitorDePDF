import ast
import base64
import json
import os
import sys
from pathlib import Path
from types import ModuleType

import streamlit as st
from google import genai


RAIZ = Path(__file__).resolve().parent
NOTEBOOK = RAIZ / "leitor_pdf_rpg.ipynb"
IMAGENS_FUNDO = RAIZ / "Imagens"
CELULAS_MOTOR = ("leitor-02", "leitor-06", "leitor-08", "leitor-10", "leitor-12")
IMPORTS_COLAB = {"google.colab", "IPython.display"}
IMPORTS_SEMANTICOS = {"torch", "sentence_transformers"}


@st.cache_resource(show_spinner=False)
def carregar_motor(semantica):
    """Carrega somente o código do motor do notebook que acompanha o projeto."""
    notebook = json.loads(NOTEBOOK.read_text(encoding="utf-8-sig"))
    celulas = {c.get("id"): c for c in notebook["cells"] if c["cell_type"] == "code"}
    nome = f"_leitor_pdf_motor_{semantica}"
    motor = ModuleType(nome)
    sys.modules[nome] = motor
    ignorados = IMPORTS_COLAB if semantica else IMPORTS_COLAB | IMPORTS_SEMANTICOS
    try:
        for id_ in CELULAS_MOTOR:
            arquivo = f"{NOTEBOOK} ({id_})"
            codigo = ast.parse("".join(celulas[id_]["source"]), filename=arquivo)
            if id_ == CELULAS_MOTOR[0]:
                codigo.body = [
                    linha for linha in codigo.body
                    if not (
                        isinstance(linha, ast.ImportFrom) and linha.module in ignorados
                        or isinstance(linha, ast.Import) and all(
                            alias.name in ignorados for alias in linha.names
                        )
                    )
                ]
            exec(compile(codigo, arquivo, "exec"), vars(motor))

        configuracao = ast.parse("".join(celulas["leitor-04"]["source"]))
        for linha in configuracao.body:
            if isinstance(linha, ast.Assign) and len(linha.targets) == 1:
                alvo = linha.targets[0]
                if isinstance(alvo, ast.Name) and alvo.id in {"AJUSTES", "MODELO_GEMINI"}:
                    setattr(motor, alvo.id, ast.literal_eval(linha.value))
    except Exception:
        sys.modules.pop(nome, None)
        raise
    return motor


@st.cache_data(show_spinner=False)
def imagem_em_base64(caminho, modificado_em):
    del modificado_em
    return base64.b64encode(Path(caminho).read_bytes()).decode("ascii")


def aplicar_identidade_visual():
    extensoes = {".jpg", ".jpeg", ".jfif", ".png", ".webp"}
    caminhos = sorted(
        caminho for caminho in IMAGENS_FUNDO.iterdir()
        if caminho.is_file() and caminho.suffix.lower() in extensoes
    ) if IMAGENS_FUNDO.is_dir() else []
    dragao = IMAGENS_FUNDO / "dragonbattle.jfif"
    if dragao in caminhos:
        caminhos.remove(dragao)
        caminhos.insert(0, dragao)
    fundos = [
        f"url('data:image/{'jpeg' if caminho.suffix.lower() in {'.jpg', '.jpeg', '.jfif'} else 'png' if caminho.suffix.lower() == '.png' else 'webp'};base64,{imagem_em_base64(str(caminho), caminho.stat().st_mtime_ns)}')"
        for caminho in caminhos
    ]
    imagem_inicial = fundos[0] if fundos else "none"
    quadros = "\n".join(
        f"{indice * 100 / len(fundos):.4f}% {{ background-image: linear-gradient(110deg, rgba(7, 9, 11, .42), rgba(7, 9, 11, .72)), {imagem}; }}"
        for indice, imagem in enumerate(fundos)
    ) if len(fundos) > 1 else ""
    if len(fundos) > 1:
        quadros += f"\n100% {{ background-image: linear-gradient(110deg, rgba(7, 9, 11, .42), rgba(7, 9, 11, .72)), {imagem_inicial}; }}"
        duracao_fundo = f"{30 * len(fundos)}s"
    else:
        duracao_fundo = "0s"

    st.html(
        f"""
        <style>
        :root {{
            --arcano-azul: #6F96AD;
            --arcano-lilas: #B9A36D;
            --ouro-antigo: #D9792B;
            --noite: #090B0D;
            --vidro: rgba(15, 17, 18, 0.92);
        }}

        .stApp {{
            background-color: #090B0D;
            background-image: linear-gradient(90deg, rgba(6, 8, 10, .30), rgba(6, 8, 10, .72)), {imagem_inicial};
            background-attachment: fixed;
            background-position: center;
            background-size: cover;
            background-repeat: no-repeat;
            animation: {"alternar-imagens " + duracao_fundo + " steps(1, end) infinite" if len(fundos) > 1 else "none"};
        }}
        {"@keyframes alternar-imagens { " + quadros + " }" if len(fundos) > 1 else ""}
        .stApp {{ color: #EEE5D2; }}

        [data-testid="stAlert"] {{
            background: rgba(30, 26, 20, .92);
            color: #EEE5D2;
            border: 1px solid rgba(217, 121, 43, .35);
        }}

        .stMainBlockContainer {{
            max-width: 1040px;
            margin-top: 2rem;
            margin-bottom: 2rem;
            padding: 2.15rem 2.6rem 7rem;
            background: linear-gradient(145deg, rgba(12, 14, 15, .94), rgba(21, 24, 26, .91));
            border: 1px solid rgba(185, 163, 109, .35);
            border-radius: 28px;
            box-shadow: 0 28px 80px rgba(0, 0, 0, .48), inset 0 1px rgba(255, 255, 255, .06);
            backdrop-filter: blur(18px) saturate(90%);
        }}

        section[data-testid="stSidebar"] {{
            background: linear-gradient(180deg, rgba(18, 20, 21, .98), rgba(10, 12, 13, .98));
            border-right: 1px solid rgba(185, 163, 109, .25);
        }}

        section[data-testid="stSidebar"] [data-testid="stSidebarContent"] {{
            padding-top: 1.35rem;
        }}

        div[data-testid="stChatMessage"] {{
            color: #EEE5D2;
            background: rgba(24, 27, 29, .92);
            border: 1px solid rgba(185, 163, 109, .22);
            border-radius: 18px;
            padding: .55rem .8rem;
            margin-bottom: .7rem;
            backdrop-filter: blur(10px);
        }}

        div[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) {{
            background: rgba(39, 51, 58, .94);
            border-color: rgba(111, 150, 173, .40);
        }}

        div[data-testid="stChatInput"] {{
            color: #EEE5D2;
            background: rgba(10, 12, 13, .98);
            border: 1px solid rgba(185, 163, 109, .40);
            border-radius: 18px;
            box-shadow: 0 10px 35px rgba(0, 0, 0, .38);
        }}

        .arcane-hero {{
            display: grid;
            grid-template-columns: 112px minmax(0, 1fr) auto;
            gap: 1.25rem;
            align-items: center;
            margin: -.3rem 0 1.7rem;
            padding-bottom: 1.55rem;
            border-bottom: 1px solid rgba(185, 163, 109, .24);
        }}

        .arcane-d20 {{
            position: relative;
            display: grid;
            width: 104px;
            height: 104px;
            place-items: center;
            color: #FFF4E2;
            background: linear-gradient(145deg, rgba(217, 121, 43, .94), rgba(111, 53, 29, .95) 52%, rgba(32, 25, 20, .98));
            clip-path: polygon(50% 0, 92% 30%, 78% 92%, 22% 92%, 8% 30%);
            filter: drop-shadow(0 0 18px rgba(217, 121, 43, .38));
            font-family: Georgia, "Times New Roman", serif;
            font-size: 1.7rem;
            font-weight: 700;
        }}

        .arcane-d20::before,
        .arcane-d20::after {{
            position: absolute;
            content: "";
            inset: 8%;
            clip-path: polygon(50% 0, 100% 35%, 80% 100%, 20% 100%, 0 35%);
            border: 1px solid rgba(238, 229, 210, .55);
        }}

        .arcane-d20::after {{
            inset: 24% 18%;
            clip-path: polygon(50% 0, 100% 45%, 78% 100%, 22% 100%, 0 45%);
            border-color: rgba(185, 163, 109, .78);
        }}

        .arcane-hero h1 {{
            margin: 0;
            color: #F3EBDC;
            font-family: Georgia, "Times New Roman", serif;
            font-size: clamp(2.25rem, 5vw, 4rem);
            font-weight: 600;
            line-height: .95;
            letter-spacing: -.035em;
            text-shadow: 0 3px 28px rgba(217, 121, 43, .18);
        }}

        .arcane-hero p {{
            max-width: 660px;
            margin: .75rem 0 0;
            color: #C5BDAF;
            font-size: 1.02rem;
            line-height: 1.55;
        }}

        .arcane-sigils {{
            display: flex;
            flex-direction: column;
            justify-content: center;
            min-height: 96px;
            color: var(--arcano-lilas);
            font-size: 1.6rem;
            line-height: 1.8;
            text-shadow: 0 0 16px rgba(185, 163, 109, .40);
        }}

        .sidebar-brand {{
            display: flex;
            align-items: center;
            gap: .75rem;
            margin-bottom: 1.2rem;
            color: #EEE5D2;
            font-family: Georgia, "Times New Roman", serif;
            font-size: 1.35rem;
        }}

        .sidebar-orb {{
            display: grid;
            width: 40px;
            height: 40px;
            place-items: center;
            border: 1px solid rgba(185, 163, 109, .55);
            border-radius: 50%;
            background: radial-gradient(circle at 35% 30%, #F2C183, #A74724 52%, #211A16 75%);
            box-shadow: 0 0 20px rgba(217, 121, 43, .28);
        }}

        .status-rune {{
            display: flex;
            gap: .65rem;
            align-items: center;
            margin: .6rem 0 1rem;
            padding: .7rem .85rem;
            color: #D3C9B8;
            background: rgba(185, 163, 109, .08);
            border: 1px solid rgba(185, 163, 109, .18);
            border-radius: 12px;
            font-size: .88rem;
        }}

        .status-rune strong {{
            color: #EEE5D2;
            font-weight: 600;
        }}

        .stButton > button, .stFormSubmitButton > button {{
            border-color: rgba(185, 163, 109, .35);
            color: #1A110B;
            background: linear-gradient(120deg, #D9792B, #E89A4A);
            box-shadow: 0 7px 22px rgba(0, 0, 0, .28);
        }}

        .stButton > button:hover, .stFormSubmitButton > button:hover {{
            border-color: var(--arcano-azul);
            color: #FFF4E2;
            box-shadow: 0 0 22px rgba(217, 121, 43, .36);
        }}

        .stExpander {{
            border-color: rgba(185, 163, 109, .25) !important;
            background: rgba(18, 20, 21, .82);
        }}

        @media (max-width: 760px) {{
            .stMainBlockContainer {{
                margin-top: 3.25rem;
                padding: 1.4rem 1.1rem 6.5rem;
                border-radius: 20px;
            }}
            .arcane-hero {{
                grid-template-columns: 70px 1fr;
                gap: .85rem;
            }}
            .arcane-d20 {{
                width: 68px;
                height: 68px;
            }}
            .arcane-sigils {{
                display: none;
            }}
        }}

        @media (prefers-reduced-motion: reduce) {{
            *, *::before, *::after {{
                scroll-behavior: auto !important;
                transition: none !important;
            }}
        }}
        </style>
        """
    )


def mostrar_cabecalho():
    st.html(
        """
        <header class="arcane-hero">
          <div class="arcane-d20" role="img" aria-label="Dado de vinte lados">20</div>
          <div>
            <h1>Oráculo dos Reinos</h1>
            <p>Consulte regras, magias e aventuras nos seus livros de D&amp;D.
               Cada resposta aponta para as páginas que sustentam a informação.</p>
          </div>
          <div class="arcane-sigils" aria-hidden="true"><span>✦</span><span>✧</span><span>✦</span></div>
        </header>
        """
    )


def sincronizar(pasta, semantica):
    motor = carregar_motor(semantica)
    pasta = Path(pasta.strip().strip('"')).expanduser().resolve()
    modo = "semantico" if semantica else "textual"
    indices = RAIZ / ".leitor_pdf_rpg" / modo
    configuracao = pasta, semantica
    acervo = st.session_state.get("acervo")
    if st.session_state.get("configuracao") != configuracao:
        acervo = motor.Acervo(
            pasta, indices, configuracao=motor.AJUSTES, semantica=semantica,
        )
    relatorio = acervo.sincronizar()
    st.session_state.update(acervo=acervo, configuracao=configuracao, relatorio=relatorio)


def mostrar_mensagem(mensagem):
    avatar = "🎲" if mensagem["papel"] == "user" else "🧙"
    with st.chat_message(mensagem["papel"], avatar=avatar):
        if mensagem["papel"] == "user":
            st.text(mensagem["texto"])
            return
        st.markdown(mensagem["texto"])
        if mensagem["fontes"]:
            with st.expander(mensagem.get("titulo_trechos", "📜 Ver páginas consultadas")):
                for referencia, trecho in mensagem["fontes"]:
                    st.markdown(f"**{referencia}**")
                    st.text(trecho)


def main():
    st.set_page_config(
        page_title="Oráculo dos Reinos",
        page_icon="🎲",
        layout="wide",
        initial_sidebar_state="auto",
    )
    aplicar_identidade_visual()
    mostrar_cabecalho()

    mensagens = st.session_state.setdefault("mensagens", [])
    pasta_padrao = RAIZ / ("LivrosRPG" if (RAIZ / "LivrosRPG").is_dir() else "Livros")

    with st.sidebar:
        st.html(
            """
            <div class="sidebar-brand">
              <span class="sidebar-orb" aria-hidden="true">✦</span>
              <span>Grimório do acervo</span>
            </div>
            """
        )
        with st.form("carregar_acervo"):
            pasta = st.text_input(
                "📚 Pasta dos livros",
                value=str(pasta_padrao),
                help="A pasta pode conter PDFs em subpastas.",
            )
            semantica = st.toggle(
                "✨ Busca semântica",
                help="Encontra conceitos semelhantes mesmo quando os termos são diferentes.",
            )
            carregar = st.form_submit_button(
                "Sincronizar grimório", type="primary", icon=":material/sync:", width="stretch",
            )

        if carregar:
            if not pasta.strip():
                st.warning("Informe o caminho da pasta de livros.")
            else:
                try:
                    with st.spinner("Lendo os tomos do acervo…"):
                        sincronizar(pasta, semantica)
                except ImportError:
                    st.error("Instale sentence-transformers para ativar a busca semântica.")
                except (OSError, ValueError, KeyError) as erro:
                    st.error(f"Não foi possível carregar o acervo. {erro}")

        acervo = st.session_state.get("acervo")
        if acervo is not None:
            pasta_ativa, semantica_ativa = st.session_state.configuracao
            relatorio = st.session_state.relatorio
            st.html(
                f"""
                <div class="status-rune">
                  <span aria-hidden="true">◈</span>
                  <span><strong>{len(acervo.livros)} livro(s)</strong><br>
                  {len(relatorio['indexados'])} novo(s) · {len(relatorio['reutilizados'])} reutilizado(s)</span>
                </div>
                """
            )
            if relatorio["falhas"]:
                with st.expander(f"⚠️ Falhas de leitura ({len(relatorio['falhas'])})"):
                    for livro, falha in relatorio["falhas"].items():
                        st.text(f"{livro} · {falha}")

        st.subheader("🔮 Foco da consulta", divider="violet")
        edicao = st.selectbox(
            "Edição",
            [None, "2014", "2024"],
            format_func=lambda valor: valor or "Todas as edições",
        )
        livros = {
            livro.id: livro for livro in (acervo.livros if acervo else ())
            if edicao is None or livro.edicao == edicao
        }
        selecionados = st.multiselect(
            "Livros",
            list(livros),
            format_func=lambda id_: f"{livros[id_].titulo} · {id_}",
            placeholder="Todo o acervo selecionado",
        )
        chave = os.getenv("GOOGLE_API_KEY", "").strip()
        if not chave:
            chave = st.text_input(
                "🪄 Chave do Gemini",
                type="password",
                autocomplete="off",
                help="A chave fica apenas nesta sessão do navegador.",
            ).strip()
        st.caption("✨ Respostas com fontes" if chave else "📖 Busca direta nas páginas")
        if st.button(
            "Limpar conversa", icon=":material/delete_sweep:", width="stretch",
            disabled=not mensagens,
        ):
            mensagens.clear()

    if not acervo:
        st.info("Escolha a pasta dos PDFs e sincronize o grimório para começar.", icon="📚")
    elif not livros:
        st.info("Nenhum livro disponível nesta edição. Altere o filtro ou sincronize outro acervo.")
    elif not mensagens:
        st.info(
            "Pergunte sobre uma magia, uma regra ou compare as edições de 2014 e 2024.",
            icon="✨",
        )

    for mensagem in mensagens:
        mostrar_mensagem(mensagem)

    with st.bottom:
        consulta = st.chat_input(
            "Pergunte ao oráculo sobre os livros…",
            disabled=not livros,
            max_chars=1200,
            submit_mode="disable",
        )
    if not consulta or not consulta.strip():
        return

    consulta = consulta.strip()
    escopo = (str(pasta_ativa), semantica_ativa, edicao, tuple(sorted(selecionados)))
    anterior = [
        m["pergunta"] for m in mensagens
        if m.get("escopo") == escopo and m.get("respondida")
    ]
    pergunta = {"papel": "user", "texto": consulta}
    mensagens.append(pergunta)
    mostrar_mensagem(pergunta)
    resposta = {
        "papel": "assistant",
        "fontes": [],
        "escopo": escopo,
        "pergunta": consulta,
        "respondida": False,
    }

    try:
        with st.spinner("Consultando os tomos…"):
            motor = carregar_motor(semantica_ativa)
            filtros = {"livros": selecionados or None, "edicao": edicao}
            if chave:
                modelo = os.getenv("GEMINI_MODEL") or motor.MODELO_GEMINI
                with genai.Client(api_key=chave) as cliente:
                    resultado = motor.Assistente(acervo, modelo, lambda: cliente).perguntar(
                        consulta, historico=anterior[-3:], **filtros,
                    )
                resposta["texto"] = resultado.texto
                resposta["respondida"] = bool(resultado.fontes)
                paginas = resultado.fontes
                if resultado.paginas_relacionadas:
                    referencias = ", ".join(
                        pagina.referencia for pagina in resultado.paginas_relacionadas[:3]
                    )
                    resposta["texto"] += f"\n\nPáginas localizadas: {referencias}."
            else:
                pesquisa = motor.Pesquisa(acervo, consulta, **filtros)
                contagem = motor.responder_contagem_paginas(pesquisa)
                if contagem is not None:
                    paginas = []
                    resposta["texto"] = contagem.texto
                else:
                    paginas, _ = pesquisa.inicial(6)
                    resposta["texto"] = (
                        f"Encontrei {len(paginas)} página(s). "
                        "Abra as páginas consultadas para ler os trechos."
                        if paginas else "Não encontrei páginas relevantes para essa busca."
                    )
            palavras, _ = motor.consulta_lexical(consulta)
            resposta["fontes"] = [
                (p.referencia, motor.limitar_pagina(p.texto, palavras, limite=900))
                for p in paginas
            ]
    except genai.errors.APIError as erro:
        resposta["texto"] = (
            f"O Gemini retornou o erro {erro.code}. Confira a chave, o modelo e a cota da API."
        )
    except (OSError, RuntimeError, ValueError):
        resposta["texto"] = (
            "A consulta falhou. Confira a conexão ou sincronize o acervo e tente novamente."
        )

    mensagens.append(resposta)
    mostrar_mensagem(resposta)


if __name__ == "__main__":
    main()
