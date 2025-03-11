from dataclasses import dataclass
from typing import Optional
import tkinter as tk
from tkinter import filedialog, scrolledtext, messagebox, ttk
import socket
import threading
import os
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path


@dataclass
class ScanConfig:
    """Configurações do scan"""
    max_threads: int = 10
    timeout: int = 3
    retry_count: int = 2

class DnsBruteGUI:
    """Interface gráfica para DNS Scanner"""
    
    WINDOW_SIZE = "800x600"
    MIN_WINDOW_SIZE = (600, 400)
    PADDING = 20
    COLORS = {
        "background": "#f0f0f0",
        "primary": "#2c3e50",
        "success": "#27ae60",
        "error": "#c0392b",
        "warning": "#f39c12"
    }

    def __init__(self, root: tk.Tk):
        self.root = root
        self.config = ScanConfig()
        self.setup_window()
        self.setup_styles()
        self.create_widgets()
        self.create_menu()
        self.setup_logging()

    def setup_window(self):
        self.root.title("DNS Scanner Pro")
        self.root.geometry(self.WINDOW_SIZE)
        self.root.minsize(*self.MIN_WINDOW_SIZE)
        self.root.configure(bg=self.COLORS["background"])

    def setup_styles(self):
        self.style = ttk.Style()
        self.style.configure("Custom.TFrame", background=self.COLORS["background"])
        self.style.configure("Custom.TButton", padding=10)
        self.style.configure("Title.TLabel", 
                           font=('Segoe UI', 16, 'bold'),
                           background=self.COLORS["background"],
                           foreground=self.COLORS["primary"])

    def create_widgets(self):
        # Frame principal
        self.main_frame = ttk.Frame(self.root, style="Custom.TFrame", padding=self.PADDING)
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Título
        title_frame = ttk.Frame(self.main_frame, style="Custom.TFrame")
        title_frame.pack(fill=tk.X, pady=(0, 20))
        ttk.Label(title_frame, text="DNS Subdomain Scanner", style="Title.TLabel").pack(side=tk.LEFT)
        
        # Container para inputs
        input_frame = ttk.Frame(self.main_frame, padding=10)
        input_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Frame do domínio
        domain_frame = ttk.Frame(input_frame)
        domain_frame.pack(fill=tk.X, pady=5)
        ttk.Label(domain_frame, text="Domínio:").pack(side=tk.LEFT)
        self.dominio_entry = ttk.Entry(domain_frame, width=50)
        self.dominio_entry.pack(side=tk.LEFT, padx=(10, 0), fill=tk.X, expand=True)
        
        # Frame da wordlist
        wordlist_frame = ttk.Frame(input_frame)
        wordlist_frame.pack(fill=tk.X, pady=5)
        ttk.Label(wordlist_frame, text="Wordlist:").pack(side=tk.LEFT)
        self.arquivo_path = tk.StringVar()
        ttk.Entry(wordlist_frame, textvariable=self.arquivo_path, width=40).pack(
            side=tk.LEFT, padx=(10, 10), fill=tk.X, expand=True)
        ttk.Button(wordlist_frame, text="Selecionar Arquivo",
                  command=self.selecionar_arquivo).pack(side=tk.LEFT)
        
        # Frame de controles
        control_frame = ttk.Frame(self.main_frame)
        control_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.progress_var = tk.IntVar(value=0)
        self.progress_bar = ttk.Progressbar(control_frame, variable=self.progress_var, 
                                          maximum=100, mode='determinate')
        self.progress_bar.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        
        self.btn_iniciar = ttk.Button(control_frame, text="▶ Iniciar Scan",
                                    command=self.iniciar_scan)
        self.btn_iniciar.pack(side=tk.RIGHT)
        
        # Área de resultados
        result_frame = ttk.LabelFrame(self.main_frame, text="Resultados", padding=10)
        result_frame.pack(fill=tk.BOTH, expand=True)
        
        self.resultado_text = scrolledtext.ScrolledText(
            result_frame,
            font=('Consolas', 10),
            background="#ffffff",
            foreground=self.COLORS["primary"]
        )
        self.resultado_text.pack(fill=tk.BOTH, expand=True)
        
        # Barra de status
        self.status_bar = ttk.Label(
            self.main_frame,
            text="Status: Pronto",
            relief=tk.SUNKEN,
            padding=(5, 2)
        )
        self.status_bar.pack(fill=tk.X, pady=(10, 0))

    def setup_logging(self):
        logging.basicConfig(
            filename='dns_scanner.log',
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )

    def create_menu(self):
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)

        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Arquivo", menu=file_menu)
        file_menu.add_command(label="Exportar Resultados", command=self.exportar_resultados)
        file_menu.add_separator()
        file_menu.add_command(label="Sair", command=self.root.quit)

        config_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Configurações", menu=config_menu)
        config_menu.add_command(label="Preferências", command=self.show_preferences)

    def show_preferences(self):
        prefs = tk.Toplevel(self.root)
        prefs.title("Preferências")
        prefs.geometry("400x300")
        
        ttk.Label(prefs, text="Threads máximas:").pack()
        thread_spin = ttk.Spinbox(prefs, from_=1, to=50, width=10)
        thread_spin.set(self.config.max_threads)
        thread_spin.pack()

    def selecionar_arquivo(self):
        filename = filedialog.askopenfilename(
            title="Selecione a Wordlist",
            filetypes=[("Arquivos de texto", "*.txt")]
        )
        if filename:
            self.arquivo_path.set(filename)
            self.status_bar.config(text=f"Status: Arquivo selecionado: {os.path.basename(filename)}")

    def iniciar_scan(self):
        dominio = self.dominio_entry.get().strip()
        lista = self.arquivo_path.get()
        
        if not dominio or not lista:
            messagebox.showerror("Erro", "Por favor, preencha todos os campos")
            return
        
        self.resultado_text.delete(1.0, tk.END)
        self.btn_iniciar.config(state=tk.DISABLED)
        self.progress_var.set(0)
        self.progress_bar.config(value=0)
        self.status_bar.config(text="Status: Escaneando...")
        
        thread = threading.Thread(target=self.executar_scan, args=(dominio, lista))
        thread.daemon = True
        thread.start()

    def executar_scan(self, dominio: str, lista: str):
        try:
            linhas = Path(lista).read_text(encoding='utf-8').splitlines()
            total = len(linhas)
            encontrados = 0
        except FileNotFoundError:
            self.atualizar_resultado("❌ Arquivo não encontrado ou inválido\n")
            self.finalizar_scan()
            logging.error(f"Arquivo não encontrado: {lista}")
            return

        self.atualizar_resultado(f"🔍 Iniciando scan para {dominio}\n")
        self.atualizar_resultado("=" * 50 + "\n")

        with ThreadPoolExecutor(max_workers=self.config.max_threads) as executor:
            futures = {executor.submit(self.verificar_subdominio, linha, dominio): linha 
                      for linha in linhas}
            
            for i, future in enumerate(as_completed(futures), 1):
                try:
                    if resultado := future.result():
                        encontrados += 1
                        self.atualizar_resultado(resultado)
                    self.progress_var.set(int((i/total)*100))
                except Exception as e:
                    logging.error(f"Erro no scan: {e}")

        self.atualizar_resultado("\n" + "=" * 50 + "\n")
        self.atualizar_resultado(f"✨ Scan concluído! Encontrados {encontrados} subdomínios.\n")
        self.finalizar_scan(encontrados)

    def verificar_subdominio(self, linha: str, dominio: str) -> Optional[str]:
        """Verifica se um subdomínio existe e retorna seu IP"""
        subdominio = f"{linha}.{dominio}"
        for _ in range(self.config.retry_count):
            try:
                ip = socket.gethostbyname(subdominio)
                return f"✅ {subdominio} ({ip})\n"
            except socket.gaierror:
                continue
            except Exception as e:
                logging.error(f"Erro ao verificar {subdominio}: {e}")
                return f"❌ {subdominio}: {e}\n"
        return None

    def finalizar_scan(self, encontrados=0):
        self.btn_iniciar.config(state=tk.NORMAL)
        self.progress_var.set(100)
        self.progress_bar.config(value=100)
        self.status_bar.config(text=f"Status: Concluído - {encontrados} subdomínios encontrados")

    def atualizar_resultado(self, texto: str):
        """Atualiza a área de resultados com novo texto"""
        self.resultado_text.insert(tk.END, texto)
        self.resultado_text.see(tk.END)

    def exportar_resultados(self):
        """Exporta os resultados para um arquivo"""
        resultado = self.resultado_text.get(1.0, tk.END).strip()
        if not resultado:
            messagebox.showwarning("Aviso", "Não há resultados para exportar")
            return

        if filename := filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Arquivo de texto", "*.txt"), ("Todos os arquivos", "*.*")]
        ):
            try:
                Path(filename).write_text(resultado, encoding='utf-8')
                messagebox.showinfo("Sucesso", "Resultados exportados com sucesso!")
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao exportar: {e}")
                logging.error(f"Erro na exportação: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = DnsBruteGUI(root)
    root.mainloop()