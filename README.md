# ⚡ ROM Manager Pro

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10+-blue?style=for-the-badge&logo=python&logoColor=white"/>
  <img src="https://img.shields.io/badge/PySide6-Qt6-green?style=for-the-badge&logo=qt&logoColor=white"/>
  <img src="https://img.shields.io/badge/Platform-Windows%20%7C%20Linux%20%7C%20macOS-lightgrey?style=for-the-badge"/>
  <img src="https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge"/>
</p>

<p align="center">
  Ferramenta desktop para gerenciamento de ROMs Android via ADB e Fastboot — com suporte a AOSP e HyperOS.
</p>

---

## 📸 Preview

> Interface dark minimalista com sidebar de navegação, cards de informação do dispositivo e terminais interativos.

---

## ✨ Funcionalidades

### 🖥 Sistema
- Exibe informações do dispositivo em tempo real: modelo, versão Android, serial, IMEI, RAM, armazenamento e bateria
- Arredondamento de RAM e armazenamento para valores comerciais reais (ex: 7.4 GB → 8 GB)

### 📦 Apps
- Lista todos os apps de terceiros instalados
- Instala APKs diretamente do PC via `adb install`
- Menu de contexto: abrir app, backup APK, limpar dados, desinstalar

### ⌨ ADB Shell
- Terminal ADB integrado com histórico de saída
- Auto-prefixo `adb` — basta digitar o subcomando

### ⚡ Fastboot
- Terminal Fastboot com ações rápidas (Devices, Reboot, Bootloader, Recovery)
- Auto-prefixo `fastboot`

### 🗜 Flash AOSP
- Extração automática de `payload.bin` via **payload-dumper-go**
- Seleção de partições customizáveis (`boot`, `init_boot`, `vendor_boot`, etc.)
- Flash sequencial via fastboot com log ao vivo
- Suporte a `adb sideload` com pop-up de confirmação

### 🔥 Flash HyperOS
- Extrai o ZIP da ROM HyperOS completo
- Lista automaticamente todos os scripts `.bat` / `.sh` encontrados
- O usuário escolhe o script (update OTA, clean install, etc.) e executa com um clique

### 🌐 Multilíngue
- Interface disponível em **Português**, **English**, **Español** e **Русский**
- Troca de idioma instantânea pela sidebar

---

## 🔧 Requisitos

| Dependência | Versão mínima | Obrigatório |
|---|---|---|
| Python | 3.10+ | ✅ |
| PySide6 | 6.x | ✅ |
| ADB (Android Debug Bridge) | qualquer | ✅ |
| Fastboot | qualquer | ✅ |
| payload-dumper-go | qualquer | ⚠️ apenas para Flash AOSP |

---

## 🚀 Instalação

### 1. Clone o repositório

```bash
git clone https://github.com/alysonsb/RomManagerPro
cd RomManagerPro
```

### 2. Instale as dependências Python

```bash
pip install PySide6
```

> No Linux, se necessário adicione `--break-system-packages`:
> ```bash
> pip install PySide6 --break-system-packages
> ```

### 3. Instale o ADB e Fastboot

**Windows:**
Baixe o [Android SDK Platform Tools](https://developer.android.com/tools/releases/platform-tools) e adicione ao PATH.

**Linux (Debian/Ubuntu):**
```bash
sudo apt install adb fastboot
```

**macOS:**
```bash
brew install android-platform-tools
```

### 4. Execute

```bash
python rom_manager.py
```

---

## 📦 Instalação do payload-dumper-go

> Necessário apenas para a aba **Flash AOSP** — extração de partições de ROMs com `payload.bin`.

### O que é?
`payload-dumper-go` é uma ferramenta open source escrita em Go que extrai imagens de partição (`.img`) a partir do arquivo `payload.bin` presente em ROMs no formato A/B (a maioria das ROMs modernas).

### Download

Acesse a página de releases oficial:

👉 **https://github.com/ssut/payload-dumper-go/releases**

Baixe o binário correspondente ao seu sistema operacional:

| Sistema | Arquivo |
|---|---|
| Windows 64-bit | `payload-dumper-go_*_windows_amd64.zip` |
| Linux 64-bit | `payload-dumper-go_*_linux_amd64.tar.gz` |
| macOS (Intel) | `payload-dumper-go_*_darwin_amd64.tar.gz` |
| macOS (Apple Silicon) | `payload-dumper-go_*_darwin_arm64.tar.gz` |

### Configuração

**Opção 1 — Adicionar ao PATH (recomendado)**

Coloque o executável em uma pasta que esteja no PATH do sistema. Assim, o ROM Manager Pro encontra automaticamente — deixe o campo no app com o valor padrão `payload-dumper-go`.

**Windows:** Mova `payload-dumper-go.exe` para `C:\Windows\System32\` ou adicione a pasta ao PATH nas variáveis de ambiente.

**Linux/macOS:**
```bash
sudo mv payload-dumper-go /usr/local/bin/
sudo chmod +x /usr/local/bin/payload-dumper-go
```

**Opção 2 — Selecionar manualmente no app**

Na aba **Flash AOSP**, clique em **"Selecionar Executável"** e navegue até onde salvou o arquivo.

### Verificar instalação

```bash
payload-dumper-go --version
```

---

## 📱 Configurando o dispositivo Android

Antes de usar qualquer função, ative as opções de desenvolvedor:

1. Vá em **Configurações → Sobre o telefone**
2. Toque em **Número da versão** 7 vezes
3. Vá em **Configurações → Opções do desenvolvedor**
4. Ative **Depuração USB**
5. Conecte o cabo e autorize o computador no popup do celular

Verifique a conexão:
```bash
adb devices
```

---

## 🗜 Como fazer flash de uma ROM AOSP

1. Abra a aba **Flash AOSP**
2. Selecione o arquivo `.zip` da ROM
3. Configure o executável `payload-dumper-go` (se não estiver no PATH)
4. Defina as partições desejadas (padrão: `boot,init_boot,vendor_boot`)
5. Clique em **Iniciar Extração** e aguarde
6. Clique em **Reboot Fastboot** para reiniciar o dispositivo no modo fastboot
7. Clique em **Fazer Flash Agora**
8. Após o flash, clique em **Reboot Recovery**

---

## 🔥 Como fazer flash de uma ROM HyperOS

1. Abra a aba **Flash HyperOS**
2. Selecione o arquivo `.zip` da ROM HyperOS
3. Clique em **Extrair ROM** e aguarde a extração completa
4. Escolha o script de instalação na lista:
   - Scripts com `update` = instalação OTA (mantém dados)
   - Scripts com `clean` = instalação limpa (apaga dados)
5. Clique em **Executar Script**

---

## 🛠 Estrutura do projeto

```
RomManagerPro/
├── rom_manager.py      # Aplicação principal
└── README.md
```

---

## 🤝 Contribuindo

Pull requests são bem-vindos! Para mudanças maiores, abra uma issue primeiro para discutir o que você gostaria de alterar.

---

## 📬 Contato

- **Telegram:** [@romManagerPro](https://t.me/romManagerPro)
- **GitHub:** [@alysonsb](https://github.com/alysonsb)

---

## ☕ Apoie o projeto

Se este projeto te ajudou, considere fazer uma doação:

[![PayPal](https://img.shields.io/badge/PayPal-Doe_um_café-00457C?style=for-the-badge&logo=paypal&logoColor=white)](https://www.paypal.com/donate)

---

<p align="center">desenvolvido com ❤️ por <a href="https://github.com/alysonsb">@alysonsb</a></p>
