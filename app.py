import subprocess
import customtkinter
import json
from PIL import Image
import sys

try:
    with open("config.json", "r", encoding="utf-8") as f:
        config = json.load(f)

except FileNotFoundError:
    print("❌ config.json não encontrado")
    sys.exit()

except json.JSONDecodeError:
    print("❌ Erro ao ler o config.json (JSON inválido)")
    sys.exit()

ICONS = {
    "coding": customtkinter.CTkImage(
    light_image=Image.open("assets/coding_icon.png")),

    "talking": customtkinter.CTkImage(
    light_image=Image.open("assets/talk_icon.png")),

    "design": customtkinter.CTkImage(
        light_image=Image.open("assets/design_icon.png")
    )
}

def coding():
    """Abre aplicativos para codar"""

    for i in config["apps"]["coding"]:
        subprocess.Popen(i, shell=True)

    app.destroy()

def talking():
    """Abre aplicativos para conversa"""
    # aumid - nome do identificador de aplicativos da Microsoft Store

    aumid = config["apps"]["talking"]["aumid"]

    # Busca o app na pasta virtual "app folder" para abrir o aplicativo que não é .exe
    if not aumid:
        print("AUMID não configurado")
        sys.exit()

    subprocess.Popen(["explorer.exe",f"shell:appsFolder\\{aumid}"])

    app.destroy()

def designing():
    """Abre aplicativos essenciais para fazer design"""

    for i in config["apps"]["designing"]:
        subprocess.Popen(i, shell=True)

    app.destroy()

app = customtkinter.CTk()

# Frame Principal
frame = customtkinter.CTkFrame(app)
frame.grid(row=0, column=0, padx=20, pady=20)

# Expandir o frame dentro da janela
app.grid_rowconfigure(0, weight=1)
app.grid_columnconfigure(0, weight=1)

# Configurar colunas internas do frame
frame.grid_columnconfigure(0, weight=1)
frame.grid_columnconfigure(1, weight=1)
frame.grid_columnconfigure(2, weight=1)

# Título
label = customtkinter.CTkLabel(
    frame,
    text='Qual modo deseja usar?',
    fg_color='transparent',
    font=('JetBrains Mono ExtraBold', 38)
)
label.grid(row=0, column=0, columnspan=3, pady=(0, 20))


btn_aspectos = {
    "text_color": "white",
    "fg_color": "black",
    "font": ("JetBrains Mono ExtraBold", 20)
}

# Botões
button1 = customtkinter.CTkButton(
    frame,
    text="Coding",
    command=coding,
    image=ICONS["coding"],
    **btn_aspectos
)
button1.grid(row=1, column=0, padx=10, pady=10)

button2 = customtkinter.CTkButton(
    frame,
    text="Talking",
    command=talking,
    image=ICONS["talking"],
    **btn_aspectos
)
button2.grid(row=1, column=1, padx=10, pady=10)

button3 = customtkinter.CTkButton(
    frame,
    text="Designing",
    command=designing,
    image=ICONS["design"],
    **btn_aspectos
)
button3.grid(row=1, column=2, padx=10, pady=10)

# Switch Theme
def switch_event():
    match switch_var.get():
        case "off":
            customtkinter.set_appearance_mode("dark")
        case "on":
            customtkinter.set_appearance_mode("light")

switch_var = customtkinter.StringVar(value="off")
switch = customtkinter.CTkSwitch(frame, text="Mudar Tema", command=switch_event,
                                 variable=switch_var, onvalue="on", offvalue="off")
switch.grid(row=2, column=2, padx=10, pady=10)

app.mainloop()