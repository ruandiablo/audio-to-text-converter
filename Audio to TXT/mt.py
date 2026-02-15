import os
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

import re
import glob
import time
import socket
import threading
import traceback
import warnings
import webbrowser
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext, ttk

# ══════════════════════════════════════════════════════════════
#  TIMEOUT GLOBAL — resolve travamento no download de modelos
#  grandes (medium/large). Padrão do Python é muito baixo.
# ══════════════════════════════════════════════════════════════
socket.setdefaulttimeout(600)

warnings.filterwarnings("ignore", category=UserWarning)

try:
    import torch
    USA_GPU = torch.cuda.is_available()
except Exception:
    USA_GPU = False


class TranscritorApp:

    # ==================== DRACULA PALETTE ====================
    BG          = "#282a36"
    BG_DARKER   = "#21222c"
    BG_LIGHTER  = "#343746"
    CURRENT     = "#44475a"
    SELECTION   = "#44475a"
    FOREGROUND  = "#f8f8f2"
    COMMENT     = "#6272a4"
    CYAN        = "#8be9fd"
    GREEN       = "#50fa7b"
    ORANGE      = "#ffb86c"
    PINK        = "#ff79c6"
    PURPLE      = "#bd93f9"
    RED         = "#ff5555"
    YELLOW      = "#f1fa8c"

    # ==================== WHISPER LANGS ====================
    WHISPER_LANGS = [
        {"code": "pt",  "pt": "Português",    "en": "Portuguese"},
        {"code": "en",  "pt": "Inglês",       "en": "English"},
        {"code": "es",  "pt": "Espanhol",     "en": "Spanish"},
        {"code": "fr",  "pt": "Francês",      "en": "French"},
        {"code": "it",  "pt": "Italiano",     "en": "Italian"},
        {"code": "de",  "pt": "Alemão",       "en": "German"},
        {"code": "ja",  "pt": "Japonês",      "en": "Japanese"},
        {"code": "ko",  "pt": "Coreano",      "en": "Korean"},
        {"code": "zh",  "pt": "Chinês",       "en": "Chinese"},
        {"code": "ru",  "pt": "Russo",        "en": "Russian"},
        {"code": None,  "pt": "Auto-detectar","en": "Auto-detect"},
    ]

    # ==================== MODELOS ====================
    MODELOS = [
        {"key": "tiny",   "nome": "TINY",   "tam": "~75 MB",
         "qual": 1, "cor": "#50fa7b"},
        {"key": "base",   "nome": "BASE",   "tam": "~140 MB",
         "qual": 2, "cor": "#8be9fd"},
        {"key": "small",  "nome": "SMALL",  "tam": "~460 MB",
         "qual": 3, "cor": "#f1fa8c"},
        {"key": "medium", "nome": "MEDIUM", "tam": "~1.5 GB",
         "qual": 4, "cor": "#ffb86c"},
        {"key": "large",  "nome": "LARGE",  "tam": "~2.9 GB",
         "qual": 5, "cor": "#ff5555"},
    ]

    TAMANHO_MINIMO_MODELO = {
        "tiny":    70_000_000,
        "base":   130_000_000,
        "small":  440_000_000,
        "medium": 1_400_000_000,
        "large":  2_800_000_000,
    }

    # ==================== LINKS ====================
    LINKS = [
        {"texto": "YouTube",   "url": "https://youtube.com",
         "cor": "#ff5555",  "icone": "▶"},
        {"texto": "YT → MP3",
         "url": "https://y2meta.is/pt89/youtube-to-mp3/",
         "cor": "#50fa7b",  "icone": "♫"},
        {"texto": "Instagram",
         "url": "https://www.instagram.com/ruanalmeidar",
         "cor": "#ff79c6",  "icone": "◈"},
        {"texto": "GitHub",
         "url": "https://github.com/ruandiablo/",
         "cor": "#bd93f9",  "icone": "⬡"},
    ]

    # ==================== TRADUÇÕES ====================
    TEXTOS = {
        "pt": {
            "window_title":         "Audio to Text — Ruan Almeida",
            "header_title":         "Transcrição de Áudio para Texto",
            "header_sub":           "Ruan Almeida  ·  2025  ·  @ruanalmeidar",
            "links_label":          "Links:",
            "drop_title":           "Clique aqui para selecionar o áudio",
            "drop_formats":
                "MP3 · WAV · M4A · OGG · FLAC · AAC · WMA · MP4",
            "drop_hint":            "Ctrl+O para abrir",
            "drop_change":          "Clique para alterar",
            "drop_files":           "{n} arquivo(s) selecionado(s)",
            "lbl_idioma":           "Idioma:",
            "chk_quebra":           "Quebrar linhas (.?!)",
            "chk_timestamps":       "Timestamps",
            "font_label":           "Fonte:",
            "instrucao":
                "Selecione o modelo para iniciar a transcrição",
            "btn_copiar":           "Copiar",
            "btn_salvar_txt":       "Salvar TXT",
            "btn_salvar_srt":       "Salvar SRT",
            "btn_limpar":           "Limpar",
            "status_pronto":
                "Pronto — selecione um áudio e clique no modelo",
            "status_pronto_curto":  "Pronto.",
            "status_copiado":       "Texto copiado!",
            "status_nada_copiar":   "Nada para copiar.",
            "status_txt_salvo":     "TXT salvo: {cam}",
            "status_srt_salvo":     "SRT salvo: {cam}",
            "status_erro":          "Erro na transcrição.",
            "status_carregando":
                "Baixando modelo {modelo}… (pode levar alguns minutos)",
            "status_carregando_n":
                "Baixando modelo {modelo}… tentativa {t}/{max}",
            "status_carregado":     "Modelo {modelo} carregado!",
            "status_transcrevendo":
                "[{modelo}]  Transcrevendo ({i}/{n}):  {arq}",
            "status_concluido":
                "Concluído!  {modelo}  ·  {palavras} palavras"
                "  ·  {tempo}",
            "status_arquivos":
                "{n} arquivo(s) selecionado(s)",
            "status_retry":
                "Download falhou. Limpando cache, "
                "tentando novamente em {seg}s…",
            "status_cache_limpo":
                "Cache parcial removido. Rebaixando {modelo}…",
            "toast_copiado":
                "Copiado para a área de transferência!",
            "toast_nada_copiar":    "Nada para copiar",
            "toast_limpo":          "Tudo limpo",
            "toast_txt_salvo":      "Arquivo TXT salvo!",
            "toast_srt_salvo":      "Arquivo SRT salvo!",
            "toast_erro":           "Erro na transcrição!",
            "toast_concluido":
                "Transcrição concluída — {palavras} palavras"
                " em {tempo}",
            "toast_arquivos":       "{n} arquivo(s) carregado(s)",
            "msg_aguarde_titulo":   "Aguarde",
            "msg_aguarde":          "Transcrição em andamento.",
            "msg_aviso":            "Aviso",
            "msg_selecione":        "Selecione um áudio primeiro.",
            "msg_sem_texto":        "Sem texto para salvar.",
            "msg_sem_seg":
                "Sem segmentos para gerar legendas.\n"
                "Transcreva um áudio primeiro.",
            "msg_whisper":
                "Biblioteca 'whisper' não encontrada!\n\n"
                "Instale com:\n"
                "   pip install openai-whisper\n\n"
                "E instale o FFmpeg.",
            "msg_download_falhou":
                "Não foi possível baixar o modelo {modelo}"
                " após {max} tentativas.\n\n"
                "Verifique sua conexão.\n\nErro: {erro}",
            "dlg_abrir":            "Selecione os áudios",
            "dlg_salvar_txt":       "Salvar TXT",
            "dlg_salvar_srt":       "Salvar SRT",
            "dlg_tipo_audio":       "Áudio",
            "dlg_tipo_todos":       "Todos",
            "dlg_tipo_texto":       "Texto",
            "dlg_tipo_srt":         "Legenda SRT",
            "footer":
                "Transcrição Áudio → Texto  |  Ruan Almeida"
                "  |  2025  |  @ruanalmeidar  |"
                "  Ctrl+O abrir · Ctrl+S salvar",
            "info_template":
                "{palavras} palavras · {chars} chars · "
                "{segs} seg · {modelo} · Idioma: {idioma}"
                " · {tempo}",
            "idioma_detectado":
                "Idioma detectado: {idioma}",
            "modelo_desc": {
                "tiny": "Ultra rápido",
                "base": "Rápido",
                "small": "Equilibrado",
                "medium": "Alta qualidade",
                "large": "Máxima precisão",
            },
        },
        "en": {
            "window_title":
                "Audio to Text — Ruan Almeida",
            "header_title":
                "Audio to Text Transcription",
            "header_sub":
                "Ruan Almeida  ·  2025  ·  @ruanalmeidar",
            "links_label":          "Links:",
            "drop_title":
                "Click here to select audio",
            "drop_formats":
                "MP3 · WAV · M4A · OGG · FLAC · AAC · WMA · MP4",
            "drop_hint":            "Ctrl+O to open",
            "drop_change":          "Click to change",
            "drop_files":           "{n} file(s) selected",
            "lbl_idioma":           "Language:",
            "chk_quebra":           "Line breaks (.?!)",
            "chk_timestamps":       "Timestamps",
            "font_label":           "Font:",
            "instrucao":
                "Select a model to start transcription",
            "btn_copiar":           "Copy",
            "btn_salvar_txt":       "Save TXT",
            "btn_salvar_srt":       "Save SRT",
            "btn_limpar":           "Clear",
            "status_pronto":
                "Ready — select an audio and click a model",
            "status_pronto_curto":  "Ready.",
            "status_copiado":       "Text copied!",
            "status_nada_copiar":   "Nothing to copy.",
            "status_txt_salvo":     "TXT saved: {cam}",
            "status_srt_salvo":     "SRT saved: {cam}",
            "status_erro":          "Transcription error.",
            "status_carregando":
                "Downloading model {modelo}…"
                " (may take a few minutes)",
            "status_carregando_n":
                "Downloading model {modelo}…"
                " attempt {t}/{max}",
            "status_carregado":
                "Model {modelo} loaded!",
            "status_transcrevendo":
                "[{modelo}]  Transcribing ({i}/{n}):  {arq}",
            "status_concluido":
                "Done!  {modelo}  ·  {palavras} words"
                "  ·  {tempo}",
            "status_arquivos":
                "{n} file(s) selected",
            "status_retry":
                "Download failed. Clearing cache,"
                " retrying in {seg}s…",
            "status_cache_limpo":
                "Partial cache removed."
                " Re-downloading {modelo}…",
            "toast_copiado":
                "Copied to clipboard!",
            "toast_nada_copiar":    "Nothing to copy",
            "toast_limpo":          "All cleared",
            "toast_txt_salvo":      "TXT file saved!",
            "toast_srt_salvo":      "SRT file saved!",
            "toast_erro":           "Transcription error!",
            "toast_concluido":
                "Transcription complete — {palavras} words"
                " in {tempo}",
            "toast_arquivos":       "{n} file(s) loaded",
            "msg_aguarde_titulo":   "Wait",
            "msg_aguarde":
                "Transcription in progress.",
            "msg_aviso":            "Warning",
            "msg_selecione":
                "Select an audio first.",
            "msg_sem_texto":        "No text to save.",
            "msg_sem_seg":
                "No segments to generate subtitles.\n"
                "Transcribe an audio first.",
            "msg_whisper":
                "Library 'whisper' not found!\n\n"
                "Install with:\n"
                "   pip install openai-whisper\n\n"
                "And install FFmpeg.",
            "msg_download_falhou":
                "Could not download model {modelo}"
                " after {max} attempts.\n\n"
                "Check your connection.\n\nError: {erro}",
            "dlg_abrir":            "Select audio files",
            "dlg_salvar_txt":       "Save TXT",
            "dlg_salvar_srt":       "Save SRT",
            "dlg_tipo_audio":       "Audio",
            "dlg_tipo_todos":       "All",
            "dlg_tipo_texto":       "Text",
            "dlg_tipo_srt":         "SRT Subtitle",
            "footer":
                "Audio → Text Transcription  |  Ruan Almeida"
                "  |  2025  |  @ruanalmeidar  |"
                "  Ctrl+O open · Ctrl+S save",
            "info_template":
                "{palavras} words · {chars} chars · "
                "{segs} seg · {modelo} · Language: {idioma}"
                " · {tempo}",
            "idioma_detectado":
                "Detected language: {idioma}",
            "modelo_desc": {
                "tiny": "Ultra fast",
                "base": "Fast",
                "small": "Balanced",
                "medium": "High quality",
                "large": "Max accuracy",
            },
        },
    }

    MAX_TENTATIVAS_DOWNLOAD = 3
    PAUSA_ENTRE_TENTATIVAS  = [10, 20, 30]

    # ────────────────────────────────────────────────
    def __init__(self, root):
        self.root = root
        self.ui_lang = "pt"

        self.root.title(self._t("window_title"))
        self.root.geometry("1000x860")
        self.root.configure(bg=self.BG)
        self.root.resizable(True, True)
        self.root.minsize(840, 720)

        self.arquivos              = []
        self.modelo_carregado      = None
        self.nome_modelo_carregado = None
        self.transcrevendo         = False
        self.btns_modelos          = {}
        self.segmentos_resultado   = []
        self.font_size             = 11
        self.timer_rodando         = False
        self.tempo_inicio          = None
        self._drop_hover           = False
        self._toast_id             = None

        self._aplicar_estilo_ttk()
        self._criar_widgets()

        self.root.bind("<Control-o>",
                       lambda e: self._selecionar_arquivos())
        self.root.bind("<Control-O>",
                       lambda e: self._selecionar_arquivos())
        self.root.bind("<Control-s>",
                       lambda e: self._salvar_txt())
        self.root.bind("<Control-S>",
                       lambda e: self._salvar_txt())

    # ======================== TTK ========================
    def _aplicar_estilo_ttk(self):
        s = ttk.Style()
        s.theme_use("clam")
        s.configure("Dracula.Horizontal.TProgressbar",
                     troughcolor=self.BG_DARKER,
                     background=self.PURPLE,
                     bordercolor=self.BG_DARKER,
                     lightcolor=self.PURPLE,
                     darkcolor=self.PINK,
                     thickness=5)

    # ======================== HELPERS ====================
    def _t(self, key):
        return self.TEXTOS[self.ui_lang].get(key, f"[{key}]")

    def _get_whisper_code(self):
        name = self.var_idioma.get()
        for lang in self.WHISPER_LANGS:
            if lang[self.ui_lang] == name:
                return lang["code"]
        return "pt"

    # ======================== WIDGETS ====================
    def _criar_widgets(self):

        # ──────────── HEADER ────────────
        header = tk.Frame(self.root, bg=self.BG_DARKER)
        header.pack(fill="x")

        header_inner = tk.Frame(header, bg=self.BG_DARKER)
        header_inner.pack(pady=(18, 14))

        self.lbl_title = tk.Label(header_inner,
            text=self._t("header_title"),
            font=("Segoe UI", 20, "bold"),
            bg=self.BG_DARKER, fg=self.PURPLE)
        self.lbl_title.pack()

        self.lbl_sub = tk.Label(header_inner,
            text=self._t("header_sub"),
            font=("Segoe UI", 9),
            bg=self.BG_DARKER, fg=self.COMMENT)
        self.lbl_sub.pack(pady=(4, 0))

        tk.Frame(self.root, bg=self.CURRENT,
                 height=1).pack(fill="x")

        # ──────────── BARRA: LINKS + BANDEIRAS ──────────
        bar = tk.Frame(self.root, bg=self.BG)
        bar.pack(fill="x")

        bar_inner = tk.Frame(bar, bg=self.BG)
        bar_inner.pack(fill="x", padx=28, pady=8)

        links_frame = tk.Frame(bar_inner, bg=self.BG)
        links_frame.pack(side="left")

        self.lbl_links = tk.Label(links_frame,
            text=self._t("links_label"),
            font=("Segoe UI", 9), bg=self.BG,
            fg=self.COMMENT)
        self.lbl_links.pack(side="left", padx=(0, 8))

        for lk in self.LINKS:
            b = tk.Button(links_frame,
                text=f" {lk['icone']}  {lk['texto']} ",
                font=("Segoe UI", 9),
                bg=self.CURRENT, fg=lk["cor"],
                activebackground=self.BG_LIGHTER,
                activeforeground=lk["cor"],
                relief="flat", bd=0, cursor="hand2",
                pady=3, padx=6,
                command=lambda u=lk["url"]: webbrowser.open(u))
            b.pack(side="left", padx=3)
            self._hover_btn(b, self.CURRENT, self.BG_LIGHTER)

        flags_frame = tk.Frame(bar_inner, bg=self.BG)
        flags_frame.pack(side="right")
        self._criar_bandeiras(flags_frame)

        tk.Frame(self.root, bg=self.CURRENT,
                 height=1).pack(fill="x")

        # ──────────── CORPO ────────────
        corpo = tk.Frame(self.root, bg=self.BG)
        corpo.pack(fill="both", expand=True, padx=28, pady=16)

        # ── DROP ZONE ──
        self.drop_frame = tk.Frame(corpo, bg=self.CURRENT, bd=0)
        self.drop_frame.pack(fill="x", pady=(0, 14))

        self.drop_canvas = tk.Canvas(
            self.drop_frame, height=90,
            highlightthickness=0,
            bg=self.BG_DARKER, cursor="hand2")
        self.drop_canvas.pack(fill="both", expand=True,
                              padx=1, pady=1)
        self.drop_canvas.bind("<Configure>",
                              self._desenhar_drop)
        self.drop_canvas.bind(
            "<Button-1>",
            lambda e: self._selecionar_arquivos())
        self.drop_canvas.bind("<Enter>", self._drop_enter)
        self.drop_canvas.bind("<Leave>", self._drop_leave)

        # ── OPÇÕES ──
        fo = tk.Frame(corpo, bg=self.BG)
        fo.pack(fill="x", pady=(0, 12))

        self.lbl_idioma_text = tk.Label(fo,
            text=self._t("lbl_idioma"),
            font=("Segoe UI", 10, "bold"),
            bg=self.BG, fg=self.FOREGROUND)
        self.lbl_idioma_text.pack(side="left")

        self.var_idioma = tk.StringVar(
            value=self.WHISPER_LANGS[0][self.ui_lang])
        self._criar_menu_idioma(fo)

        self._sep_v(fo)

        self.var_quebra_linha = tk.BooleanVar(value=True)
        self.cb_quebra = tk.Checkbutton(fo,
            text=self._t("chk_quebra"),
            variable=self.var_quebra_linha,
            font=("Segoe UI", 10), bg=self.BG,
            fg=self.FOREGROUND,
            selectcolor=self.BG_DARKER,
            activebackground=self.BG,
            activeforeground=self.FOREGROUND,
            bd=0, highlightthickness=0, cursor="hand2")
        self.cb_quebra.pack(side="left", padx=(0, 12))

        self.var_timestamps = tk.BooleanVar(value=False)
        self.cb_timestamps = tk.Checkbutton(fo,
            text=self._t("chk_timestamps"),
            variable=self.var_timestamps,
            font=("Segoe UI", 10), bg=self.BG,
            fg=self.FOREGROUND,
            selectcolor=self.BG_DARKER,
            activebackground=self.BG,
            activeforeground=self.FOREGROUND,
            bd=0, highlightthickness=0, cursor="hand2")
        self.cb_timestamps.pack(side="left", padx=(0, 12))

        self._sep_v(fo)

        dev = "GPU (CUDA)" if USA_GPU else "CPU"
        dc  = self.GREEN if USA_GPU else self.ORANGE
        tk.Label(fo, text=dev,
                 font=("Segoe UI", 9, "bold"),
                 bg=self.BG, fg=dc).pack(side="left")

        rf = tk.Frame(fo, bg=self.BG)
        rf.pack(side="right")
        self.lbl_fonte = tk.Label(rf,
            text=self._t("font_label"),
            font=("Segoe UI", 9), bg=self.BG,
            fg=self.COMMENT)
        self.lbl_fonte.pack(side="left", padx=(0, 4))

        for txt, cmd in [(" A+ ", self._font_mais),
                         (" A- ", self._font_menos)]:
            b = tk.Button(rf, text=txt,
                font=("Segoe UI", 9, "bold"),
                bg=self.CURRENT, fg=self.FOREGROUND,
                relief="flat", bd=0, cursor="hand2",
                activebackground=self.BG_LIGHTER,
                activeforeground=self.FOREGROUND,
                command=cmd)
            b.pack(side="left", padx=2)
            self._hover_btn(b, self.CURRENT, self.BG_LIGHTER)

        # ── INSTRUÇÃO ──
        self.lbl_instrucao = tk.Label(corpo,
            text=self._t("instrucao"),
            font=("Segoe UI", 9), bg=self.BG,
            fg=self.COMMENT)
        self.lbl_instrucao.pack(fill="x", pady=(0, 8))

        # ── 5 CARDS MODELO ──
        fm = tk.Frame(corpo, bg=self.BG)
        fm.pack(fill="x", pady=(0, 12))

        descs = self._t("modelo_desc")
        for i, m in enumerate(self.MODELOS):
            estrelas = ("★" * m["qual"]
                        + "☆" * (5 - m["qual"]))

            outer = tk.Frame(fm, bg=self.CURRENT, bd=0)
            outer.pack(side="left", fill="both",
                       expand=True,
                       padx=(0 if i == 0 else 4, 0))

            inner = tk.Frame(outer, bg=self.BG_DARKER, bd=0)
            inner.pack(fill="both", expand=True,
                       padx=1, pady=1)

            tk.Frame(inner, bg=m["cor"],
                     height=2).pack(fill="x")

            btn = tk.Button(inner,
                text=(f"{m['nome']}\n{m['tam']}\n"
                      f"{estrelas}\n{descs[m['key']]}"),
                font=("Segoe UI", 9, "bold"),
                bg=self.BG_DARKER, fg=m["cor"],
                activebackground=self.BG_LIGHTER,
                activeforeground=m["cor"],
                cursor="hand2", relief="flat",
                bd=0, pady=10,
                command=lambda k=m["key"]:
                    self._clique_modelo(k))
            btn.pack(fill="both", expand=True)

            self.btns_modelos[m["key"]] = {
                "btn": btn, "cor": m["cor"],
                "outer": outer}

            cor_m = m["cor"]
            def _me(e, b=btn, c=cor_m, o=outer):
                if str(b.cget("state")) != "disabled":
                    b.config(bg=self.BG_LIGHTER)
                    o.config(bg=c)
            def _ml(e, b=btn, o=outer):
                if str(b.cget("state")) != "disabled":
                    b.config(bg=self.BG_DARKER)
                    o.config(bg=self.CURRENT)
            btn.bind("<Enter>", _me)
            btn.bind("<Leave>", _ml)

        # ── PROGRESSO + TIMER ──
        fp = tk.Frame(corpo, bg=self.BG)
        fp.pack(fill="x", pady=(0, 4))

        self.progress = ttk.Progressbar(fp,
            style="Dracula.Horizontal.TProgressbar",
            mode="indeterminate")
        self.progress.pack(side="left", fill="x",
                           expand=True, padx=(0, 12))

        self.label_timer = tk.Label(fp, text="00:00",
            font=("Consolas", 11, "bold"),
            bg=self.BG, fg=self.COMMENT)
        self.label_timer.pack(side="right")

        # ── STATUS ──
        self.label_status = tk.Label(corpo,
            text=self._t("status_pronto"),
            font=("Segoe UI", 10), bg=self.BG,
            fg=self.GREEN, anchor="w")
        self.label_status.pack(fill="x", pady=(0, 8))

        # ── AÇÕES ──
        fa = tk.Frame(corpo, bg=self.BG)
        fa.pack(fill="x", pady=(0, 8))

        self.btn_copiar = self._action_btn(
            fa, self._t("btn_copiar"),
            self._copiar_texto, self.CYAN, 0)
        self.btn_salvar_txt = self._action_btn(
            fa, self._t("btn_salvar_txt"),
            self._salvar_txt, self.GREEN, 6)
        self.btn_salvar_srt = self._action_btn(
            fa, self._t("btn_salvar_srt"),
            self._salvar_srt, self.ORANGE, 6)
        self.btn_limpar = self._action_btn(
            fa, self._t("btn_limpar"),
            self._limpar_tudo, self.RED, 6)

        self.label_info = tk.Label(fa, text="",
            font=("Segoe UI", 8), bg=self.BG,
            fg=self.COMMENT, anchor="e")
        self.label_info.pack(side="right", fill="x",
                             expand=True)

        # ── AREA DE TEXTO ──
        self.text_border = tk.Frame(corpo,
                                    bg=self.CURRENT, bd=0)
        self.text_border.pack(fill="both", expand=True)

        text_inner = tk.Frame(self.text_border,
                              bg=self.BG_DARKER, bd=0)
        text_inner.pack(fill="both", expand=True,
                        padx=1, pady=1)

        self.texto_resultado = scrolledtext.ScrolledText(
            text_inner, wrap="word",
            font=("Consolas", self.font_size),
            bg=self.BG_DARKER, fg=self.FOREGROUND,
            insertbackground=self.PURPLE,
            selectbackground=self.SELECTION,
            selectforeground=self.FOREGROUND,
            relief="flat", padx=14, pady=12, bd=0)
        self.texto_resultado.pack(fill="both", expand=True)

        # ──────────── FOOTER ────────────
        tk.Frame(self.root, bg=self.CURRENT,
                 height=1).pack(fill="x", side="bottom")

        footer = tk.Frame(self.root, bg=self.BG_DARKER,
                          height=30)
        footer.pack(fill="x", side="bottom")
        footer.pack_propagate(False)

        self.lbl_footer = tk.Label(footer,
            text=self._t("footer"),
            font=("Segoe UI", 8), bg=self.BG_DARKER,
            fg=self.COMMENT)
        self.lbl_footer.pack(expand=True)

        # ── TOAST ──
        self.toast_label = tk.Label(self.root, text="",
            font=("Segoe UI", 10, "bold"),
            bg=self.CURRENT, fg=self.GREEN,
            padx=18, pady=5, bd=0, relief="flat")

    # ======================== BANDEIRAS ==================
    def _criar_bandeiras(self, parent):
        self.flag_br_frame = tk.Frame(
            parent, bg=self.PURPLE, cursor="hand2")
        self.flag_br_frame.pack(side="left", padx=(0, 5))

        self.flag_br = tk.Canvas(self.flag_br_frame,
            width=38, height=26, highlightthickness=0,
            cursor="hand2")
        self.flag_br.pack(padx=2, pady=2)
        self._draw_flag_br()

        self.flag_br.bind("<Button-1>",
            lambda e: self._trocar_idioma_ui("pt"))
        self.flag_br_frame.bind("<Button-1>",
            lambda e: self._trocar_idioma_ui("pt"))
        self.flag_br.bind("<Enter>",
            lambda e: self.flag_br_frame.config(
                bg=self.PURPLE
                if self.ui_lang == "pt"
                else self.COMMENT))
        self.flag_br.bind("<Leave>",
            lambda e: self.flag_br_frame.config(
                bg=self.PURPLE
                if self.ui_lang == "pt"
                else self.CURRENT))

        self.flag_us_frame = tk.Frame(
            parent, bg=self.CURRENT, cursor="hand2")
        self.flag_us_frame.pack(side="left")

        self.flag_us = tk.Canvas(self.flag_us_frame,
            width=38, height=26, highlightthickness=0,
            cursor="hand2")
        self.flag_us.pack(padx=2, pady=2)
        self._draw_flag_us()

        self.flag_us.bind("<Button-1>",
            lambda e: self._trocar_idioma_ui("en"))
        self.flag_us_frame.bind("<Button-1>",
            lambda e: self._trocar_idioma_ui("en"))
        self.flag_us.bind("<Enter>",
            lambda e: self.flag_us_frame.config(
                bg=self.PURPLE
                if self.ui_lang == "en"
                else self.COMMENT))
        self.flag_us.bind("<Leave>",
            lambda e: self.flag_us_frame.config(
                bg=self.PURPLE
                if self.ui_lang == "en"
                else self.CURRENT))

    def _draw_flag_br(self):
        c = self.flag_br; c.delete("all")
        c.create_rectangle(0, 0, 38, 26,
                           fill="#009c3b", outline="")
        c.create_polygon(19, 2, 36, 13, 19, 24, 2, 13,
                         fill="#ffdf00", outline="")
        c.create_oval(11, 7, 27, 20,
                      fill="#002776", outline="")
        c.create_arc(7, 8, 31, 26, start=20, extent=140,
                     style="arc", outline="#fff", width=1)

    def _draw_flag_us(self):
        c = self.flag_us; c.delete("all")
        for i in range(13):
            cor = "#B22234" if i % 2 == 0 else "#FFFFFF"
            y1 = round(i * 26 / 13)
            y2 = round((i + 1) * 26 / 13)
            c.create_rectangle(0, y1, 38, y2,
                               fill=cor, outline="")
        c.create_rectangle(0, 0, 16, 14,
                           fill="#3C3B6E", outline="")
        for row, cols in enumerate(
                [(3, 8, 13), (5, 11), (3, 8, 13)]):
            for cx in cols:
                cy = 3 + row * 4
                c.create_text(cx, cy, text="·",
                    fill="white",
                    font=("Segoe UI", 5, "bold"))

    # ======================== TROCA IDIOMA ===============
    def _trocar_idioma_ui(self, new_lang):
        if new_lang == self.ui_lang:
            return
        old_name = self.var_idioma.get()
        selected_code = "pt"
        for lang in self.WHISPER_LANGS:
            if lang[self.ui_lang] == old_name:
                selected_code = lang["code"]
                break
        self.ui_lang = new_lang
        for lang in self.WHISPER_LANGS:
            if lang["code"] == selected_code:
                self.var_idioma.set(lang[new_lang])
                break
        if new_lang == "pt":
            self.flag_br_frame.config(bg=self.PURPLE)
            self.flag_us_frame.config(bg=self.CURRENT)
        else:
            self.flag_br_frame.config(bg=self.CURRENT)
            self.flag_us_frame.config(bg=self.PURPLE)
        self._atualizar_textos()

    def _atualizar_textos(self):
        t = self._t
        self.root.title(t("window_title"))
        self.lbl_title.config(text=t("header_title"))
        self.lbl_sub.config(text=t("header_sub"))
        self.lbl_links.config(text=t("links_label"))
        self._desenhar_drop()
        self.lbl_idioma_text.config(text=t("lbl_idioma"))
        self.cb_quebra.config(text=t("chk_quebra"))
        self.cb_timestamps.config(text=t("chk_timestamps"))
        self.lbl_fonte.config(text=t("font_label"))
        self.lbl_instrucao.config(text=t("instrucao"))
        descs = t("modelo_desc")
        for m in self.MODELOS:
            k = m["key"]
            estrelas = ("★" * m["qual"]
                        + "☆" * (5 - m["qual"]))
            self.btns_modelos[k]["btn"].config(
                text=(f"{m['nome']}\n{m['tam']}\n"
                      f"{estrelas}\n{descs[k]}"))
        self.btn_copiar.config(
            text=f"  {t('btn_copiar')}  ")
        self.btn_salvar_txt.config(
            text=f"  {t('btn_salvar_txt')}  ")
        self.btn_salvar_srt.config(
            text=f"  {t('btn_salvar_srt')}  ")
        self.btn_limpar.config(
            text=f"  {t('btn_limpar')}  ")
        if not self.transcrevendo:
            self.label_status.config(
                text=t("status_pronto"))
        self.lbl_footer.config(text=t("footer"))
        self._rebuild_menu_idioma()

    # ======================== MENU IDIOMA ================
    def _criar_menu_idioma(self, parent):
        nomes = [l[self.ui_lang]
                 for l in self.WHISPER_LANGS]
        self.menu_idioma = tk.OptionMenu(
            parent, self.var_idioma, *nomes)
        self.menu_idioma.config(
            bg=self.CURRENT, fg=self.CYAN,
            font=("Segoe UI", 10, "bold"),
            relief="flat", highlightthickness=0, bd=0,
            padx=10, pady=2,
            activebackground=self.BG_LIGHTER,
            activeforeground=self.CYAN)
        self.menu_idioma["menu"].config(
            bg=self.BG_DARKER, fg=self.FOREGROUND,
            font=("Segoe UI", 10),
            activebackground=self.PURPLE,
            activeforeground=self.FOREGROUND, bd=0)
        self.menu_idioma.pack(side="left", padx=(6, 14))

    def _rebuild_menu_idioma(self):
        menu = self.menu_idioma["menu"]
        menu.delete(0, "end")
        for info in self.WHISPER_LANGS:
            name = info[self.ui_lang]
            menu.add_command(label=name,
                command=lambda v=name:
                    self.var_idioma.set(v))
        menu.config(
            bg=self.BG_DARKER, fg=self.FOREGROUND,
            font=("Segoe UI", 10),
            activebackground=self.PURPLE,
            activeforeground=self.FOREGROUND, bd=0)

    # ======================== SMALL HELPERS ==============
    def _sep_v(self, parent):
        tk.Frame(parent, bg=self.CURRENT, width=1).pack(
            side="left", fill="y", padx=(0, 12), pady=4)

    def _hover_btn(self, w, bg_n, bg_h):
        w.bind("<Enter>", lambda e: (
            w.config(bg=bg_h)
            if str(w.cget("state")) != "disabled"
            else None))
        w.bind("<Leave>", lambda e: (
            w.config(bg=bg_n)
            if str(w.cget("state")) != "disabled"
            else None))

    def _action_btn(self, parent, texto, cmd, cor, px):
        b = tk.Button(parent, text=f"  {texto}  ",
            font=("Segoe UI", 10, "bold"),
            bg=self.CURRENT, fg=cor,
            relief="flat", pady=5, padx=6, bd=0,
            cursor="hand2",
            activebackground=self.BG_LIGHTER,
            activeforeground=cor, command=cmd)
        b.pack(side="left", padx=(px, 0))
        self._hover_btn(b, self.CURRENT, self.BG_LIGHTER)
        return b

    @staticmethod
    def _tamanho_arquivo(path):
        try:
            sz = os.path.getsize(path)
            if sz < 1024:
                return f"{sz} B"
            if sz < 1024 ** 2:
                return f"{sz / 1024:.0f} KB"
            if sz < 1024 ** 3:
                return f"{sz / 1024**2:.1f} MB"
            return f"{sz / 1024**3:.2f} GB"
        except Exception:
            return "?"

    def _status(self, msg, cor=None):
        self.label_status.config(
            text=msg, fg=cor or self.FOREGROUND)
        self.root.update_idletasks()

    def _toast(self, msg, cor=None, duracao=2500):
        cor = cor or self.GREEN
        self.toast_label.config(
            text=f"  {msg}  ", fg=cor,
            bg=self.BG_DARKER)
        self.toast_label.place(
            relx=0.5, y=95, anchor="center")
        if self._toast_id:
            self.root.after_cancel(self._toast_id)
        self._toast_id = self.root.after(
            duracao,
            lambda: self.toast_label.place_forget())

    def _formatar_texto(self, texto):
        texto = re.sub(r'([.!?])\s+', r'\1\n\n', texto)
        texto = re.sub(r'\n{3,}', '\n\n', texto)
        return texto.strip()

    def _font_mais(self):
        self.font_size = min(24, self.font_size + 1)
        self.texto_resultado.config(
            font=("Consolas", self.font_size))

    def _font_menos(self):
        self.font_size = max(7, self.font_size - 1)
        self.texto_resultado.config(
            font=("Consolas", self.font_size))

    # ======================== DROP ZONE ==================
    def _desenhar_drop(self, event=None):
        c = self.drop_canvas
        w, h = c.winfo_width(), c.winfo_height()
        if w < 20:
            return
        c.delete("all")
        borda = (self.PURPLE if self._drop_hover
                 else self.COMMENT)
        c.create_rectangle(10, 8, w - 10, h - 8,
            outline=borda, width=1, dash=(8, 4))
        if not self.arquivos:
            c.create_text(w // 2, h // 2 - 14,
                text=self._t("drop_title"),
                font=("Segoe UI", 13, "bold"),
                fill=self.PURPLE)
            c.create_text(w // 2, h // 2 + 8,
                text=self._t("drop_formats"),
                font=("Segoe UI", 9),
                fill=self.COMMENT)
            c.create_text(w // 2, h // 2 + 26,
                text=self._t("drop_hint"),
                font=("Segoe UI", 8),
                fill=self.CURRENT)
        else:
            nomes = [os.path.basename(f)
                     for f in self.arquivos]
            tams = [self._tamanho_arquivo(f)
                    for f in self.arquivos]
            info = "  |  ".join(
                f"{n} ({t})"
                for n, t in zip(nomes, tams))
            if len(info) > 85:
                info = info[:82] + "…"
            c.create_text(w // 2, h // 2 - 10,
                text=info,
                font=("Segoe UI", 11, "bold"),
                fill=self.GREEN)
            c.create_text(w // 2, h // 2 + 12,
                text=(self._t("drop_files").format(
                          n=len(self.arquivos))
                      + "  ·  "
                      + self._t("drop_change")),
                font=("Segoe UI", 9),
                fill=self.COMMENT)

    def _drop_enter(self, e):
        self._drop_hover = True
        self.drop_canvas.config(bg=self.BG_LIGHTER)
        self.drop_frame.config(bg=self.PURPLE)
        self._desenhar_drop()

    def _drop_leave(self, e):
        self._drop_hover = False
        self.drop_canvas.config(bg=self.BG_DARKER)
        self.drop_frame.config(bg=self.CURRENT)
        self._desenhar_drop()

    # ======================== TIMER ======================
    def _iniciar_timer(self):
        self.tempo_inicio = time.time()
        self.timer_rodando = True
        self.label_timer.config(fg=self.PURPLE)
        self._tick()

    def _tick(self):
        if not self.timer_rodando:
            return
        el = int(time.time() - self.tempo_inicio)
        m, s = divmod(el, 60)
        self.label_timer.config(text=f"{m:02d}:{s:02d}")
        self.root.after(1000, self._tick)

    def _parar_timer(self):
        self.timer_rodando = False
        self.label_timer.config(fg=self.GREEN)

    # ======================== ARQUIVO ====================
    def _selecionar_arquivos(self):
        if self.transcrevendo:
            return
        tipos = [
            (self._t("dlg_tipo_audio"),
             "*.mp3 *.wav *.m4a *.ogg *.flac "
             "*.wma *.aac *.webm *.mp4"),
            (self._t("dlg_tipo_todos"), "*.*")]
        caminhos = filedialog.askopenfilenames(
            title=self._t("dlg_abrir"), filetypes=tipos)
        if caminhos:
            self.arquivos = list(caminhos)
            self._desenhar_drop()
            n = len(self.arquivos)
            self._status(
                self._t("status_arquivos").format(n=n),
                self.GREEN)
            self._toast(
                self._t("toast_arquivos").format(n=n),
                self.GREEN)

    def _limpar_tudo(self):
        if self.transcrevendo:
            return
        self.arquivos = []
        self.segmentos_resultado = []
        self._desenhar_drop()
        self.texto_resultado.delete("1.0", tk.END)
        self.label_info.config(text="")
        self.label_timer.config(text="00:00",
                                fg=self.COMMENT)
        self._status(self._t("status_pronto_curto"),
                     self.GREEN)
        self._toast(self._t("toast_limpo"), self.ORANGE)

    # ======================== COPIAR / SALVAR ============
    def _copiar_texto(self):
        txt = self.texto_resultado.get(
            "1.0", tk.END).strip()
        if txt:
            self.root.clipboard_clear()
            self.root.clipboard_append(txt)
            self._status(self._t("status_copiado"),
                         self.GREEN)
            self._toast(self._t("toast_copiado"),
                        self.GREEN)
        else:
            self._status(self._t("status_nada_copiar"),
                         self.ORANGE)
            self._toast(self._t("toast_nada_copiar"),
                        self.ORANGE)

    def _salvar_txt(self):
        txt = self.texto_resultado.get(
            "1.0", tk.END).strip()
        if not txt:
            messagebox.showwarning(
                self._t("msg_aviso"),
                self._t("msg_sem_texto"))
            return
        cam = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[
                (self._t("dlg_tipo_texto"), "*.txt"),
                (self._t("dlg_tipo_todos"), "*.*")],
            title=self._t("dlg_salvar_txt"))
        if cam:
            with open(cam, "w", encoding="utf-8") as f:
                f.write(txt)
            self._status(
                self._t("status_txt_salvo").format(
                    cam=cam), self.GREEN)
            self._toast(self._t("toast_txt_salvo"),
                        self.GREEN)

    def _salvar_srt(self):
        if not self.segmentos_resultado:
            messagebox.showwarning(
                self._t("msg_aviso"),
                self._t("msg_sem_seg"))
            return
        cam = filedialog.asksaveasfilename(
            defaultextension=".srt",
            filetypes=[
                (self._t("dlg_tipo_srt"), "*.srt"),
                (self._t("dlg_tipo_todos"), "*.*")],
            title=self._t("dlg_salvar_srt"))
        if cam:
            with open(cam, "w", encoding="utf-8") as f:
                for i, seg in enumerate(
                        self.segmentos_resultado, 1):
                    ini = self._seg_para_srt(seg["start"])
                    fim = self._seg_para_srt(seg["end"])
                    f.write(
                        f"{i}\n{ini} --> {fim}\n"
                        f"{seg['text'].strip()}\n\n")
            self._status(
                self._t("status_srt_salvo").format(
                    cam=cam), self.GREEN)
            self._toast(self._t("toast_srt_salvo"),
                        self.GREEN)

    @staticmethod
    def _seg_para_srt(seg):
        h  = int(seg // 3600)
        m  = int((seg % 3600) // 60)
        s  = int(seg % 60)
        ms = int((seg % 1) * 1000)
        return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"

    # ======================== CACHE WHISPER ==============
    def _get_whisper_cache_dir(self):
        xdg = os.environ.get("XDG_CACHE_HOME")
        if xdg:
            return os.path.join(xdg, "whisper")
        return os.path.join(
            os.path.expanduser("~"),
            ".cache", "whisper")

    def _limpar_cache_modelo(self, nome_modelo):
        cache_dir = self._get_whisper_cache_dir()
        if not os.path.isdir(cache_dir):
            return
        patterns = [
            f"{nome_modelo}*.pt",
            f"{nome_modelo}*.download",
        ]
        for pattern in patterns:
            for fp in glob.glob(
                    os.path.join(cache_dir, pattern)):
                try:
                    sz = os.path.getsize(fp)
                    min_sz = self.TAMANHO_MINIMO_MODELO.get(
                        nome_modelo, 0)
                    if (sz < min_sz
                            or fp.endswith(".download")):
                        os.remove(fp)
                except Exception:
                    pass

    def _modelo_ja_em_cache(self, nome_modelo):
        cache_dir = self._get_whisper_cache_dir()
        if not os.path.isdir(cache_dir):
            return False
        patterns = [
            f"{nome_modelo}.pt",
            f"{nome_modelo}-v2.pt",
            f"{nome_modelo}-v3.pt",
        ]
        min_sz = self.TAMANHO_MINIMO_MODELO.get(
            nome_modelo, 0)
        for pattern in patterns:
            for fp in glob.glob(
                    os.path.join(cache_dir, pattern)):
                try:
                    if os.path.getsize(fp) >= min_sz:
                        return True
                except Exception:
                    pass
        return False

    # ======================== CARREGAR COM RETRY =========
    def _carregar_modelo_com_retry(self, nome_modelo):
        import whisper
        max_t = self.MAX_TENTATIVAS_DOWNLOAD
        ultimo_erro = None

        for tentativa in range(1, max_t + 1):
            try:
                if tentativa == 1:
                    self._status(
                        self._t("status_carregando"
                        ).format(
                            modelo=nome_modelo.upper()),
                        self.ORANGE)
                else:
                    self._status(
                        self._t("status_carregando_n"
                        ).format(
                            modelo=nome_modelo.upper(),
                            t=tentativa, max=max_t),
                        self.ORANGE)

                modelo = whisper.load_model(nome_modelo)
                return modelo

            except Exception as e:
                ultimo_erro = e
                erro_str = str(e).lower()
                erros_rede = [
                    "timeout", "timed out", "connection",
                    "urlopen", "download", "eof", "reset",
                    "broken pipe", "incomplete",
                    "urlerror", "httperror", "ssl",
                    "remote end closed",
                    "chunkedencodingerror",
                    "connectionerror",
                ]
                is_rede = any(
                    kw in erro_str for kw in erros_rede)

                if is_rede and tentativa < max_t:
                    self._limpar_cache_modelo(nome_modelo)
                    pausa = self.PAUSA_ENTRE_TENTATIVAS[
                        min(tentativa - 1,
                            len(self.PAUSA_ENTRE_TENTATIVAS)
                            - 1)]
                    self._status(
                        self._t("status_retry").format(
                            seg=pausa),
                        self.RED)
                    time.sleep(pausa)
                    self._status(
                        self._t("status_cache_limpo"
                        ).format(
                            modelo=nome_modelo.upper()),
                        self.ORANGE)
                    time.sleep(1)
                else:
                    raise

        raise Exception(
            self._t("msg_download_falhou").format(
                modelo=nome_modelo.upper(),
                max=max_t,
                erro=str(ultimo_erro)))

    # ======================== TRANSCREVER =================
    def _clique_modelo(self, nome_modelo):
        if self.transcrevendo:
            messagebox.showinfo(
                self._t("msg_aguarde_titulo"),
                self._t("msg_aguarde"))
            return
        if not self.arquivos:
            messagebox.showwarning(
                self._t("msg_aviso"),
                self._t("msg_selecione"))
            return

        for nm, info in self.btns_modelos.items():
            if nm == nome_modelo:
                info["btn"].config(
                    bg=info["cor"], fg=self.BG_DARKER)
                info["outer"].config(bg=info["cor"])
            else:
                info["btn"].config(
                    bg=self.BG_DARKER, fg=info["cor"])
                info["outer"].config(bg=self.CURRENT)

        self.transcrevendo = True
        self._desabilitar()
        self.progress.start(14)
        self.texto_resultado.delete("1.0", tk.END)
        self.label_info.config(text="")
        self.segmentos_resultado = []
        self.text_border.config(bg=self.PURPLE)
        self._iniciar_timer()

        threading.Thread(
            target=self._transcrever,
            args=(nome_modelo,),
            daemon=True).start()

    def _desabilitar(self):
        for info in self.btns_modelos.values():
            info["btn"].config(state="disabled")
        self.menu_idioma.config(state="disabled")
        self.drop_canvas.config(cursor="watch")

    def _habilitar(self):
        for nm, info in self.btns_modelos.items():
            info["btn"].config(
                state="normal",
                bg=self.BG_DARKER, fg=info["cor"])
            info["outer"].config(bg=self.CURRENT)
        self.menu_idioma.config(state="normal")
        self.drop_canvas.config(cursor="hand2")
        self.text_border.config(bg=self.CURRENT)

    def _transcrever(self, nome_modelo):
        try:
            import whisper
        except ImportError:
            self._resultado_erro(self._t("msg_whisper"))
            return

        idioma_cod = self._get_whisper_code()
        usar_ts    = self.var_timestamps.get()
        quebrar    = self.var_quebra_linha.get()

        try:
            if (self.modelo_carregado is None
                    or self.nome_modelo_carregado
                    != nome_modelo):
                self.modelo_carregado = \
                    self._carregar_modelo_com_retry(
                        nome_modelo)
                self.nome_modelo_carregado = nome_modelo
                self._status(
                    self._t("status_carregado").format(
                        modelo=nome_modelo.upper()),
                    self.GREEN)

            resultado  = []
            todos_seg  = []
            idioma_det = "?"

            for i, arq in enumerate(self.arquivos, 1):
                nome_arq = os.path.basename(arq)
                self._status(
                    self._t("status_transcrevendo"
                    ).format(
                        modelo=nome_modelo.upper(),
                        i=i, n=len(self.arquivos),
                        arq=nome_arq),
                    self.PURPLE)

                kw = {"fp16": USA_GPU,
                      "task": "transcribe",
                      "verbose": False}
                if idioma_cod is not None:
                    kw["language"] = idioma_cod

                res = self.modelo_carregado.transcribe(
                    arq, **kw)
                segs = res.get("segments", [])
                todos_seg.extend(segs)
                idioma_det = res.get(
                    "language", idioma_det)

                if len(self.arquivos) > 1:
                    resultado.append(
                        f"\n{'=' * 50}")
                    resultado.append(
                        f"  {nome_arq}")
                    if idioma_cod is None:
                        resultado.append(
                            self._t("idioma_detectado"
                            ).format(idioma=idioma_det))
                    resultado.append(
                        f"{'=' * 50}\n")

                if usar_ts:
                    for sg in segs:
                        mi, si = divmod(
                            int(sg["start"]), 60)
                        mf, sf = divmod(
                            int(sg["end"]), 60)
                        resultado.append(
                            f"[{mi:02d}:{si:02d} -> "
                            f"{mf:02d}:{sf:02d}]  "
                            f"{sg['text'].strip()}")
                    resultado.append("")
                else:
                    texto_bruto = res["text"].strip()
                    if quebrar:
                        texto_bruto = \
                            self._formatar_texto(
                                texto_bruto)
                    resultado.append(texto_bruto)
                    resultado.append("")

            self.segmentos_resultado = todos_seg
            texto_final = "\n".join(resultado).strip()

            el = (int(time.time() - self.tempo_inicio)
                  if self.tempo_inicio else 0)
            m, s = divmod(el, 60)
            tempo = f"{m:02d}:{s:02d}"

            self.root.after(
                0, self._mostrar_resultado,
                texto_final, nome_modelo,
                tempo, idioma_det)

        except Exception as e:
            self._resultado_erro(f"Erro:\n\n{e!s}")

    def _mostrar_resultado(self, texto, modelo,
                           tempo, idioma):
        self.texto_resultado.delete("1.0", tk.END)
        self.texto_resultado.insert("1.0", texto)
        self.progress.stop()
        self._parar_timer()
        self._habilitar()
        self.transcrevendo = False

        palavras = len(texto.split())
        chars    = len(texto)
        segs     = len(self.segmentos_resultado)

        self.label_info.config(
            text=self._t("info_template").format(
                palavras=palavras, chars=chars,
                segs=segs, modelo=modelo.upper(),
                idioma=idioma, tempo=tempo))
        self._status(
            self._t("status_concluido").format(
                modelo=modelo.upper(),
                palavras=palavras, tempo=tempo),
            self.GREEN)
        self._toast(
            self._t("toast_concluido").format(
                palavras=palavras, tempo=tempo),
            self.GREEN)

    def _resultado_erro(self, msg):
        def up():
            self.texto_resultado.delete("1.0", tk.END)
            self.texto_resultado.insert("1.0", msg)
            self.progress.stop()
            self._parar_timer()
            self._habilitar()
            self.transcrevendo = False
            self._status(self._t("status_erro"),
                         self.RED)
            self._toast(self._t("toast_erro"),
                        self.RED)
        self.root.after(0, up)


# ═══════════════════════════════════════════════════════
def main():
    # Garantir que estamos no diretório do script
    # (importante quando lançado via atalho)
    script_dir = os.path.dirname(
        os.path.abspath(__file__))
    os.chdir(script_dir)

    try:
        root = tk.Tk()
        TranscritorApp(root)
        root.mainloop()
    except Exception:
        # Sem console, mostrar erro em popup
        try:
            messagebox.showerror(
                "Erro Fatal",
                f"Erro ao iniciar o programa:\n\n"
                f"{traceback.format_exc()}")
        except Exception:
            pass


if __name__ == "__main__":
    main()