import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from datetime import datetime
from PIL import Image, ImageTk
import os

# --- DEFINIÇÃO DE CAMINHOS ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, 'base_novacap.db')

# --- BANCO DE DADOS ---
def iniciar_banco():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS desligados 
        (id INTEGER PRIMARY KEY AUTOINCREMENT, nome TEXT, cartao TEXT, data_recebido TEXT, status TEXT)''')
    conn.commit()
    conn.close()

def receber_cartao():
    nome, cartao = ent_nome.get().upper(), ent_cartao.get()
    if nome and cartao:
        conn = sqlite3.connect(DB_PATH)
        conn.cursor().execute("INSERT INTO desligados (nome, cartao, data_recebido, status) VALUES (?, ?, ?, 'Comigo')",
                       (nome, cartao, datetime.now().strftime("%d/%m/%Y %H:%M")))
        conn.commit()
        conn.close()
        ent_nome.delete(0, tk.END); ent_cartao.delete(0, tk.END)
        atualizar_lista()
    else: messagebox.showwarning("Aviso", "Preencha o Nome e o Cartão!")

def repassar_central():
    selecionados = tabela.get_children()
    if not selecionados:
        messagebox.showinfo("Vazio", "Não há cartões pendentes.")
        return
    if messagebox.askyesno("Confirmar", "Gerar protocolo e dar baixa para a Central?"):
        data_repasse = datetime.now().strftime("%d-%m-%Y_%H-%M")
        nome_arquivo = f"protocolo_central_{data_repasse}.txt"
        
        try:
            with open(nome_arquivo, "w", encoding="utf-8") as f:
                f.write("--- PROTOCOLO DE ENTREGA DE CARTÕES NOVACAP ---\n")
                f.write(f"Data: {datetime.now().strftime('%d/%m/%Y %H:%M')}\n\n")
                conn = sqlite3.connect(DB_PATH)
                cursor = conn.cursor()
                for item in selecionados:
                    d = tabela.item(item)['values']
                    # d[1] é o Nome, d[2] é o Cartão
                    f.write(f"REEDUCANDO: {d[1]} | CARTÃO: {d[2]}\n")
                    cursor.execute("UPDATE desligados SET status='Entregue' WHERE id=?", (d[0],))
                conn.commit()
                conn.close()
                f.write("\nRecebido por: ________________________________")
            atualizar_lista()
            messagebox.showinfo("Sucesso", f"Protocolo '{nome_arquivo}' criado!")
        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao gerar arquivo: {e}")

def atualizar_lista():
    for i in tabela.get_children(): tabela.delete(i)
    try:
        conn = sqlite3.connect(DB_PATH)
        for linha in conn.cursor().execute("SELECT id, nome, cartao, data_recebido FROM desligados WHERE status='Comigo'"):
            tabela.insert('', 'end', values=linha)
        conn.close()
    except: pass

# --- INTERFACE ---
janela = tk.Tk()
janela.title("NOVACAP - Controle de Acesso FUNAP")
janela.geometry("900x650")
janela.configure(bg="white")

frame_topo = tk.Frame(janela, bg="white")
frame_topo.pack(fill="x", pady=10)

def carregar_logo(nome_arquivo, w, h, lado):
    path = os.path.join(BASE_DIR, nome_arquivo)
    if os.path.exists(path):
        try:
            img_open = Image.open(path).resize((w, h), Image.Resampling.LANCZOS)
            img = ImageTk.PhotoImage(img_open)
            lbl = tk.Label(frame_topo, image=img, bg="white")
            lbl.image = img
            lbl.pack(side=lado, padx=30)
        except: pass

# Chamada das logos (ajuste os nomes se necessário)
carregar_logo("logo_gdf.png", 80, 80, "left")
carregar_logo("logo_novacap.png", 160, 50, "left")
carregar_logo("logo_funap.png", 80, 80, "right")

tk.Label(janela, text="SISTEMA DE RECEBIMENTO - DESLIGADOS", font=("Arial", 12, "bold"), bg="white", fg="#004a8d").pack(pady=10)

frame_in = tk.LabelFrame(janela, text=" Registro de Recolhimento ", bg="white", padx=10, pady=10)
frame_in.pack(padx=20, fill="x")

tk.Label(frame_in, text="NOME:", bg="white").grid(row=0, column=0)
ent_nome = tk.Entry(frame_in, width=40); ent_nome.grid(row=0, column=1, padx=5)

tk.Label(frame_in, text="CARTÃO:", bg="white").grid(row=0, column=2)
ent_cartao = tk.Entry(frame_in, width=10); ent_cartao.grid(row=0, column=3, padx=5)

tk.Button(frame_in, text="REGISTRAR", bg="#28a745", fg="white", font="bold", command=receber_cartao).grid(row=0, column=4, padx=10)

tabela = ttk.Treeview(janela, columns=("ID", "Nome", "Cartão", "Data"), show="headings")
for c in ("ID", "Nome", "Cartão", "Data"): 
    tabela.heading(c, text=c); tabela.column(c, anchor="center")
tabela.column("Nome", width=350, anchor="w")
tabela.pack(expand=True, fill="both", padx=20, pady=10)

tk.Button(janela, text="GERAR PROTOCOLO PARA CENTRAL", bg="#004a8d", fg="white", font="bold", pady=15, command=repassar_central).pack(fill="x", padx=20, pady=20)

iniciar_banco()
atualizar_lista()
janela.mainloop()
