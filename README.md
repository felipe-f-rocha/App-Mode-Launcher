# App Mode Launcher

Aplicação desktop em Python com **CustomTkinter** que permite abrir rapidamente conjuntos de aplicativos com base no modo de trabalho escolhido: **Coding**, **Talking** ou **Designing**.

> ⚠️ **Importante**  
> Os caminhos dos aplicativos (**paths**) e o **AUMID** **não vêm configurados propositalmente**.  
> Cada usuário deve adicionar manualmente **seus próprios valores** no código e no `config.json`.

---

## 📋 Tabela de Conteúdos

- [Visão Geral](#-visão-geral)
- [Funcionalidades](#-funcionalidades)
- [Pré-requisitos](#-pré-requisitos)
- [Instalação](#-instalação)
- [Configuração Manual](#-configuração-manual)
- [Uso](#-uso)
- [Estrutura do Projeto](#-estrutura-do-projeto)
- [Dependências](#-dependências)
- [Observações Importantes](#-observações-importantes)
- [Licença](#-licença)

---

## 📖 Visão Geral

O **App Mode Launcher** é uma interface gráfica simples que permite ao usuário escolher um modo de trabalho. Ao selecionar um modo, a aplicação abre automaticamente os aplicativos configurados pelo próprio usuário e encerra a interface.

O projeto foi desenvolvido para ser **totalmente personalizável**, evitando configurações fixas que só funcionariam em uma máquina específica.

---

## ✨ Funcionalidades

- Interface gráfica moderna com **CustomTkinter**
- Modos disponíveis:
  - **Coding** – aplicativos de programação
  - **Talking** – aplicativos de conversa
  - **Designing** – aplicativos de design
- Ícones personalizados
- Alternância entre **tema claro** e **tema escuro**
- Configuração manual simples

---

## 🧰 Pré-requisitos

- Python **3.10 ou superior**
- Sistema operacional **Windows**
- Pip atualizado

---

## ⚙️ Instalação

1. Clone o repositório:
   ```bash
   git clone https://github.com/felipe-f-rocha/app-mode-launcher.git
   cd app-mode-launcher
   
2. (Opcional) Crie um ambiente virtual:
    ```bash
    python -m venv venv
    venv\Scripts\activate
   
3. Instale as dependências:
   ```bash
   pip install -r requirements.txt

## 🔧 Configuração Manual

### 1️⃣ Arquivo `config.json`

O usuário deve definir manualmente quais aplicativos serão abertos nos modos **Coding** e **Designing**.

```json
{
  "apps": {
    "coding": [
      "CAMINHO_OU_COMANDO_DO_SEU_APP"
    ],
    "designing": [
      "CAMINHO_OU_COMANDO_DO_SEU_APP"
    ]
  }
}
```

💡 **Os valores podem ser:**

- **Caminhos completos**  
  `C:\\Program Files\\...`

- **Comandos disponíveis no PATH**  
  Ex.: `code`, `cmd`

---

### 2️⃣ Configuração do AUMID (Modo Talking)

No arquivo principal (`app.py`), substitua manualmente o valor da variável `aumid`:

```python
aumid = "COLOQUE_AQUI_O_AUMID_DO_SEU_APP_DE_CONVERSA"
```
Esse passo é necessário para aplicativos instalados via **Microsoft Store** (ex.: WhatsApp).

---
## ▶️ Uso

Execute o aplicativo com:

```bash
python app.py
```

1. Escolha o modo desejado  
2. Os aplicativos configurados serão abertos  
3. A aplicação será encerrada automaticamente  

Use o switch **“Mudar Tema”** para alternar entre claro e escuro.

---
## 📁 Estrutura do Projeto

```arduíno
├── assets/
│ ├── coding_icon.png
│ ├── talk_icon.png
│ └── design_icon.png
├── config.json
├── app.py
├── requirements.txt
└── README.md
```

---

## 📦 Dependências

Conteúdo sugerido para `requirements.txt`:
```txt
customtkinter
pillow
```
---
## ⚠️ Observações Importantes
- O projeto não funciona imediatamente após o clone
- Cada usuário deve configurar:
  - Paths ou comandos dos aplicativos   
  - AUMID do aplicativo de conversa
- Isso é intencional para garantir compatibilidade com qualquer máquina
---
## 📄 Licença

Este projeto está sob a licença MIT.
