#%% 
import requests
import json
from datetime import datetime
import os
import tkinter as tk
from tkinter import ttk, messagebox


def obter_moedas_disponiveis():
    try: 
        resposta = requests.get("https://api.frankfurter.app/currencies")
        return resposta.json()
    except:
        return{}
    

def converter_moeda(origem, destino, valor):
    try:
        url = f"https://api.frankfurter.app/latest?amount={valor}&from={origem}&to={destino}"
        resposta = requests.get(url)
        dados = resposta.json()
        return dados['rates'][destino]
    except:
        return None

def salvar_historico(origem, destino, valor, resultado):
    historico = []
    if os.path.exists("historico_conversoes.json"):
        with open("historico_conversoes.json", "r") as f:
            try:
                historico = json.load(f)
            except json.JSONDecodeError:
                historico = []

    conversao = {
        "data_hora": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "origem": origem,
        "destino": destino,
        "valor": valor,
        "resultado": resultado

    }
    historico.append(conversao)
    with open("historico_conversoes.json", "w") as f:
        json.dump(historico, f, indent=4)

def mostrar_historico():
    if not os.path.exists("historico_conversoes.json"):
        messagebox.showinfo("Histórico", "Nenhum histórico encontrado.")
        return
    
    with open("historico_conversoes.json", "r") as f:
        try:
            historico = json.load(f)
        except json.JSONDecodeError:
            messagebox.showinfo("Histórico", "Erro ao carregar o histórico.")
            return
        
    texto = ""
    for item in historico:
        try: 
            texto += f"[{item['data_hora']}] {item['valor']} {item['origem']} → {item['resultado']:.2f} {item['destino']}"
        except KeyError:
            continue

    messagebox.showinfo("Histórico de Conversões", texto if texto else "Histórico Vazio")

def realizar_conversao():
    origem = combo_origem.get()
    destino = combo_destino.get()
    try:
        valor = float(entry_valor.get())
    except ValueError:
        messagebox.showerror("Erro", "Digite um valorn numérico válido.")
        return
    
    resultado = converter_moeda(origem, destino, valor)
    if resultado is None:
        messagebox.showerror("Erro", "Falha na Conversão.")
    else:
        label_resultado.config(text=f"{valor:.2f} {origem} = {resultado:.2f} {destino}")
        salvar_historico(origem, destino, valor, resultado)
    
# -- Interface --
moedas = obter_moedas_disponiveis()
if not moedas:
    print("Erro ao obter lista de moedas disponíveis.")
    exit()

root = tk.Tk()
root.title("Conversor de Moedas")
root.geometry("400x400")
root.resizable(False, False)

tk.Label(root, text="Moeda de Origem:").pack(pady=5)
combo_origem = ttk.Combobox(root, values=sorted(moedas.keys()))
combo_origem.set("USD")
combo_origem.pack()

tk.Label(root, text="Moeda de Destino:").pack(pady=5)
combo_destino = ttk.Combobox(root, values=sorted(moedas.keys()))
combo_destino.set("BRL")
combo_destino.pack()

tk.Button(root, text="Valor:").pack(pady=5)
entry_valor = tk.Entry(root)
entry_valor.pack()

tk.Button(root, text="Converter", command=realizar_conversao).pack(pady=10)
label_resultado = tk.Label(root, text="", font=("Arial", 12))
label_resultado.pack(pady=5)

tk.Button(root, text="Ver histórico", command=mostrar_historico).pack(pady=10)

root.mainloop()
