import sys
import os
import subprocess
import re
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QGridLayout, QLabel, QPushButton, QListWidget, QListWidgetItem,
    QTextEdit, QLineEdit, QTabWidget, QFrame, QMenu, QSizePolicy,
    QGraphicsDropShadowEffect, QFileDialog, QMessageBox, QComboBox
)
from PySide6.QtCore import Qt, QThread, Signal, QSize
from PySide6.QtGui import QColor, QFont, QIcon, QPalette


# ===============================
# TRANSLATIONS
# ===============================
TRANSLATIONS = {
    "pt": {
        # Sidebar
        "nav_sistema":       "🖥  Sistema",
        "nav_apps":          "📦  Apps",
        "nav_adb":           "⌨  ADB Shell",
        "nav_fastboot":      "⚡  Fastboot",
        "nav_aosp":          "🗜  Flash AOSP",
        "nav_hyperos":       "🔥  Flash HyperOS",
        "donate":            "☕  Me doe um cafe",
        "dev_by":            "desenvolvido por @alysonsb",
        # Sistema
        "tab_sistema":       "Sistema",
        "tab_sistema_sub":   "Informações do dispositivo",
        "sec_device":        "DISPOSITIVO",
        "card_modelo":       "Modelo",
        "card_android":      "Android",
        "card_serial":       "Serial",
        "card_imei":         "IMEI",
        "card_ram":          "RAM",
        "card_storage":      "Armazenamento",
        "card_battery":      "Bateria",
        "card_health":       "Saúde",
        "btn_refresh":       "↻  Atualizar Dados",
        "health_unknown":    "Desconhecida",
        "health_good":       "Boa ✓",
        "health_overheat":   "Superaquecendo",
        "health_dead":       "Morta",
        "health_over_volt":  "Sobretensão",
        "health_failure":    "Falha",
        "health_cold":       "Fria",
        "restricted":        "Restrito",
        # Apps
        "tab_apps":          "Aplicativos",
        "tab_apps_sub":      "Pacotes instalados",
        "sec_install_apk":   "INSTALAR APK DO PC",
        "apk_placeholder":   "Selecione um arquivo .apk...",
        "btn_browse":        "📂  Procurar",
        "btn_install":       "📲  Instalar no Dispositivo",
        "installing":        "⏳  Instalando...",
        "install_ok":        "✓  Instalado com sucesso!",
        "sec_packages":      "PACOTES DE TERCEIROS",
        "btn_load_apps":     "↻  Carregar Apps",
        "packages_found":    "{n} pacotes encontrados",
        "menu_open":         "🚀  Abrir App",
        "menu_backup":       "💾  Backup APK",
        "menu_clear":        "🗑  Limpar Dados",
        "menu_uninstall":    "❌  Desinstalar",
        # ADB
        "tab_adb":           "ADB Shell",
        "tab_adb_sub":       "Execute comandos ADB",
        "sec_command":       "COMANDO",
        "adb_placeholder":   "shell getprop ro.product.model",
        "btn_run":           "Executar",
        "btn_clear":         "Limpar",
        "sec_output":        "SAÍDA",
        # Fastboot
        "tab_fastboot":      "Fastboot",
        "tab_fastboot_sub":  "Flash e bootloader",
        "fb_placeholder":    "flash boot boot.img",
        "sec_quick":         "AÇÕES RÁPIDAS",
        "btn_devices":       "Devices",
        "btn_reboot":        "Reboot",
        "btn_bootloader":    "Bootloader",
        "btn_recovery_warn": "⚠  Reboot Recovery",
        # AOSP
        "tab_aosp":          "Flash AOSP",
        "tab_aosp_sub":      "Extração de payload.bin e flash de partições",
        "sec_step1":         "PASSO 1 — SELECIONAR ROM (.zip)",
        "rom_placeholder":   "Selecione o arquivo .zip da ROM...",
        "btn_select_rom":    "Selecionar ROM",
        "dumper_label":      "Executável  payload-dumper-go",
        "dumper_hint":       "Se estiver no PATH, deixe o valor padrao",
        "dumper_placeholder":"payload-dumper-go",
        "btn_select_exe":    "Selecionar Executavel",
        "sec_step2":         "PASSO 2 — EXTRAIR PAYLOAD",
        "partitions_label":  "Partições:",
        "btn_extract":       "🗜  Iniciar Extração",
        "extract_start_msg": "Selecione uma ROM para começar.",
        "sec_step3":         "PASSO 3 — FLASH DAS PARTIÇÕES",
        "flash_info":        "Os comandos abaixo serão gerados automaticamente após a extração.",
        "btn_reboot_fb":     "🔄  Reboot Fastboot",
        "btn_flash_now":     "⚡  Fazer Flash Agora",
        "btn_reboot_rec":    "↩  Reboot Recovery",
        "btn_cleanup":       "🗑  Limpar Arquivos",
        "btn_flash_rom":     "📲  FLASH ROM",
        "sideload_title":    "⚠  Atenção — Antes de continuar",
        "sideload_bold":     "<b>Prepare o dispositivo antes de continuar!</b>",
        "sideload_body":     ("1. Certifique-se que o dispositivo está no <b>Recovery</b>.<br>"
                              "2. No recovery, acesse:<br>"
                              "&nbsp;&nbsp;&nbsp;<b>Apply update → Apply from ADB</b><br>"
                              "&nbsp;&nbsp;&nbsp;(ou <b>Update from ADB</b>, dependendo do recovery)<br>"
                              "3. Clique <b>OK</b> quando o dispositivo estiver aguardando.<br><br>"),
        "btn_confirm_flash": "✓  Estou pronto, iniciar flash",
        "btn_cancel":        "Cancelar",
        "sideload_notice":   ("⚠  No celular, acesse o recovery e selecione:  "
                              "\"Apply update\" → \"Apply from ADB\" (ou \"Update from ADB\").\n"
                              "   Aguarde a transferência concluir. Não desconecte o cabo."),
        # HyperOS
        "tab_hyperos":       "Flash HyperOS",
        "tab_hyperos_sub":   "Extração e flash via scripts oficiais",
        "sec_hyper_step1":   "PASSO 1 — SELECIONAR ROM HYPEROS (.zip)",
        "hyper_placeholder": "Selecione o arquivo .zip da ROM HyperOS...",
        "sec_hyper_step2":   "PASSO 2 — EXTRAIR E SELECIONAR SCRIPT DE INSTALACAO",
        "btn_hyper_extract": "🗜  Extrair ROM",
        "hyper_start_msg":   "Selecione uma ROM HyperOS para começar.",
        "sec_hyper_step3":   "PASSO 3 — ESCOLHA O SCRIPT DE FLASH",
        "scripts_hint":      ("Clique em um script para selecioná-lo.  "
                              "Dica: scripts com 'update' instalam como OTA, 'clean' apagam dados."),
        "sec_hyper_step4":   "PASSO 4 — EXECUTAR FLASH",
        "no_script":         "Nenhum script selecionado.",
        "btn_run_script":    "⚡  Executar Script",
    },

    "en": {
        "nav_sistema":       "🖥  System",
        "nav_apps":          "📦  Apps",
        "nav_adb":           "⌨  ADB Shell",
        "nav_fastboot":      "⚡  Fastboot",
        "nav_aosp":          "🗜  Flash AOSP",
        "nav_hyperos":       "🔥  Flash HyperOS",
        "donate":            "☕  Buy me a coffee",
        "dev_by":            "developed by @alysonsb",
        "tab_sistema":       "System",
        "tab_sistema_sub":   "Device information",
        "sec_device":        "DEVICE",
        "card_modelo":       "Model",
        "card_android":      "Android",
        "card_serial":       "Serial",
        "card_imei":         "IMEI",
        "card_ram":          "RAM",
        "card_storage":      "Storage",
        "card_battery":      "Battery",
        "card_health":       "Health",
        "btn_refresh":       "↻  Refresh Data",
        "health_unknown":    "Unknown",
        "health_good":       "Good ✓",
        "health_overheat":   "Overheating",
        "health_dead":       "Dead",
        "health_over_volt":  "Over Voltage",
        "health_failure":    "Failure",
        "health_cold":       "Cold",
        "restricted":        "Restricted",
        "tab_apps":          "Applications",
        "tab_apps_sub":      "Installed packages",
        "sec_install_apk":   "INSTALL APK FROM PC",
        "apk_placeholder":   "Select an .apk file...",
        "btn_browse":        "📂  Browse",
        "btn_install":       "📲  Install on Device",
        "installing":        "⏳  Installing...",
        "install_ok":        "✓  Installed successfully!",
        "sec_packages":      "THIRD-PARTY PACKAGES",
        "btn_load_apps":     "↻  Load Apps",
        "packages_found":    "{n} packages found",
        "menu_open":         "🚀  Open App",
        "menu_backup":       "💾  Backup APK",
        "menu_clear":        "🗑  Clear Data",
        "menu_uninstall":    "❌  Uninstall",
        "tab_adb":           "ADB Shell",
        "tab_adb_sub":       "Run ADB commands",
        "sec_command":       "COMMAND",
        "adb_placeholder":   "shell getprop ro.product.model",
        "btn_run":           "Run",
        "btn_clear":         "Clear",
        "sec_output":        "OUTPUT",
        "tab_fastboot":      "Fastboot",
        "tab_fastboot_sub":  "Flash & bootloader",
        "fb_placeholder":    "flash boot boot.img",
        "sec_quick":         "QUICK ACTIONS",
        "btn_devices":       "Devices",
        "btn_reboot":        "Reboot",
        "btn_bootloader":    "Bootloader",
        "btn_recovery_warn": "⚠  Reboot Recovery",
        "tab_aosp":          "Flash AOSP",
        "tab_aosp_sub":      "payload.bin extraction and partition flash",
        "sec_step1":         "STEP 1 — SELECT ROM (.zip)",
        "rom_placeholder":   "Select the ROM .zip file...",
        "btn_select_rom":    "Select ROM",
        "dumper_label":      "payload-dumper-go  Executable",
        "dumper_hint":       "If it's in PATH, leave the default value",
        "dumper_placeholder":"payload-dumper-go",
        "btn_select_exe":    "Select Executable",
        "sec_step2":         "STEP 2 — EXTRACT PAYLOAD",
        "partitions_label":  "Partitions:",
        "btn_extract":       "🗜  Start Extraction",
        "extract_start_msg": "Select a ROM to begin.",
        "sec_step3":         "STEP 3 — FLASH PARTITIONS",
        "flash_info":        "Commands below will be generated automatically after extraction.",
        "btn_reboot_fb":     "🔄  Reboot Fastboot",
        "btn_flash_now":     "⚡  Flash Now",
        "btn_reboot_rec":    "↩  Reboot Recovery",
        "btn_cleanup":       "🗑  Clean Files",
        "btn_flash_rom":     "📲  FLASH ROM",
        "sideload_title":    "⚠  Warning — Before continuing",
        "sideload_bold":     "<b>Prepare your device before continuing!</b>",
        "sideload_body":     ("1. Make sure the device is in <b>Recovery</b> mode.<br>"
                              "2. In recovery, go to:<br>"
                              "&nbsp;&nbsp;&nbsp;<b>Apply update → Apply from ADB</b><br>"
                              "&nbsp;&nbsp;&nbsp;(or <b>Update from ADB</b>, depending on recovery)<br>"
                              "3. Click <b>OK</b> when the device is waiting.<br><br>"),
        "btn_confirm_flash": "✓  Ready, start flash",
        "btn_cancel":        "Cancel",
        "sideload_notice":   ("⚠  On your phone, go to recovery and select:  "
                              "\"Apply update\" → \"Apply from ADB\" (or \"Update from ADB\").\n"
                              "   Wait for transfer to complete. Do not disconnect the cable."),
        "tab_hyperos":       "Flash HyperOS",
        "tab_hyperos_sub":   "Extraction and flash via official scripts",
        "sec_hyper_step1":   "STEP 1 — SELECT HYPEROS ROM (.zip)",
        "hyper_placeholder": "Select the HyperOS ROM .zip file...",
        "sec_hyper_step2":   "STEP 2 — EXTRACT AND SELECT INSTALL SCRIPT",
        "btn_hyper_extract": "🗜  Extract ROM",
        "hyper_start_msg":   "Select a HyperOS ROM to begin.",
        "sec_hyper_step3":   "STEP 3 — CHOOSE FLASH SCRIPT",
        "scripts_hint":      ("Click a script to select it.  "
                              "Tip: 'update' scripts install as OTA, 'clean' scripts wipe data."),
        "sec_hyper_step4":   "STEP 4 — RUN FLASH",
        "no_script":         "No script selected.",
        "btn_run_script":    "⚡  Run Script",
    },

    "es": {
        "nav_sistema":       "🖥  Sistema",
        "nav_apps":          "📦  Apps",
        "nav_adb":           "⌨  ADB Shell",
        "nav_fastboot":      "⚡  Fastboot",
        "nav_aosp":          "🗜  Flash AOSP",
        "nav_hyperos":       "🔥  Flash HyperOS",
        "donate":            "☕  Invítame un café",
        "dev_by":            "desarrollado por @alysonsb",
        "tab_sistema":       "Sistema",
        "tab_sistema_sub":   "Información del dispositivo",
        "sec_device":        "DISPOSITIVO",
        "card_modelo":       "Modelo",
        "card_android":      "Android",
        "card_serial":       "Serial",
        "card_imei":         "IMEI",
        "card_ram":          "RAM",
        "card_storage":      "Almacenamiento",
        "card_battery":      "Batería",
        "card_health":       "Salud",
        "btn_refresh":       "↻  Actualizar Datos",
        "health_unknown":    "Desconocida",
        "health_good":       "Buena ✓",
        "health_overheat":   "Sobrecalentando",
        "health_dead":       "Muerta",
        "health_over_volt":  "Sobretensión",
        "health_failure":    "Falla",
        "health_cold":       "Fría",
        "restricted":        "Restringido",
        "tab_apps":          "Aplicaciones",
        "tab_apps_sub":      "Paquetes instalados",
        "sec_install_apk":   "INSTALAR APK DESDE PC",
        "apk_placeholder":   "Seleccione un archivo .apk...",
        "btn_browse":        "📂  Explorar",
        "btn_install":       "📲  Instalar en Dispositivo",
        "installing":        "⏳  Instalando...",
        "install_ok":        "✓  ¡Instalado con éxito!",
        "sec_packages":      "PAQUETES DE TERCEROS",
        "btn_load_apps":     "↻  Cargar Apps",
        "packages_found":    "{n} paquetes encontrados",
        "menu_open":         "🚀  Abrir App",
        "menu_backup":       "💾  Backup APK",
        "menu_clear":        "🗑  Limpiar Datos",
        "menu_uninstall":    "❌  Desinstalar",
        "tab_adb":           "ADB Shell",
        "tab_adb_sub":       "Ejecutar comandos ADB",
        "sec_command":       "COMANDO",
        "adb_placeholder":   "shell getprop ro.product.model",
        "btn_run":           "Ejecutar",
        "btn_clear":         "Limpiar",
        "sec_output":        "SALIDA",
        "tab_fastboot":      "Fastboot",
        "tab_fastboot_sub":  "Flash y bootloader",
        "fb_placeholder":    "flash boot boot.img",
        "sec_quick":         "ACCIONES RÁPIDAS",
        "btn_devices":       "Devices",
        "btn_reboot":        "Reboot",
        "btn_bootloader":    "Bootloader",
        "btn_recovery_warn": "⚠  Reboot Recovery",
        "tab_aosp":          "Flash AOSP",
        "tab_aosp_sub":      "Extracción de payload.bin y flash de particiones",
        "sec_step1":         "PASO 1 — SELECCIONAR ROM (.zip)",
        "rom_placeholder":   "Seleccione el archivo .zip de la ROM...",
        "btn_select_rom":    "Seleccionar ROM",
        "dumper_label":      "Ejecutable  payload-dumper-go",
        "dumper_hint":       "Si está en PATH, deje el valor predeterminado",
        "dumper_placeholder":"payload-dumper-go",
        "btn_select_exe":    "Seleccionar Ejecutable",
        "sec_step2":         "PASO 2 — EXTRAER PAYLOAD",
        "partitions_label":  "Particiones:",
        "btn_extract":       "🗜  Iniciar Extracción",
        "extract_start_msg": "Seleccione una ROM para comenzar.",
        "sec_step3":         "PASO 3 — FLASH DE PARTICIONES",
        "flash_info":        "Los comandos se generarán automáticamente tras la extracción.",
        "btn_reboot_fb":     "🔄  Reboot Fastboot",
        "btn_flash_now":     "⚡  Hacer Flash Ahora",
        "btn_reboot_rec":    "↩  Reboot Recovery",
        "btn_cleanup":       "🗑  Limpiar Archivos",
        "btn_flash_rom":     "📲  FLASH ROM",
        "sideload_title":    "⚠  Atención — Antes de continuar",
        "sideload_bold":     "<b>¡Prepare el dispositivo antes de continuar!</b>",
        "sideload_body":     ("1. Asegúrese de que el dispositivo esté en <b>Recovery</b>.<br>"
                              "2. En recovery, acceda a:<br>"
                              "&nbsp;&nbsp;&nbsp;<b>Apply update → Apply from ADB</b><br>"
                              "&nbsp;&nbsp;&nbsp;(o <b>Update from ADB</b>, según el recovery)<br>"
                              "3. Haga clic en <b>OK</b> cuando el dispositivo esté esperando.<br><br>"),
        "btn_confirm_flash": "✓  Listo, iniciar flash",
        "btn_cancel":        "Cancelar",
        "sideload_notice":   ("⚠  En el celular, acceda al recovery y seleccione:  "
                              "\"Apply update\" → \"Apply from ADB\" (o \"Update from ADB\").\n"
                              "   Espere a que finalice la transferencia. No desconecte el cable."),
        "tab_hyperos":       "Flash HyperOS",
        "tab_hyperos_sub":   "Extracción y flash mediante scripts oficiales",
        "sec_hyper_step1":   "PASO 1 — SELECCIONAR ROM HYPEROS (.zip)",
        "hyper_placeholder": "Seleccione el archivo .zip de la ROM HyperOS...",
        "sec_hyper_step2":   "PASO 2 — EXTRAER Y SELECCIONAR SCRIPT DE INSTALACIÓN",
        "btn_hyper_extract": "🗜  Extraer ROM",
        "hyper_start_msg":   "Seleccione una ROM HyperOS para comenzar.",
        "sec_hyper_step3":   "PASO 3 — ELEGIR SCRIPT DE FLASH",
        "scripts_hint":      ("Haga clic en un script para seleccionarlo.  "
                              "Consejo: 'update' instala como OTA, 'clean' borra datos."),
        "sec_hyper_step4":   "PASO 4 — EJECUTAR FLASH",
        "no_script":         "Ningún script seleccionado.",
        "btn_run_script":    "⚡  Ejecutar Script",
    },

    "ru": {
        "nav_sistema":       "🖥  Система",
        "nav_apps":          "📦  Приложения",
        "nav_adb":           "⌨  ADB Shell",
        "nav_fastboot":      "⚡  Fastboot",
        "nav_aosp":          "🗜  Flash AOSP",
        "nav_hyperos":       "🔥  Flash HyperOS",
        "donate":            "☕  Угостить кофе",
        "dev_by":            "разработано @alysonsb",
        "tab_sistema":       "Система",
        "tab_sistema_sub":   "Информация об устройстве",
        "sec_device":        "УСТРОЙСТВО",
        "card_modelo":       "Модель",
        "card_android":      "Android",
        "card_serial":       "Серийный номер",
        "card_imei":         "IMEI",
        "card_ram":          "ОЗУ",
        "card_storage":      "Хранилище",
        "card_battery":      "Батарея",
        "card_health":       "Состояние",
        "btn_refresh":       "↻  Обновить данные",
        "health_unknown":    "Неизвестно",
        "health_good":       "Хорошее ✓",
        "health_overheat":   "Перегрев",
        "health_dead":       "Мёртвая",
        "health_over_volt":  "Перенапряжение",
        "health_failure":    "Сбой",
        "health_cold":       "Холодная",
        "restricted":        "Ограничено",
        "tab_apps":          "Приложения",
        "tab_apps_sub":      "Установленные пакеты",
        "sec_install_apk":   "УСТАНОВИТЬ APK С ПК",
        "apk_placeholder":   "Выберите файл .apk...",
        "btn_browse":        "📂  Обзор",
        "btn_install":       "📲  Установить на устройство",
        "installing":        "⏳  Установка...",
        "install_ok":        "✓  Успешно установлено!",
        "sec_packages":      "СТОРОННИЕ ПАКЕТЫ",
        "btn_load_apps":     "↻  Загрузить приложения",
        "packages_found":    "{n} пакетов найдено",
        "menu_open":         "🚀  Открыть приложение",
        "menu_backup":       "💾  Резервная копия APK",
        "menu_clear":        "🗑  Очистить данные",
        "menu_uninstall":    "❌  Удалить",
        "tab_adb":           "ADB Shell",
        "tab_adb_sub":       "Выполнить команды ADB",
        "sec_command":       "КОМАНДА",
        "adb_placeholder":   "shell getprop ro.product.model",
        "btn_run":           "Выполнить",
        "btn_clear":         "Очистить",
        "sec_output":        "ВЫВОД",
        "tab_fastboot":      "Fastboot",
        "tab_fastboot_sub":  "Прошивка и загрузчик",
        "fb_placeholder":    "flash boot boot.img",
        "sec_quick":         "БЫСТРЫЕ ДЕЙСТВИЯ",
        "btn_devices":       "Устройства",
        "btn_reboot":        "Перезагрузка",
        "btn_bootloader":    "Загрузчик",
        "btn_recovery_warn": "⚠  Reboot Recovery",
        "tab_aosp":          "Flash AOSP",
        "tab_aosp_sub":      "Извлечение payload.bin и прошивка разделов",
        "sec_step1":         "ШАГ 1 — ВЫБРАТЬ ROM (.zip)",
        "rom_placeholder":   "Выберите файл .zip с ROM...",
        "btn_select_rom":    "Выбрать ROM",
        "dumper_label":      "Исполняемый файл  payload-dumper-go",
        "dumper_hint":       "Если в PATH, оставьте значение по умолчанию",
        "dumper_placeholder":"payload-dumper-go",
        "btn_select_exe":    "Выбрать исполняемый файл",
        "sec_step2":         "ШАГ 2 — ИЗВЛЕЧЬ PAYLOAD",
        "partitions_label":  "Разделы:",
        "btn_extract":       "🗜  Начать извлечение",
        "extract_start_msg": "Выберите ROM для начала.",
        "sec_step3":         "ШАГ 3 — ПРОШИВКА РАЗДЕЛОВ",
        "flash_info":        "Команды будут созданы автоматически после извлечения.",
        "btn_reboot_fb":     "🔄  Reboot Fastboot",
        "btn_flash_now":     "⚡  Прошить сейчас",
        "btn_reboot_rec":    "↩  Reboot Recovery",
        "btn_cleanup":       "🗑  Удалить файлы",
        "btn_flash_rom":     "📲  FLASH ROM",
        "sideload_title":    "⚠  Внимание — Перед продолжением",
        "sideload_bold":     "<b>Подготовьте устройство перед продолжением!</b>",
        "sideload_body":     ("1. Убедитесь, что устройство находится в режиме <b>Recovery</b>.<br>"
                              "2. В recovery выберите:<br>"
                              "&nbsp;&nbsp;&nbsp;<b>Apply update → Apply from ADB</b><br>"
                              "&nbsp;&nbsp;&nbsp;(или <b>Update from ADB</b>, в зависимости от recovery)<br>"
                              "3. Нажмите <b>OK</b>, когда устройство будет ожидать.<br><br>"),
        "btn_confirm_flash": "✓  Готов, начать прошивку",
        "btn_cancel":        "Отмена",
        "sideload_notice":   ("⚠  На телефоне откройте recovery и выберите:  "
                              "\"Apply update\" → \"Apply from ADB\" (или \"Update from ADB\").\n"
                              "   Дождитесь завершения передачи. Не отключайте кабель."),
        "tab_hyperos":       "Flash HyperOS",
        "tab_hyperos_sub":   "Извлечение и прошивка через официальные скрипты",
        "sec_hyper_step1":   "ШАГ 1 — ВЫБРАТЬ ROM HYPEROS (.zip)",
        "hyper_placeholder": "Выберите файл .zip ROM HyperOS...",
        "sec_hyper_step2":   "ШАГ 2 — ИЗВЛЕЧЬ И ВЫБРАТЬ СКРИПТ УСТАНОВКИ",
        "btn_hyper_extract": "🗜  Извлечь ROM",
        "hyper_start_msg":   "Выберите ROM HyperOS для начала.",
        "sec_hyper_step3":   "ШАГ 3 — ВЫБРАТЬ СКРИПТ ПРОШИВКИ",
        "scripts_hint":      ("Нажмите на скрипт для выбора.  "
                              "Совет: 'update' — OTA без сброса, 'clean' — полный сброс данных."),
        "sec_hyper_step4":   "ШАГ 4 — ВЫПОЛНИТЬ ПРОШИВКУ",
        "no_script":         "Скрипт не выбран.",
        "btn_run_script":    "⚡  Запустить скрипт",
    },
}

def tr(lang, key, **kwargs):
    text = TRANSLATIONS.get(lang, TRANSLATIONS["pt"]).get(key, key)
    return text.format(**kwargs) if kwargs else text




# ===============================
# UTIL
# ===============================
def run_command(command):
    try:
        result = subprocess.check_output(command, shell=True, stderr=subprocess.STDOUT)
        return result.decode(errors="ignore")
    except subprocess.CalledProcessError as e:
        return e.output.decode(errors="ignore")


def round_ram_gb(kb):
    """Arredonda RAM para o valor comercial mais próximo (potência de 2 ou múltiplo comum)."""
    gb_exact = kb / 1024 / 1024
    # Valores comerciais comuns de RAM
    commercial = [1, 2, 3, 4, 6, 8, 10, 12, 16, 24, 32, 48, 64]
    closest = min(commercial, key=lambda x: abs(x - gb_exact))
    return f"{closest} GB"


def battery_health_text(code, lang="pt"):
    key_map = {
        "1": "health_unknown",
        "2": "health_good",
        "3": "health_overheat",
        "4": "health_dead",
        "5": "health_over_volt",
        "6": "health_failure",
        "7": "health_cold",
    }
    key = key_map.get(code, "health_unknown")
    return tr(lang, key)


# ===============================
# THREAD FASTBOOT
# ===============================
class FastbootThread(QThread):
    output_signal = Signal(str)

    def __init__(self, command):
        super().__init__()
        self.command = command

    def run(self):
        try:
            process = subprocess.Popen(
                self.command,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT
            )
            for line in iter(process.stdout.readline, b''):
                if not line:
                    break
                self.output_signal.emit(line.decode(errors="ignore").rstrip())
            process.wait()
        except Exception as e:
            self.output_signal.emit(f"Erro: {e}")
        self.output_signal.emit("\n─── Finalizado ───")


# ===============================
# THREAD: EXTRAÇÃO DE ROM
# ===============================
class RomExtractThread(QThread):
    log_signal  = Signal(str)
    done_signal = Signal(dict, str)   # (found_files, error)

    def __init__(self, command, out_dir, partitions):
        super().__init__()
        self.command    = command
        self.out_dir    = out_dir
        self.partitions = partitions

    def run(self):
        import os
        try:
            process = subprocess.Popen(
                self.command,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT
            )
            for line in iter(process.stdout.readline, b''):
                if not line:
                    break
                self.log_signal.emit(line.decode(errors="ignore").rstrip())
            process.wait()

            if process.returncode not in (0, None):
                self.done_signal.emit({}, f"payload-dumper-go retornou código {process.returncode}")
                return

            # Procura os .img extraídos
            found = {}
            for f in os.listdir(self.out_dir):
                name, ext = os.path.splitext(f)
                if ext == ".img":
                    found[name] = os.path.join(self.out_dir, f)

            self.done_signal.emit(found, "")

        except FileNotFoundError:
            self.done_signal.emit(
                {},
                "payload-dumper-go não encontrado. Verifique o caminho ou instale-o."
            )
        except Exception as e:
            self.done_signal.emit({}, str(e))


# ===============================
# THREAD: FLASH SEQUENCIAL
# ===============================
class SequentialFastbootThread(QThread):
    log_signal  = Signal(str)
    done_signal = Signal(bool)   # True = sucesso

    def __init__(self, commands):
        super().__init__()
        self.commands = commands

    def run(self):
        success = True
        for cmd in self.commands:
            self.log_signal.emit(f"\n$ {cmd}")
            try:
                process = subprocess.Popen(
                    cmd,
                    shell=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT
                )
                for line in iter(process.stdout.readline, b''):
                    if not line:
                        break
                    decoded = line.decode(errors="ignore").rstrip()
                    self.log_signal.emit(decoded)
                process.wait()

                if process.returncode != 0:
                    self.log_signal.emit(f"✗  Erro no comando (código {process.returncode})")
                    success = False
                    break
                else:
                    self.log_signal.emit("✓  OK")

            except Exception as e:
                self.log_signal.emit(f"✗  Exceção: {e}")
                success = False
                break

        self.done_signal.emit(success)



class InfoCard(QFrame):
    def __init__(self, title, icon=""):
        super().__init__()
        self.setObjectName("InfoCard")
        self.setMinimumHeight(100)

        layout = QVBoxLayout()
        layout.setContentsMargins(18, 16, 18, 16)
        layout.setSpacing(6)

        header = QHBoxLayout()
        if icon:
            icon_label = QLabel(icon)
            icon_label.setObjectName("cardIcon")
            header.addWidget(icon_label)

        title_label = QLabel(title.upper())
        title_label.setObjectName("cardTitle")
        header.addWidget(title_label)
        header.addStretch()

        self.value = QLabel("—")
        self.value.setObjectName("cardValue")
        self.value.setWordWrap(True)

        layout.addLayout(header)
        layout.addWidget(self.value)
        layout.addStretch()
        self.setLayout(layout)

        # Drop shadow
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setOffset(0, 4)
        shadow.setColor(QColor(0, 0, 0, 80))
        self.setGraphicsEffect(shadow)


# ===============================
# TERMINAL-STYLE OUTPUT
# ===============================
class TerminalOutput(QTextEdit):
    def __init__(self, placeholder=""):
        super().__init__()
        self.setReadOnly(True)
        self.setObjectName("TerminalOutput")
        if placeholder:
            self.setPlaceholderText(placeholder)

    def append_line(self, text):
        self.append(text.rstrip())
        self.verticalScrollBar().setValue(self.verticalScrollBar().maximum())


# ===============================
# SECTION HEADER
# ===============================
class SectionHeader(QLabel):
    def __init__(self, text):
        super().__init__(text)
        self.setObjectName("SectionHeader")


# ===============================
# MAIN WINDOW
# ===============================
class RomManager(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ROM Manager Pro")
        self.resize(1240, 780)
        self.setMinimumSize(900, 600)

        self._lang = "pt"

        # Central container
        central = QWidget()
        self.setCentralWidget(central)

        root = QHBoxLayout()
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # Sidebar
        sidebar = self._build_sidebar()
        root.addWidget(sidebar)

        # Content area with tabs (hidden tab bar)
        self.tabs = QTabWidget()
        self.tabs.setObjectName("MainTabs")
        self.tabs.tabBar().hide()
        root.addWidget(self.tabs, 1)

        central.setLayout(root)

        self.create_system_tab()
        self.create_apps_tab()
        self.create_adb_tab()
        self.create_fastboot_tab()
        self.create_rom_tab()
        self.create_hyperos_tab()

        self.apply_style()
        self._sidebar_buttons[0].setProperty("active", True)
        self._sidebar_buttons[0].style().unpolish(self._sidebar_buttons[0])
        self._sidebar_buttons[0].style().polish(self._sidebar_buttons[0])

    # ── Sidebar ──────────────────────────────────────────────
    def _build_sidebar(self):
        sidebar = QFrame()
        sidebar.setObjectName("Sidebar")
        sidebar.setFixedWidth(260)

        layout = QVBoxLayout()
        layout.setContentsMargins(14, 28, 14, 28)
        layout.setSpacing(4)

        # Logo area
        logo = QLabel("⚡ ROM Manager")
        logo.setObjectName("SidebarLogo")
        logo.setWordWrap(True)
        layout.addWidget(logo)

        divider = QFrame()
        divider.setObjectName("Divider")
        divider.setFixedHeight(1)
        layout.addSpacing(16)
        layout.addWidget(divider)
        layout.addSpacing(16)

        self._sidebar_buttons = []
        nav_items = [
            ("🖥  Sistema",       0),
            ("📦  Apps",          1),
            ("⌨  ADB Shell",     2),
            ("⚡  Fastboot",      3),
            ("🗜  Flash AOSP",    4),
            ("🔥  Flash HyperOS", 5),
        ]

        for label, idx in nav_items:
            btn = QPushButton(label)
            btn.setObjectName("NavButton")
            btn.setCheckable(True)
            btn.clicked.connect(lambda checked, i=idx: self._switch_tab(i))
            layout.addWidget(btn)
            self._sidebar_buttons.append(btn)

        layout.addStretch()

        # ── Seletor de idioma ──
        lang_row = QHBoxLayout()
        lang_row.setSpacing(6)
        lang_row.setContentsMargins(2, 0, 2, 0)

        lang_icon = QLabel("🌐")
        lang_icon.setStyleSheet("font-size: 14px;")
        lang_icon.setFixedWidth(22)

        self.lang_combo = QComboBox()
        self.lang_combo.setObjectName("LangCombo")
        self.lang_combo.addItem("Português", "pt")
        self.lang_combo.addItem("English",   "en")
        self.lang_combo.addItem("Español",   "es")
        self.lang_combo.addItem("Русский",   "ru")
        self.lang_combo.currentIndexChanged.connect(self._on_lang_changed)

        lang_row.addWidget(lang_icon)
        lang_row.addWidget(self.lang_combo, 1)
        layout.addLayout(lang_row)
        layout.addSpacing(10)

        donate_btn = QPushButton(tr(self._lang, "donate"))
        donate_btn.setObjectName("DonateButton")
        donate_btn.setFixedHeight(38)
        donate_btn.setCursor(Qt.PointingHandCursor)
        donate_btn.clicked.connect(self._open_donation)
        self._donate_btn = donate_btn
        layout.addWidget(donate_btn)
        layout.addSpacing(8)

        version = QLabel("v1.0")
        version.setObjectName("VersionLabel")
        layout.addWidget(version)

        dev_label = QLabel(tr(self._lang, "dev_by"))
        dev_label.setObjectName("DevLabel")
        self._dev_label = dev_label
        layout.addWidget(dev_label)
        layout.addSpacing(6)

        # Ícones de GitHub e Telegram lado a lado
        # sidebar 260px - margins 14*2 = 232px úteis, split em 2 com 6px gap = 113px cada
        icons_row = QHBoxLayout()
        icons_row.setSpacing(6)
        icons_row.setContentsMargins(0, 0, 0, 0)

        github_btn = QPushButton("  GitHub")
        github_btn.setObjectName("IconLinkButton")
        github_btn.setCursor(Qt.PointingHandCursor)
        github_btn.setFixedHeight(30)
        github_btn.setFixedWidth(113)
        github_btn.setIcon(self._github_icon())
        github_btn.clicked.connect(self._open_github)

        telegram_btn = QPushButton("  Telegram")
        telegram_btn.setObjectName("IconLinkButton")
        telegram_btn.setCursor(Qt.PointingHandCursor)
        telegram_btn.setFixedHeight(30)
        telegram_btn.setFixedWidth(113)
        telegram_btn.setIcon(self._telegram_icon())
        telegram_btn.clicked.connect(self._open_telegram)

        icons_row.addWidget(github_btn)
        icons_row.addWidget(telegram_btn)
        layout.addLayout(icons_row)
        layout.addSpacing(4)

        sidebar.setLayout(layout)
        return sidebar

    def _switch_tab(self, index):
        self.tabs.setCurrentIndex(index)
        for i, btn in enumerate(self._sidebar_buttons):
            btn.setChecked(i == index)

    def _open_donation(self):
        import webbrowser
        webbrowser.open("https://www.paypal.com/donate")

    def _open_github(self):
        import webbrowser
        webbrowser.open("https://github.com/alysonsb/RomManagerPro-")

    def _open_telegram(self):
        import webbrowser
        webbrowser.open("https://t.me/romManagerPro")

    def _on_lang_changed(self, index):
        self._lang = self.lang_combo.itemData(index)
        self._rebuild_all_tabs()

    def _rebuild_all_tabs(self):
        """Remove e recria todas as abas com o novo idioma."""
        # Salva estado que o usuário pode ter preenchido
        saved = {
            "rom_path":      getattr(self, "rom_path_input",    None) and self.rom_path_input.text(),
            "dumper_path":   getattr(self, "dumper_path_input", None) and self.dumper_path_input.text(),
            "partitions":    getattr(self, "partitions_input",  None) and self.partitions_input.text(),
            "hyper_rom":     getattr(self, "hyper_rom_input",   None) and self.hyper_rom_input.text(),
            "adb_cmd":       getattr(self, "adb_input",         None) and self.adb_input.text(),
            "fastboot_cmd":  getattr(self, "fastboot_input",    None) and self.fastboot_input.text(),
        }

        # Remove todas as abas
        while self.tabs.count():
            widget = self.tabs.widget(0)
            self.tabs.removeTab(0)
            if widget:
                widget.deleteLater()

        # Reset listas de referências
        self._tab_title_labels = []
        self._tab_sub_labels   = []
        self._sec_headers      = {}

        # Recria tudo
        self.create_system_tab()
        self.create_apps_tab()
        self.create_adb_tab()
        self.create_fastboot_tab()
        self.create_rom_tab()
        self.create_hyperos_tab()

        # Restaura botões da sidebar com novo texto
        L = self._lang
        nav_keys = ["nav_sistema","nav_apps","nav_adb","nav_fastboot","nav_aosp","nav_hyperos"]
        for btn, key in zip(self._sidebar_buttons, nav_keys):
            btn.setText(tr(L, key))
        self._donate_btn.setText(tr(L, "donate"))
        self._dev_label.setText(tr(L, "dev_by"))

        # Restaura valores salvos
        if saved["rom_path"]    and self.rom_path_input:
            self.rom_path_input.setText(saved["rom_path"])
            self.extract_btn.setEnabled(bool(saved["rom_path"]))
        if saved["dumper_path"] and self.dumper_path_input:
            self.dumper_path_input.setText(saved["dumper_path"])
        if saved["partitions"]  and self.partitions_input:
            self.partitions_input.setText(saved["partitions"])
        if saved["hyper_rom"]   and self.hyper_rom_input:
            self.hyper_rom_input.setText(saved["hyper_rom"])
            self.hyper_extract_btn.setEnabled(bool(saved["hyper_rom"]))
        if saved["adb_cmd"]     and self.adb_input:
            self.adb_input.setText(saved["adb_cmd"])
        if saved["fastboot_cmd"] and self.fastboot_input:
            self.fastboot_input.setText(saved["fastboot_cmd"])

        # Volta para a aba que estava ativa
        self.tabs.setCurrentIndex(
            next((i for i, b in enumerate(self._sidebar_buttons) if b.isChecked()), 0)
        )



    def _github_icon(self):
        try:
            from PySide6.QtGui import QPixmap, QPainter
            from PySide6.QtSvg import QSvgRenderer
            from PySide6.QtCore import QByteArray
            svg = b"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="#9CA3AF">
              <path d="M12 0C5.37 0 0 5.37 0 12c0 5.31 3.435 9.795 8.205 11.385.6.105.825-.255.825-.57
              0-.285-.015-1.23-.015-2.235-3.015.555-3.795-.735-4.035-1.41-.135-.345-.72-1.41-1.23-1.695
              -.42-.225-1.02-.78-.015-.795.945-.015 1.62.87 1.845 1.23 1.08 1.815 2.805 1.305 3.495.99
              .105-.78.42-1.305.765-1.605-2.67-.3-5.46-1.335-5.46-5.925 0-1.305.465-2.385 1.23-3.225
              -.12-.3-.54-1.53.12-3.18 0 0 1.005-.315 3.3 1.23.96-.27 1.98-.405 3-.405s2.04.135 3 .405
              c2.295-1.56 3.3-1.23 3.3-1.23.66 1.65.24 2.88.12 3.18.765.84 1.23 1.905 1.23 3.225
              0 4.605-2.805 5.625-5.475 5.925.435.375.81 1.095.81 2.22 0 1.605-.015 2.895-.015 3.3
              0 .315.225.69.825.57A12.02 12.02 0 0 0 24 12c0-6.63-5.37-12-12-12z"/>
            </svg>"""
            renderer = QSvgRenderer(QByteArray(svg))
            pixmap = QPixmap(18, 18)
            pixmap.fill(Qt.transparent)
            painter = QPainter(pixmap)
            renderer.render(painter)
            painter.end()
            return QIcon(pixmap)
        except Exception:
            return QIcon()

    def _telegram_icon(self):
        try:
            from PySide6.QtGui import QPixmap, QPainter
            from PySide6.QtSvg import QSvgRenderer
            from PySide6.QtCore import QByteArray
            svg = b"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="#9CA3AF">
              <path d="M12 0C5.373 0 0 5.373 0 12s5.373 12 12 12 12-5.373 12-12S18.627 0 12 0zm5.894
              8.221-1.97 9.28c-.145.658-.537.818-1.084.508l-3-2.21-1.447 1.394c-.16.16-.295.295-.605.295
              l.213-3.053 5.56-5.023c.242-.213-.054-.333-.373-.12L8.32 13.617l-2.96-.924c-.643-.204
              -.657-.643.136-.953l11.57-4.461c.537-.194 1.006.131.828.942z"/>
            </svg>"""
            renderer = QSvgRenderer(QByteArray(svg))
            pixmap = QPixmap(18, 18)
            pixmap.fill(Qt.transparent)
            painter = QPainter(pixmap)
            renderer.render(painter)
            painter.end()
            return QIcon(pixmap)
        except Exception:
            return QIcon()

    # ── Stylesheet ───────────────────────────────────────────
    def apply_style(self):
        self.setStyleSheet("""
        /* ── Base ── */
        * { font-family: 'Consolas', 'Courier New', monospace; }

        QWidget {
            background-color: #0C0E12;
            color: #D8DEE9;
            font-size: 13px;
        }

        /* ── Sidebar ── */
        QFrame#Sidebar {
            background-color: #111318;
            border-right: 1px solid #1E2028;
        }

        QLabel#SidebarLogo {
            font-size: 16px;
            font-weight: bold;
            color: #7EB8F7;
            letter-spacing: 1px;
            padding: 4px 0;
        }

        QFrame#Divider {
            background-color: #1E2028;
            border: none;
        }

        /* ── Language Combo ── */
        QComboBox#LangCombo {
            background-color: #1A1D25;
            border: 1px solid #252933;
            border-radius: 7px;
            padding: 5px 8px;
            color: #9CA3AF;
            font-size: 12px;
        }

        QComboBox#LangCombo:hover {
            border-color: #3B4460;
            color: #D8DEE9;
        }

        QComboBox#LangCombo::drop-down {
            border: none;
            width: 20px;
        }

        QComboBox#LangCombo QAbstractItemView {
            background-color: #151820;
            border: 1px solid #252933;
            color: #9CA3AF;
            selection-background-color: #1C2333;
            selection-color: #7EB8F7;
            padding: 4px;
        }

        QPushButton#NavButton {
            background: transparent;
            border: none;
            border-radius: 8px;
            padding: 11px 14px;
            text-align: left;
            color: #6B7280;
            font-size: 15px;
        }

        QPushButton#NavButton:hover {
            background-color: #1A1D25;
            color: #D8DEE9;
        }

        QPushButton#NavButton:checked {
            background-color: #1C2333;
            color: #7EB8F7;
            border-left: 3px solid #7EB8F7;
        }

        QLabel#VersionLabel {
            font-size: 13px;
            font-weight: bold;
            color: #FFFFFF;
            padding: 0 2px;
        }

        QLabel#DevLabel {
            font-size: 11px;
            color: #4B5563;
            padding: 0 2px;
        }

        QPushButton#IconLinkButton {
            background: transparent;
            border: 1px solid #1E2028;
            border-radius: 7px;
            color: #6B7280;
            font-size: 11px;
            padding: 0 8px;
            text-align: left;
        }

        QPushButton#IconLinkButton:hover {
            background-color: #1A1D25;
            border-color: #2A3145;
            color: #D8DEE9;
        }

        QPushButton#DonateButton {
            background-color: #1A1400;
            border: 1px solid #5C4A00;
            border-radius: 8px;
            color: #F59E0B;
            font-size: 13px;
            font-weight: bold;
        }

        QPushButton#DonateButton:hover {
            background-color: #241C00;
            border-color: #92700A;
            color: #FCD34D;
        }

        QPushButton#DonateButton:pressed {
            background-color: #120F00;
        }

        /* ── Tabs Content ── */
        QTabWidget#MainTabs {
            border: none;
        }
        QTabWidget#MainTabs::pane {
            border: none;
            background-color: #0C0E12;
        }

        /* ── Install / Flash Frames ── */
        QFrame#InstallFrame, QFrame#FlashFrame {
            background-color: #111318;
            border: 1px solid #1E2028;
            border-radius: 10px;
        }

        QFrame#FlashFrame {
            border-color: #2A1E0A;
        }

        /* ── Cards ── */
        QFrame#InfoCard {
            background-color: #111318;
            border: 1px solid #1E2028;
            border-radius: 12px;
        }

        QFrame#InfoCard:hover {
            border: 1px solid #2A3145;
        }

        QLabel#cardIcon {
            font-size: 16px;
        }

        QLabel#cardTitle {
            font-size: 10px;
            color: #4B5563;
            letter-spacing: 1.5px;
        }

        QLabel#cardValue {
            font-size: 18px;
            font-weight: bold;
            color: #E2E8F0;
        }

        /* ── Section Headers ── */
        QLabel#SectionHeader {
            font-size: 11px;
            color: #4B5563;
            letter-spacing: 2px;
            padding: 0 4px;
        }

        /* ── Buttons ── */
        QPushButton {
            background-color: #1A1D25;
            border: 1px solid #252933;
            border-radius: 8px;
            padding: 9px 20px;
            color: #9CA3AF;
            font-size: 12px;
        }

        QPushButton:hover {
            background-color: #1E2330;
            border-color: #3B4460;
            color: #D8DEE9;
        }

        QPushButton:pressed {
            background-color: #131823;
        }

        QPushButton#PrimaryButton {
            background-color: #1C2E4A;
            border: 1px solid #2B4778;
            color: #7EB8F7;
        }

        QPushButton#PrimaryButton:hover {
            background-color: #1F3457;
            border-color: #3B6BAA;
            color: #A8D0F8;
        }

        QPushButton#DangerButton {
            background-color: #2A1A1A;
            border: 1px solid #5C2222;
            color: #F87171;
        }

        QPushButton#DangerButton:hover {
            background-color: #341F1F;
            border-color: #7B3333;
        }

        QPushButton#SuccessButton {
            background-color: #0F2A1A;
            border: 1px solid #1A5C32;
            color: #4ADE80;
            font-weight: bold;
        }

        QPushButton#SuccessButton:hover {
            background-color: #153520;
            border-color: #22A355;
            color: #6EF0A0;
        }

        QPushButton#SuccessButton:pressed {
            background-color: #0C1F14;
        }

        QLabel#SideloadNotice {
            background-color: #0F1F14;
            border: 1px solid #1A5C32;
            border-radius: 8px;
            color: #4ADE80;
            font-size: 12px;
            padding: 10px 14px;
        }

        /* ── List ── */
        QListWidget {
            background-color: #111318;
            border: 1px solid #1E2028;
            border-radius: 10px;
            padding: 6px;
            outline: none;
        }

        QListWidget::item {
            padding: 8px 12px;
            border-radius: 6px;
            color: #9CA3AF;
        }

        QListWidget::item:hover {
            background-color: #1A1D25;
            color: #D8DEE9;
        }

        QListWidget::item:selected {
            background-color: #1C2333;
            color: #7EB8F7;
        }

        /* ── Terminal / Text ── */
        QTextEdit#TerminalOutput {
            background-color: #080A0D;
            border: 1px solid #1A1D24;
            border-radius: 10px;
            padding: 14px;
            color: #7EB8F7;
            font-family: 'Consolas', 'Courier New', monospace;
            font-size: 12px;
            line-height: 1.6;
        }

        QLineEdit {
            background-color: #111318;
            border: 1px solid #1E2028;
            border-radius: 8px;
            padding: 10px 14px;
            color: #D8DEE9;
            font-size: 13px;
            selection-background-color: #1C2E4A;
        }

        QLineEdit:focus {
            border-color: #2B4778;
            background-color: #131620;
        }

        QLineEdit::placeholder {
            color: #374151;
        }

        /* ── Scrollbars ── */
        QScrollBar:vertical {
            background: transparent;
            width: 6px;
            margin: 0;
        }
        QScrollBar::handle:vertical {
            background: #252933;
            border-radius: 3px;
            min-height: 30px;
        }
        QScrollBar::handle:vertical:hover { background: #374151; }
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }

        QScrollBar:horizontal {
            background: transparent;
            height: 6px;
        }
        QScrollBar::handle:horizontal {
            background: #252933;
            border-radius: 3px;
        }
        QScrollBar::handle:horizontal:hover { background: #374151; }
        QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal { width: 0; }

        /* ── Scripts List ── */
        QListWidget#ScriptsList::item {
            padding: 9px 12px;
            border-radius: 6px;
            color: #9CA3AF;
            border-bottom: 1px solid #1A1D25;
        }

        QListWidget#ScriptsList::item:hover {
            background-color: #1A1D25;
            color: #E879F9;
        }

        QListWidget#ScriptsList::item:selected {
            background-color: #2A1535;
            color: #E879F9;
            border-left: 3px solid #E879F9;
        }

        /* ── Context Menu ── */
        QMenu {
            background-color: #151820;
            border: 1px solid #252933;
            border-radius: 8px;
            padding: 4px;
        }
        QMenu::item {
            padding: 8px 18px;
            border-radius: 5px;
            color: #9CA3AF;
        }
        QMenu::item:selected {
            background-color: #1C2333;
            color: #7EB8F7;
        }
        QMenu::separator {
            height: 1px;
            background: #1E2028;
            margin: 4px 8px;
        }
        """)

    # ── Tab helpers ──────────────────────────────────────────
    def _tab_layout(self, title, subtitle=""):
        tab = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(28, 28, 28, 28)
        layout.setSpacing(20)

        header_row = QHBoxLayout()
        title_label = QLabel(title)
        title_label.setStyleSheet("font-size: 20px; font-weight: bold; color: #E2E8F0;")
        header_row.addWidget(title_label)
        header_row.addStretch()

        sub = QLabel(subtitle)
        sub.setStyleSheet("font-size: 12px; color: #374151;")
        if subtitle:
            header_row.addWidget(sub)

        layout.addLayout(header_row)

        # Store refs for retranslation
        if not hasattr(self, '_tab_title_labels'):
            self._tab_title_labels = []
            self._tab_sub_labels   = []
            self._sec_headers      = {}
        self._tab_title_labels.append(title_label)
        self._tab_sub_labels.append(sub)

        return tab, layout

    def _sec(self, key):
        """Create a SectionHeader and store it by key for retranslation."""
        header = SectionHeader(tr(self._lang, key))
        self._sec_headers[key] = header
        return header

    # ── Sistema ──────────────────────────────────────────────
    def create_system_tab(self):
        L = self._lang
        tab, layout = self._tab_layout(tr(L,"tab_sistema"), tr(L,"tab_sistema_sub"))

        layout.addWidget(self._sec("sec_device"))

        grid = QGridLayout()
        grid.setSpacing(14)

        card_defs = [
            ("card_modelo",   "🖥"),
            ("card_android",  "🤖"),
            ("card_serial",   "🔑"),
            ("card_imei",     "📡"),
            ("card_ram",      "💾"),
            ("card_storage",  "🗄"),
            ("card_battery",  "🔋"),
            ("card_health",   "❤"),
        ]

        # cards keyed by PT name for stable access
        self.cards = {}
        row = col = 0
        for key, icon in card_defs:
            pt_name = tr("pt", key)
            card = InfoCard(tr(L, key), icon)
            self.cards[pt_name] = card
            grid.addWidget(card, row, col)
            col += 1
            if col == 3:
                col = 0
                row += 1

        layout.addLayout(grid)

        btn_row = QHBoxLayout()
        refresh = QPushButton(tr(L, "btn_refresh"))
        refresh.setObjectName("PrimaryButton")
        refresh.setFixedWidth(180)
        refresh.clicked.connect(self.load_device_info)
        self._refresh_btn = refresh
        btn_row.addWidget(refresh)
        btn_row.addStretch()
        layout.addLayout(btn_row)
        layout.addStretch()

        tab.setLayout(layout)
        self.tabs.addTab(tab, "Sistema")

    def load_device_info(self):
        model   = run_command("adb shell getprop ro.product.model").strip() or "—"
        android = run_command("adb shell getprop ro.build.version.release").strip() or "—"
        serial  = run_command("adb get-serialno").strip() or "—"

        imei = run_command("adb shell getprop persist.radio.imei").strip()
        if not imei:
            imei = tr(self._lang, "restricted")

        # RAM com arredondamento para valor comercial
        meminfo   = run_command("adb shell cat /proc/meminfo")
        ram_match = re.search(r'MemTotal:\s+(\d+)', meminfo)
        ram = round_ram_gb(int(ram_match.group(1))) if ram_match else "—"

        # Armazenamento interno total
        df_output = run_command("adb shell df /data")
        storage = "—"
        for line in df_output.splitlines():
            parts = line.split()
            if len(parts) >= 2 and parts[0] not in ("Filesystem", "tmpfs"):
                try:
                    total_kb = int(parts[1])
                    gb_exact = total_kb / 1024 / 1024
                    commercial = [8, 16, 32, 64, 128, 256, 512, 1024]
                    closest = min(commercial, key=lambda x: abs(x - gb_exact))
                    storage = f"{closest} GB"
                    break
                except (ValueError, IndexError):
                    continue

        battery = run_command("adb shell dumpsys battery")
        level   = re.search(r'level: (\d+)', battery)
        health  = re.search(r'health: (\d+)', battery)

        battery_level = level.group(1) + "%" if level else "—"
        health_text   = battery_health_text(health.group(1), self._lang) if health else "—"

        values = [model, android, serial, imei, ram, storage, battery_level, health_text]
        for key, value in zip(self.cards.keys(), values):
            self.cards[key].value.setText(value)

    # ── Apps ─────────────────────────────────────────────────
    def create_apps_tab(self):
        L = self._lang
        tab, layout = self._tab_layout(tr(L,"tab_apps"), tr(L,"tab_apps_sub"))

        layout.addWidget(self._sec("sec_install_apk"))

        install_frame = QFrame()
        install_frame.setObjectName("InstallFrame")
        install_layout = QVBoxLayout()
        install_layout.setContentsMargins(16, 14, 16, 14)
        install_layout.setSpacing(10)

        file_row = QHBoxLayout()
        self.apk_path_input = QLineEdit()
        self.apk_path_input.setPlaceholderText(tr(L,"apk_placeholder"))
        self.apk_path_input.setReadOnly(True)

        browse_btn = QPushButton(tr(L,"btn_browse"))
        browse_btn.setFixedWidth(120)
        browse_btn.clicked.connect(self._browse_apk)
        self._browse_apk_btn = browse_btn

        file_row.addWidget(self.apk_path_input, 1)
        file_row.addWidget(browse_btn)
        install_layout.addLayout(file_row)

        action_row = QHBoxLayout()
        self.install_btn = QPushButton(tr(L,"btn_install"))
        self.install_btn.setObjectName("PrimaryButton")
        self.install_btn.setFixedWidth(240)
        self.install_btn.setEnabled(False)
        self.install_btn.clicked.connect(self._install_apk)

        self.install_status = QLabel("")
        self.install_status.setStyleSheet("font-size: 12px; color: #374151;")

        action_row.addWidget(self.install_btn)
        action_row.addWidget(self.install_status)
        action_row.addStretch()
        install_layout.addLayout(action_row)

        install_frame.setLayout(install_layout)
        layout.addWidget(install_frame)

        layout.addWidget(self._sec("sec_packages"))

        self.apps_list = QListWidget()
        self.apps_list.setContextMenuPolicy(Qt.CustomContextMenu)
        self.apps_list.customContextMenuRequested.connect(self.app_menu)

        btn_row = QHBoxLayout()
        load_btn = QPushButton(tr(L,"btn_load_apps"))
        load_btn.setObjectName("PrimaryButton")
        load_btn.setFixedWidth(160)
        load_btn.clicked.connect(self.load_apps)
        self._load_apps_btn = load_btn

        self.app_count_label = QLabel("")
        self.app_count_label.setStyleSheet("color: #374151; font-size: 12px;")

        btn_row.addWidget(load_btn)
        btn_row.addWidget(self.app_count_label)
        btn_row.addStretch()

        layout.addLayout(btn_row)
        layout.addWidget(self.apps_list)

        tab.setLayout(layout)
        self.tabs.addTab(tab, "Apps")

    def _browse_apk(self):
        path, _ = QFileDialog.getOpenFileName(
            self,
            "Selecionar APK",
            "",
            "Arquivos APK (*.apk);;Todos os arquivos (*)"
        )
        if path:
            self.apk_path_input.setText(path)
            self.install_btn.setEnabled(True)
            self.install_status.setText("")
            # Exibe só o nome do arquivo no status
            import os
            self.install_status.setText(f"  {os.path.basename(path)}")

    def _install_apk(self):
        path = self.apk_path_input.text().strip()
        if not path:
            return

        self.install_btn.setEnabled(False)
        self.install_status.setText("⏳  Instalando...")
        self.install_status.setStyleSheet("font-size: 12px; color: #F59E0B;")
        QApplication.processEvents()

        output = run_command(f'adb install -r "{path}"')

        if "Success" in output:
            self.install_status.setText("✓  Instalado com sucesso!")
            self.install_status.setStyleSheet("font-size: 12px; color: #4ADE80;")
            self.load_apps()  # Atualiza lista automaticamente
        else:
            error = output.strip().splitlines()[-1] if output.strip() else "Erro desconhecido"
            self.install_status.setText(f"✗  {error}")
            self.install_status.setStyleSheet("font-size: 12px; color: #F87171;")

        self.install_btn.setEnabled(True)

    def load_apps(self):
        self.apps_list.clear()
        output   = run_command("adb shell pm list packages -3")
        packages = [p.replace("package:", "").strip() for p in output.splitlines() if p.strip()]

        for pkg in sorted(packages):
            item = QListWidgetItem(f"  {pkg}")
            item.setData(Qt.UserRole, pkg)
            self.apps_list.addItem(item)

        self.app_count_label.setText(tr(self._lang, "packages_found", n=len(packages)))

    def app_menu(self, position):
        item = self.apps_list.itemAt(position)
        if not item:
            return

        pkg  = item.data(Qt.UserRole)
        menu = QMenu()
        L = self._lang

        menu.addAction(tr(L,"menu_open"),
                       lambda: run_command(f"adb shell monkey -p {pkg} -c android.intent.category.LAUNCHER 1"))
        menu.addAction(tr(L,"menu_backup"), lambda: self._backup_apk(pkg))
        menu.addSeparator()
        menu.addAction(tr(L,"menu_clear"),
                       lambda: run_command(f"adb shell pm clear {pkg}"))
        menu.addAction(tr(L,"menu_uninstall"),
                       lambda: self._uninstall_app(pkg, item))

        menu.exec(self.apps_list.mapToGlobal(position))

    def _backup_apk(self, pkg):
        path_output = run_command(f"adb shell pm path {pkg}")
        apk_path = path_output.replace("package:", "").strip()
        if apk_path:
            run_command(f'adb pull "{apk_path}"')

    def _uninstall_app(self, pkg, item):
        run_command(f"adb uninstall {pkg}")
        row = self.apps_list.row(item)
        self.apps_list.takeItem(row)

    # ── ADB ──────────────────────────────────────────────────
    def create_adb_tab(self):
        L = self._lang
        tab, layout = self._tab_layout(tr(L,"tab_adb"), tr(L,"tab_adb_sub"))

        layout.addWidget(self._sec("sec_command_adb"))

        input_row = QHBoxLayout()
        prefix = QLabel("adb")
        prefix.setStyleSheet("color: #7EB8F7; font-weight: bold; font-size: 14px; padding: 0 4px;")

        self.adb_input = QLineEdit()
        self.adb_input.setPlaceholderText(tr(L,"adb_placeholder"))
        self.adb_input.returnPressed.connect(self.run_adb)

        run_btn = QPushButton(tr(L,"btn_run"))
        run_btn.setObjectName("PrimaryButton")
        run_btn.setFixedWidth(110)
        run_btn.clicked.connect(self.run_adb)
        self._adb_run_btn = run_btn

        clear_btn = QPushButton(tr(L,"btn_clear"))
        clear_btn.setFixedWidth(90)
        clear_btn.clicked.connect(lambda: self.adb_output.clear())
        self._adb_clear_btn = clear_btn

        input_row.addWidget(prefix)
        input_row.addWidget(self.adb_input, 1)
        input_row.addWidget(run_btn)
        input_row.addWidget(clear_btn)
        layout.addLayout(input_row)

        layout.addWidget(self._sec("sec_output_adb"))
        self.adb_output = TerminalOutput("# ...")
        layout.addWidget(self.adb_output)

        tab.setLayout(layout)
        self.tabs.addTab(tab, "ADB")

    def run_adb(self):
        sub = self.adb_input.text().strip()
        if not sub:
            return
        command = sub if sub.startswith("adb ") else f"adb {sub}"
        self.adb_output.append_line(f"$ {command}")
        output = run_command(command)
        self.adb_output.append_line(output.rstrip() or "(no output)")
        self.adb_output.append_line("─" * 40)

    # ── Fastboot ─────────────────────────────────────────────
    def create_fastboot_tab(self):
        L = self._lang
        tab, layout = self._tab_layout(tr(L,"tab_fastboot"), tr(L,"tab_fastboot_sub"))

        layout.addWidget(self._sec("sec_command_fb"))

        input_row = QHBoxLayout()
        prefix = QLabel("fastboot")
        prefix.setStyleSheet("color: #F59E0B; font-weight: bold; font-size: 14px; padding: 0 4px;")

        self.fastboot_input = QLineEdit()
        self.fastboot_input.setPlaceholderText(tr(L,"fb_placeholder"))
        self.fastboot_input.returnPressed.connect(self.run_fastboot)

        run_btn = QPushButton(tr(L,"btn_run"))
        run_btn.setObjectName("PrimaryButton")
        run_btn.setFixedWidth(110)
        run_btn.clicked.connect(self.run_fastboot)
        self._fb_run_btn = run_btn

        clear_btn = QPushButton(tr(L,"btn_clear"))
        clear_btn.setFixedWidth(90)
        clear_btn.clicked.connect(lambda: self.fastboot_output.clear())
        self._fb_clear_btn = clear_btn

        input_row.addWidget(prefix)
        input_row.addWidget(self.fastboot_input, 1)
        input_row.addWidget(run_btn)
        input_row.addWidget(clear_btn)
        layout.addLayout(input_row)

        layout.addWidget(self._sec("sec_quick"))
        quick_row = QHBoxLayout()
        quick_row.setSpacing(10)

        devices_btn = QPushButton(tr(L,"btn_devices"))
        devices_btn.setFixedHeight(34)
        devices_btn.clicked.connect(lambda: self._run_fastboot_cmd("fastboot devices"))
        self._fb_devices_btn = devices_btn

        reboot_btn = QPushButton(tr(L,"btn_reboot"))
        reboot_btn.setFixedHeight(34)
        reboot_btn.clicked.connect(lambda: self._run_fastboot_cmd("fastboot reboot"))
        self._fb_reboot_btn = reboot_btn

        bootloader_btn = QPushButton(tr(L,"btn_bootloader"))
        bootloader_btn.setFixedHeight(34)
        bootloader_btn.clicked.connect(lambda: self._run_fastboot_cmd("fastboot reboot-bootloader"))
        self._fb_bootloader_btn = bootloader_btn

        recovery_btn = QPushButton(tr(L,"btn_recovery_warn"))
        recovery_btn.setObjectName("DangerButton")
        recovery_btn.setFixedHeight(34)
        recovery_btn.clicked.connect(lambda: self._run_fastboot_cmd("fastboot reboot recovery"))
        self._fb_recovery_btn = recovery_btn

        quick_row.addWidget(devices_btn)
        quick_row.addWidget(reboot_btn)
        quick_row.addWidget(bootloader_btn)
        quick_row.addWidget(recovery_btn)
        quick_row.addStretch()
        layout.addLayout(quick_row)

        layout.addWidget(self._sec("sec_output_fb"))
        self.fastboot_output = TerminalOutput("# ...")
        self.fastboot_output.setStyleSheet(
            "QTextEdit#TerminalOutput { color: #F59E0B; background-color: #080A0D; "
            "border: 1px solid #1A1D24; border-radius: 10px; padding: 14px; "
            "font-family: 'Consolas', 'Courier New', monospace; font-size: 12px; }"
        )
        layout.addWidget(self.fastboot_output)

        tab.setLayout(layout)
        self.tabs.addTab(tab, "Fastboot")

    def _run_fastboot_cmd(self, full_command):
        self.fastboot_output.append_line(f"$ {full_command}")
        self.thread = FastbootThread(full_command)
        self.thread.output_signal.connect(self.fastboot_output.append_line)
        self.thread.start()

    def run_fastboot(self):
        sub = self.fastboot_input.text().strip()
        if not sub:
            return
        command = sub if sub.startswith("fastboot ") else f"fastboot {sub}"
        self._run_fastboot_cmd(command)

    # ── Flash AOSP ───────────────────────────────────────────
    def create_rom_tab(self):
        L = self._lang
        tab, layout = self._tab_layout(tr(L,"tab_aosp"), tr(L,"tab_aosp_sub"))

        layout.addWidget(self._sec("sec_step1"))

        rom_frame = QFrame()
        rom_frame.setObjectName("InstallFrame")
        rom_inner = QVBoxLayout()
        rom_inner.setContentsMargins(16, 14, 16, 14)
        rom_inner.setSpacing(10)

        rom_file_row = QHBoxLayout()
        self.rom_path_input = QLineEdit()
        self.rom_path_input.setPlaceholderText(tr(L,"rom_placeholder"))
        self.rom_path_input.setReadOnly(True)

        rom_browse_btn = QPushButton(tr(L,"btn_select_rom"))
        rom_browse_btn.setFixedWidth(140)
        rom_browse_btn.clicked.connect(self._browse_rom)
        self._aosp_browse_btn = rom_browse_btn

        rom_file_row.addWidget(self.rom_path_input, 1)
        rom_file_row.addWidget(rom_browse_btn)
        rom_inner.addLayout(rom_file_row)

        sep = QFrame()
        sep.setFixedHeight(1)
        sep.setStyleSheet("background-color: #1E2028;")
        rom_inner.addWidget(sep)

        dumper_label_row = QHBoxLayout()
        dumper_title = QLabel(tr(L,"dumper_label"))
        dumper_title.setStyleSheet("color: #6B7280; font-size: 11px; letter-spacing: 1px;")
        dumper_hint = QLabel(tr(L,"dumper_hint"))
        dumper_hint.setStyleSheet("color: #374151; font-size: 11px;")
        self._dumper_title_lbl = dumper_title
        self._dumper_hint_lbl  = dumper_hint
        dumper_label_row.addWidget(dumper_title)
        dumper_label_row.addStretch()
        dumper_label_row.addWidget(dumper_hint)
        rom_inner.addLayout(dumper_label_row)

        dumper_row = QHBoxLayout()
        dumper_row.setSpacing(8)

        self.dumper_path_input = QLineEdit()
        self.dumper_path_input.setPlaceholderText(tr(L,"dumper_placeholder"))
        self.dumper_path_input.setText("payload-dumper-go")

        dumper_browse_btn = QPushButton(tr(L,"btn_select_exe"))
        dumper_browse_btn.setFixedWidth(200)
        dumper_browse_btn.setFixedHeight(36)
        dumper_browse_btn.setStyleSheet(
            "QPushButton { background-color: #1A1D25; border: 1px solid #252933; "
            "border-radius: 8px; padding: 0 14px; color: #9CA3AF; font-size: 12px; }"
            "QPushButton:hover { background-color: #1E2330; border-color: #3B4460; color: #D8DEE9; }"
        )
        dumper_browse_btn.clicked.connect(self._browse_dumper)
        self._dumper_browse_btn = dumper_browse_btn

        dumper_row.addWidget(self.dumper_path_input, 1)
        dumper_row.addWidget(dumper_browse_btn)
        rom_inner.addLayout(dumper_row)

        rom_frame.setLayout(rom_inner)
        layout.addWidget(rom_frame)

        layout.addWidget(self._sec("sec_step2"))

        extract_frame = QFrame()
        extract_frame.setObjectName("InstallFrame")
        extract_inner = QVBoxLayout()
        extract_inner.setContentsMargins(16, 14, 16, 14)
        extract_inner.setSpacing(10)

        partitions_row = QHBoxLayout()
        part_lbl = QLabel(tr(L,"partitions_label"))
        part_lbl.setStyleSheet("color: #4B5563; font-size: 12px;")
        part_lbl.setFixedWidth(90)
        self._partitions_lbl = part_lbl

        self.partitions_input = QLineEdit()
        self.partitions_input.setText("boot,init_boot,vendor_boot")
        self.partitions_input.setPlaceholderText("boot,init_boot,vendor_boot")

        partitions_row.addWidget(part_lbl)
        partitions_row.addWidget(self.partitions_input, 1)
        extract_inner.addLayout(partitions_row)

        extract_action_row = QHBoxLayout()
        self.extract_btn = QPushButton(tr(L,"btn_extract"))
        self.extract_btn.setObjectName("PrimaryButton")
        self.extract_btn.setFixedWidth(200)
        self.extract_btn.setEnabled(False)
        self.extract_btn.clicked.connect(self._start_extraction)

        self.extract_status = QLabel(tr(L,"extract_start_msg"))
        self.extract_status.setStyleSheet("font-size: 12px; color: #374151;")

        extract_action_row.addWidget(self.extract_btn)
        extract_action_row.addWidget(self.extract_status)
        extract_action_row.addStretch()
        extract_inner.addLayout(extract_action_row)

        self.extract_log = TerminalOutput("# ...")
        self.extract_log.setMaximumHeight(140)
        extract_inner.addWidget(self.extract_log)

        extract_frame.setLayout(extract_inner)
        layout.addWidget(extract_frame)

        layout.addWidget(self._sec("sec_step3"))

        flash_frame = QFrame()
        flash_frame.setObjectName("FlashFrame")
        flash_inner = QVBoxLayout()
        flash_inner.setContentsMargins(16, 14, 16, 14)
        flash_inner.setSpacing(8)

        flash_info = QLabel(tr(L,"flash_info"))
        flash_info.setStyleSheet("color: #374151; font-size: 12px;")
        self._flash_info_lbl = flash_info
        flash_inner.addWidget(flash_info)

        self.flash_commands_display = QTextEdit()
        self.flash_commands_display.setObjectName("TerminalOutput")
        self.flash_commands_display.setReadOnly(True)
        self.flash_commands_display.setMaximumHeight(120)
        flash_inner.addWidget(self.flash_commands_display)

        flash_btn_row = QHBoxLayout()
        flash_btn_row.setSpacing(10)

        self.reboot_fb_btn = QPushButton(tr(L,"btn_reboot_fb"))
        self.reboot_fb_btn.setObjectName("DangerButton")
        self.reboot_fb_btn.setFixedWidth(180)
        self.reboot_fb_btn.clicked.connect(self._reboot_fastboot)

        self.flash_btn = QPushButton(tr(L,"btn_flash_now"))
        self.flash_btn.setObjectName("PrimaryButton")
        self.flash_btn.setFixedWidth(190)
        self.flash_btn.setEnabled(False)
        self.flash_btn.clicked.connect(self._do_flash)

        self.reboot_rec_btn = QPushButton(tr(L,"btn_reboot_rec"))
        self.reboot_rec_btn.setObjectName("DangerButton")
        self.reboot_rec_btn.setFixedWidth(170)
        self.reboot_rec_btn.setEnabled(False)
        self.reboot_rec_btn.clicked.connect(self._reboot_recovery)

        self.cleanup_btn = QPushButton(tr(L,"btn_cleanup"))
        self.cleanup_btn.setFixedWidth(160)
        self.cleanup_btn.setEnabled(False)
        self.cleanup_btn.clicked.connect(self._cleanup_extracted)

        self.flash_status = QLabel("")
        self.flash_status.setStyleSheet("font-size: 12px; color: #374151;")

        self.sideload_btn = QPushButton(tr(L,"btn_flash_rom"))
        self.sideload_btn.setObjectName("SuccessButton")
        self.sideload_btn.setFixedWidth(160)
        self.sideload_btn.clicked.connect(self._do_sideload)

        flash_btn_row.addWidget(self.reboot_fb_btn)
        flash_btn_row.addWidget(self.flash_btn)
        flash_btn_row.addWidget(self.reboot_rec_btn)
        flash_btn_row.addWidget(self.cleanup_btn)
        flash_btn_row.addWidget(self.flash_status)
        flash_btn_row.addStretch()
        flash_btn_row.addWidget(self.sideload_btn)
        flash_inner.addLayout(flash_btn_row)

        self.sideload_notice = QLabel(tr(L,"sideload_notice"))
        self.sideload_notice.setObjectName("SideloadNotice")
        self.sideload_notice.setVisible(False)
        self.sideload_notice.setWordWrap(True)
        flash_inner.addWidget(self.sideload_notice)

        self.flash_log = TerminalOutput("# ...")
        self.flash_log.setStyleSheet(
            "QTextEdit#TerminalOutput { color: #F59E0B; background-color: #080A0D; "
            "border: 1px solid #1A1D24; border-radius: 10px; padding: 14px; "
            "font-family: 'Consolas', 'Courier New', monospace; font-size: 12px; }"
        )
        flash_inner.addWidget(self.flash_log)

        flash_frame.setLayout(flash_inner)
        layout.addWidget(flash_frame)

        self._extracted_dir   = None
        self._extracted_files = {}

        tab.setLayout(layout)
        self.tabs.addTab(tab, "Flash AOSP")

    def _browse_rom(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Selecionar ROM", "",
            "Arquivos ZIP (*.zip);;Todos os arquivos (*)"
        )
        if path:
            self.rom_path_input.setText(path)
            self.extract_btn.setEnabled(True)
            self.extract_status.setText("ROM selecionada. Clique em Iniciar Extração.")
            self.extract_status.setStyleSheet("font-size: 12px; color: #9CA3AF;")

    def _browse_dumper(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Localizar payload-dumper-go", "", "Executáveis (*)"
        )
        if path:
            self.dumper_path_input.setText(path)

    def _start_extraction(self):
        import os, tempfile, zipfile, shutil

        rom_path = self.rom_path_input.text().strip()
        if not rom_path or not os.path.isfile(rom_path):
            self.extract_status.setText("✗  ROM não encontrada.")
            return

        self.extract_btn.setEnabled(False)
        self.flash_btn.setEnabled(False)
        self.flash_commands_display.clear()
        self.extract_log.clear()
        self._extracted_files = {}

        self.extract_status.setText("⏳  Extraindo ROM...")
        self.extract_status.setStyleSheet("font-size: 12px; color: #F59E0B;")
        QApplication.processEvents()

        # Diretório temporário de trabalho
        work_dir = tempfile.mkdtemp(prefix="rom_manager_")
        self._extracted_dir = work_dir
        self.extract_log.append_line(f"📁  Diretório temporário: {work_dir}")
        QApplication.processEvents()

        # Passo 1: extrair payload.bin do ZIP
        payload_path = os.path.join(work_dir, "payload.bin")
        try:
            self.extract_log.append_line("📦  Abrindo ROM zip...")
            QApplication.processEvents()
            with zipfile.ZipFile(rom_path, 'r') as z:
                names = z.namelist()
                payload_entries = [n for n in names if n.endswith("payload.bin")]
                if not payload_entries:
                    self.extract_log.append_line("✗  payload.bin não encontrado no ZIP!")
                    self.extract_status.setText("✗  payload.bin não encontrado na ROM.")
                    self.extract_status.setStyleSheet("font-size: 12px; color: #F87171;")
                    self.extract_btn.setEnabled(True)
                    return

                entry = payload_entries[0]
                self.extract_log.append_line(f"✓  payload.bin encontrado: {entry}")
                self.extract_log.append_line("⏳  Extraindo payload.bin (pode demorar)...")
                QApplication.processEvents()
                z.extract(entry, work_dir)

                # Se estiver em subpasta dentro do zip
                extracted_payload = os.path.join(work_dir, entry)
                if extracted_payload != payload_path:
                    shutil.move(extracted_payload, payload_path)

            self.extract_log.append_line(f"✓  payload.bin extraído ({os.path.getsize(payload_path) // 1024 // 1024} MB)")
            QApplication.processEvents()
        except Exception as e:
            self.extract_log.append_line(f"✗  Erro ao extrair ZIP: {e}")
            self.extract_status.setText("✗  Erro ao extrair ZIP.")
            self.extract_status.setStyleSheet("font-size: 12px; color: #F87171;")
            self.extract_btn.setEnabled(True)
            return

        # Passo 2: rodar payload-dumper-go
        partitions = [p.strip() for p in self.partitions_input.text().split(",") if p.strip()]
        dumper_exe = self.dumper_path_input.text().strip() or "payload-dumper-go"
        out_dir = os.path.join(work_dir, "extracted")
        os.makedirs(out_dir, exist_ok=True)

        parts_arg = ",".join(partitions)
        cmd = f'"{dumper_exe}" -p {parts_arg} -o "{out_dir}" "{payload_path}"'
        self.extract_log.append_line(f"\n$ {cmd}")
        QApplication.processEvents()

        self.extract_status.setText("⏳  Extraindo partições com payload-dumper-go...")
        QApplication.processEvents()

        # Run with live output via thread
        self._extract_thread = RomExtractThread(cmd, out_dir, partitions)
        self._extract_thread.log_signal.connect(self.extract_log.append_line)
        self._extract_thread.done_signal.connect(self._on_extraction_done)
        self._extract_thread.start()

    def _on_extraction_done(self, found_files: dict, error: str):
        import os
        if error:
            self.extract_status.setText(f"✗  {error}")
            self.extract_status.setStyleSheet("font-size: 12px; color: #F87171;")
            self.extract_btn.setEnabled(True)
            return

        self._extracted_files = found_files

        if not found_files:
            self.extract_status.setText("⚠  Nenhuma partição encontrada após extração.")
            self.extract_status.setStyleSheet("font-size: 12px; color: #F59E0B;")
            self.extract_btn.setEnabled(True)
            return

        self.extract_log.append_line(f"\n✓  {len(found_files)} partição(ões) extraída(s):")
        for name, path in found_files.items():
            size_mb = os.path.getsize(path) / 1024 / 1024
            self.extract_log.append_line(f"   • {name}.img  ({size_mb:.1f} MB)")

        self.extract_status.setText(f"✓  Extração concluída! {len(found_files)} arquivo(s) prontos.")
        self.extract_status.setStyleSheet("font-size: 12px; color: #4ADE80;")

        # Monta comandos de flash
        # Ordem preferencial: init_boot primeiro, depois boot, vendor_boot
        priority = ["init_boot", "boot", "vendor_boot"]
        ordered = [p for p in priority if p in found_files]
        ordered += [p for p in found_files if p not in ordered]

        lines = []
        for part in ordered:
            img_path = found_files[part]
            lines.append(f'fastboot flash {part}_ab "{img_path}"')

        self.flash_commands_display.setPlainText("\n".join(lines))
        self.flash_btn.setEnabled(True)
        self.cleanup_btn.setEnabled(True)
        self.extract_btn.setEnabled(True)
        QApplication.processEvents()

    def _do_flash(self):
        if not self._extracted_files:
            return

        self.flash_btn.setEnabled(False)
        self.flash_log.clear()
        self.flash_status.setText("⏳  Fazendo flash...")
        self.flash_status.setStyleSheet("font-size: 12px; color: #F59E0B;")
        QApplication.processEvents()

        priority = ["init_boot", "boot", "vendor_boot"]
        ordered = [p for p in priority if p in self._extracted_files]
        ordered += [p for p in self._extracted_files if p not in ordered]

        commands = []
        for part in ordered:
            img_path = self._extracted_files[part]
            commands.append(f'fastboot flash {part}_ab "{img_path}"')

        self._flash_thread = SequentialFastbootThread(commands)
        self._flash_thread.log_signal.connect(self.flash_log.append_line)
        self._flash_thread.done_signal.connect(self._on_flash_done)
        self._flash_thread.start()

    def _on_flash_done(self, success: bool):
        if success:
            self.flash_status.setText("✓  Flash concluído! Reinicie para recovery.")
            self.flash_status.setStyleSheet("font-size: 12px; color: #4ADE80;")
            self.reboot_rec_btn.setEnabled(True)
        else:
            self.flash_status.setText("✗  Erro durante flash. Veja o log.")
            self.flash_status.setStyleSheet("font-size: 12px; color: #F87171;")
        self.flash_btn.setEnabled(True)

    def _reboot_fastboot(self):
        self.flash_log.append_line("\n$ adb reboot fastboot")
        run_command("adb reboot fastboot")
        self.flash_log.append_line("✓  Comando enviado. Aguarde o dispositivo reiniciar em fastboot.")

    def _do_sideload(self):
        import os
        rom_path = self.rom_path_input.text().strip()
        if not rom_path or not os.path.isfile(rom_path):
            self.flash_log.append_line("✗  Nenhuma ROM selecionada. Escolha um arquivo .zip no Passo 1.")
            self.sideload_notice.setVisible(False)
            return

        rom_name = os.path.basename(rom_path)
        L = self._lang

        msg = QMessageBox(self)
        msg.setWindowTitle(tr(L,"sideload_title"))
        msg.setIcon(QMessageBox.Warning)
        msg.setText(tr(L,"sideload_bold"))
        msg.setInformativeText(
            tr(L,"sideload_body") +
            f"<span style='color:#9CA3AF;'>ROM: {rom_name}</span>"
        )
        msg.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
        msg.button(QMessageBox.Ok).setText(tr(L,"btn_confirm_flash"))
        msg.button(QMessageBox.Cancel).setText(tr(L,"btn_cancel"))

        # Estilo escuro no popup
        msg.setStyleSheet("""
            QMessageBox {
                background-color: #111318;
                color: #D8DEE9;
                font-family: 'Consolas', 'Courier New', monospace;
            }
            QMessageBox QLabel {
                color: #D8DEE9;
                font-size: 13px;
                min-width: 380px;
            }
            QPushButton {
                background-color: #1A1D25;
                border: 1px solid #252933;
                border-radius: 8px;
                padding: 8px 18px;
                color: #9CA3AF;
                font-size: 12px;
                min-width: 160px;
            }
            QPushButton:hover {
                background-color: #1E2330;
                color: #D8DEE9;
            }
            QPushButton:default {
                background-color: #0F2A1A;
                border-color: #1A5C32;
                color: #4ADE80;
                font-weight: bold;
            }
            QPushButton:default:hover {
                background-color: #153520;
                border-color: #22A355;
            }
        """)

        result = msg.exec()

        if result != QMessageBox.Ok:
            return

        # Usuário confirmou — inicia o sideload
        self.sideload_notice.setVisible(True)
        self.sideload_btn.setEnabled(False)
        QApplication.processEvents()

        cmd = f'adb sideload "{rom_path}"'
        self.flash_log.append_line(f"\n$ {cmd}")
        self.flash_log.append_line("⏳  Enviando ROM... (aguarde, pode demorar vários minutos)")
        QApplication.processEvents()

        self._sideload_thread = FastbootThread(cmd)
        self._sideload_thread.output_signal.connect(self.flash_log.append_line)
        self._sideload_thread.finished.connect(self._on_sideload_done)
        self._sideload_thread.start()

    def _on_sideload_done(self):
        self.sideload_btn.setEnabled(True)
        self.flash_log.append_line("✓  Sideload concluído (verifique o dispositivo).")

    def _reboot_recovery(self):
        self.flash_log.append_line("\n$ fastboot reboot recovery")
        run_command("fastboot reboot recovery")
        self.flash_log.append_line("✓  Comando enviado.")

    def _cleanup_extracted(self):
        import shutil
        if self._extracted_dir and os.path.isdir(self._extracted_dir):
            try:
                shutil.rmtree(self._extracted_dir)
                self.extract_log.append_line(f"\n🗑  Arquivos temporários removidos: {self._extracted_dir}")
                self._extracted_dir = None
                self._extracted_files = {}
                self.flash_btn.setEnabled(False)
                self.cleanup_btn.setEnabled(False)
                self.reboot_rec_btn.setEnabled(False)
                self.flash_commands_display.clear()
                self.flash_status.setText("🗑  Arquivos removidos.")
                self.flash_status.setStyleSheet("font-size: 12px; color: #9CA3AF;")
            except Exception as e:
                self.extract_log.append_line(f"✗  Erro ao remover: {e}")

    # ── Flash HyperOS ────────────────────────────────────────
    def create_hyperos_tab(self):
        L = self._lang
        tab, layout = self._tab_layout(tr(L,"tab_hyperos"), tr(L,"tab_hyperos_sub"))

        layout.addWidget(self._sec("sec_hyper_step1"))

        rom_frame = QFrame()
        rom_frame.setObjectName("InstallFrame")
        rom_inner = QVBoxLayout()
        rom_inner.setContentsMargins(16, 14, 16, 14)
        rom_inner.setSpacing(10)

        rom_file_row = QHBoxLayout()
        self.hyper_rom_input = QLineEdit()
        self.hyper_rom_input.setPlaceholderText(tr(L,"hyper_placeholder"))
        self.hyper_rom_input.setReadOnly(True)

        hyper_browse_btn = QPushButton(tr(L,"btn_select_rom"))
        hyper_browse_btn.setObjectName("PrimaryButton")
        hyper_browse_btn.setFixedWidth(150)
        hyper_browse_btn.clicked.connect(self._hyper_browse_rom)
        self._hyper_browse_btn_ref = hyper_browse_btn

        rom_file_row.addWidget(self.hyper_rom_input, 1)
        rom_file_row.addWidget(hyper_browse_btn)
        rom_inner.addLayout(rom_file_row)

        rom_frame.setLayout(rom_inner)
        layout.addWidget(rom_frame)

        layout.addWidget(self._sec("sec_hyper_step2"))

        extract_frame = QFrame()
        extract_frame.setObjectName("InstallFrame")
        extract_inner = QVBoxLayout()
        extract_inner.setContentsMargins(16, 14, 16, 14)
        extract_inner.setSpacing(10)

        extract_action_row = QHBoxLayout()
        self.hyper_extract_btn = QPushButton(tr(L,"btn_hyper_extract"))
        self.hyper_extract_btn.setObjectName("PrimaryButton")
        self.hyper_extract_btn.setFixedWidth(180)
        self.hyper_extract_btn.setEnabled(False)
        self.hyper_extract_btn.clicked.connect(self._hyper_extract)

        self.hyper_extract_status = QLabel(tr(L,"hyper_start_msg"))
        self.hyper_extract_status.setStyleSheet("font-size: 12px; color: #374151;")

        extract_action_row.addWidget(self.hyper_extract_btn)
        extract_action_row.addWidget(self.hyper_extract_status)
        extract_action_row.addStretch()
        extract_inner.addLayout(extract_action_row)

        self.hyper_extract_log = TerminalOutput("# ...")
        self.hyper_extract_log.setMaximumHeight(100)
        extract_inner.addWidget(self.hyper_extract_log)

        extract_frame.setLayout(extract_inner)
        layout.addWidget(extract_frame)

        layout.addWidget(self._sec("sec_hyper_step3"))

        scripts_frame = QFrame()
        scripts_frame.setObjectName("InstallFrame")
        scripts_inner = QVBoxLayout()
        scripts_inner.setContentsMargins(16, 14, 16, 14)
        scripts_inner.setSpacing(10)

        scripts_hint = QLabel(tr(L,"scripts_hint"))
        scripts_hint.setStyleSheet("font-size: 11px; color: #4B5563;")
        scripts_hint.setWordWrap(True)
        self._scripts_hint_lbl = scripts_hint
        scripts_inner.addWidget(scripts_hint)

        self.hyper_scripts_list = QListWidget()
        self.hyper_scripts_list.setObjectName("ScriptsList")
        self.hyper_scripts_list.setMaximumHeight(160)
        self.hyper_scripts_list.setSelectionMode(QListWidget.SingleSelection)
        self.hyper_scripts_list.itemClicked.connect(self._hyper_script_selected)
        scripts_inner.addWidget(self.hyper_scripts_list)

        scripts_frame.setLayout(scripts_inner)
        layout.addWidget(scripts_frame)

        layout.addWidget(self._sec("sec_hyper_step4"))

        flash_frame = QFrame()
        flash_frame.setObjectName("FlashFrame")
        flash_inner = QVBoxLayout()
        flash_inner.setContentsMargins(16, 14, 16, 14)
        flash_inner.setSpacing(10)

        self.hyper_selected_label = QLabel(tr(L,"no_script"))
        self.hyper_selected_label.setStyleSheet(
            "font-size: 12px; color: #4B5563; font-style: italic;"
        )
        flash_inner.addWidget(self.hyper_selected_label)

        flash_btn_row = QHBoxLayout()
        flash_btn_row.setSpacing(10)

        self.hyper_flash_btn = QPushButton(tr(L,"btn_run_script"))
        self.hyper_flash_btn.setObjectName("PrimaryButton")
        self.hyper_flash_btn.setFixedWidth(190)
        self.hyper_flash_btn.setEnabled(False)
        self.hyper_flash_btn.clicked.connect(self._hyper_run_flash)

        self.hyper_cleanup_btn = QPushButton(tr(L,"btn_cleanup"))
        self.hyper_cleanup_btn.setFixedWidth(160)
        self.hyper_cleanup_btn.setEnabled(False)
        self.hyper_cleanup_btn.clicked.connect(self._hyper_cleanup)

        self.hyper_flash_status = QLabel("")
        self.hyper_flash_status.setStyleSheet("font-size: 12px; color: #374151;")

        flash_btn_row.addWidget(self.hyper_flash_btn)
        flash_btn_row.addWidget(self.hyper_cleanup_btn)
        flash_btn_row.addWidget(self.hyper_flash_status)
        flash_btn_row.addStretch()
        flash_inner.addLayout(flash_btn_row)

        self.hyper_flash_log = TerminalOutput("# ...")
        self.hyper_flash_log.setStyleSheet(
            "QTextEdit#TerminalOutput { color: #E879F9; background-color: #080A0D; "
            "border: 1px solid #1A1D24; border-radius: 10px; padding: 14px; "
            "font-family: 'Consolas', 'Courier New', monospace; font-size: 12px; }"
        )
        flash_inner.addWidget(self.hyper_flash_log)

        flash_frame.setLayout(flash_inner)
        layout.addWidget(flash_frame)

        self._hyper_extract_dir    = None
        self._hyper_selected_script = None

        tab.setLayout(layout)
        self.tabs.addTab(tab, "Flash HyperOS")

    def _hyper_browse_rom(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Selecionar ROM HyperOS", "",
            "Arquivos ZIP (*.zip);;Todos os arquivos (*)"
        )
        if path:
            self.hyper_rom_input.setText(path)
            self.hyper_extract_btn.setEnabled(True)
            self.hyper_extract_status.setText("ROM selecionada. Clique em Extrair ROM.")
            self.hyper_extract_status.setStyleSheet("font-size: 12px; color: #9CA3AF;")
            # Reset estado anterior
            self.hyper_scripts_list.clear()
            self.hyper_flash_btn.setEnabled(False)
            self.hyper_selected_label.setText("Nenhum script selecionado.")
            self._hyper_selected_script = None

    def _hyper_extract(self):
        import zipfile, tempfile, shutil

        rom_path = self.hyper_rom_input.text().strip()
        if not rom_path or not os.path.isfile(rom_path):
            return

        self.hyper_extract_btn.setEnabled(False)
        self.hyper_scripts_list.clear()
        self.hyper_extract_log.clear()
        self.hyper_flash_btn.setEnabled(False)
        self._hyper_selected_script = None
        self.hyper_selected_label.setText("Nenhum script selecionado.")

        self.hyper_extract_status.setText("⏳  Extraindo...")
        self.hyper_extract_status.setStyleSheet("font-size: 12px; color: #F59E0B;")
        QApplication.processEvents()

        # Limpa extração anterior
        if self._hyper_extract_dir and os.path.isdir(self._hyper_extract_dir):
            import shutil as _sh
            _sh.rmtree(self._hyper_extract_dir, ignore_errors=True)

        work_dir = tempfile.mkdtemp(prefix="hyperos_")
        self._hyper_extract_dir = work_dir

        self.hyper_extract_log.append_line(f"📁  Diretório temporário: {work_dir}")
        QApplication.processEvents()

        try:
            with zipfile.ZipFile(rom_path, 'r') as z:
                all_files = z.namelist()
                # Filtra scripts .bat e .sh
                scripts = [
                    f for f in all_files
                    if f.lower().endswith(('.bat', '.sh'))
                    and '/' not in f.rstrip('/').replace('\\', '/')  # só raiz ou subpastas conhecidas
                ]
                # Se não achar na raiz, busca em qualquer nível
                if not scripts:
                    scripts = [f for f in all_files if f.lower().endswith(('.bat', '.sh'))]

                total = len(all_files)
                self.hyper_extract_log.append_line(f"📦  {total} arquivos no ZIP.")
                self.hyper_extract_log.append_line(f"🔍  Extraindo conteúdo completo...")
                QApplication.processEvents()

                z.extractall(work_dir)

            self.hyper_extract_log.append_line("✓  Extração concluída.")
            QApplication.processEvents()

            # Lista scripts encontrados no diretório extraído
            found_scripts = []
            for root_dir, dirs, files in os.walk(work_dir):
                for f in files:
                    if f.lower().endswith(('.bat', '.sh')):
                        found_scripts.append(os.path.join(root_dir, f))

            if not found_scripts:
                self.hyper_extract_log.append_line("⚠  Nenhum script .bat/.sh encontrado.")
                self.hyper_extract_status.setText("⚠  Nenhum script encontrado.")
                self.hyper_extract_status.setStyleSheet("font-size: 12px; color: #F59E0B;")
                self.hyper_extract_btn.setEnabled(True)
                return

            self.hyper_extract_log.append_line(f"\n📋  {len(found_scripts)} script(s) encontrado(s):")
            self.hyper_scripts_list.clear()

            for script_path in sorted(found_scripts):
                rel = os.path.relpath(script_path, work_dir)
                self.hyper_extract_log.append_line(f"   • {rel}")
                item = QListWidgetItem(f"  {rel}")
                item.setData(Qt.UserRole, script_path)
                self.hyper_scripts_list.addItem(item)

            self.hyper_extract_status.setText(
                f"✓  {len(found_scripts)} script(s) encontrado(s). Selecione um abaixo."
            )
            self.hyper_extract_status.setStyleSheet("font-size: 12px; color: #4ADE80;")
            self.hyper_cleanup_btn.setEnabled(True)

        except Exception as e:
            self.hyper_extract_log.append_line(f"✗  Erro: {e}")
            self.hyper_extract_status.setText("✗  Erro na extração.")
            self.hyper_extract_status.setStyleSheet("font-size: 12px; color: #F87171;")

        self.hyper_extract_btn.setEnabled(True)

    def _hyper_script_selected(self, item):
        script_path = item.data(Qt.UserRole)
        self._hyper_selected_script = script_path
        rel = os.path.relpath(script_path, self._hyper_extract_dir or "")
        self.hyper_selected_label.setText(f"▶  Script selecionado:  {rel}")
        self.hyper_selected_label.setStyleSheet("font-size: 12px; color: #E879F9; font-style: normal;")
        self.hyper_flash_btn.setEnabled(True)

    def _hyper_run_flash(self):
        if not self._hyper_selected_script or not os.path.isfile(self._hyper_selected_script):
            self.hyper_flash_status.setText("✗  Script não encontrado.")
            return

        script = self._hyper_selected_script
        script_dir = os.path.dirname(script)
        script_name = os.path.basename(script)

        # Monta comando de acordo com a extensão
        if script_name.lower().endswith('.bat'):
            if sys.platform == 'win32':
                cmd = f'cd /d "{script_dir}" && "{script_name}"'
            else:
                cmd = f'cd "{script_dir}" && wine "{script_name}"'
        else:
            cmd = f'cd "{script_dir}" && bash "{script_name}"'

        self.hyper_flash_log.clear()
        self.hyper_flash_log.append_line(f"$ {cmd}\n")
        self.hyper_flash_btn.setEnabled(False)
        self.hyper_flash_status.setText("⏳  Executando script...")
        self.hyper_flash_status.setStyleSheet("font-size: 12px; color: #F59E0B;")
        QApplication.processEvents()

        self._hyper_flash_thread = FastbootThread(cmd)
        self._hyper_flash_thread.output_signal.connect(self.hyper_flash_log.append_line)
        self._hyper_flash_thread.finished.connect(self._hyper_flash_done)
        self._hyper_flash_thread.start()

    def _hyper_flash_done(self):
        self.hyper_flash_btn.setEnabled(True)
        self.hyper_flash_status.setText("✓  Script finalizado. Verifique o log.")
        self.hyper_flash_status.setStyleSheet("font-size: 12px; color: #4ADE80;")

    def _hyper_cleanup(self):
        import shutil
        if self._hyper_extract_dir and os.path.isdir(self._hyper_extract_dir):
            try:
                shutil.rmtree(self._hyper_extract_dir)
                self.hyper_extract_log.append_line(f"\n🗑  Removido: {self._hyper_extract_dir}")
                self._hyper_extract_dir = None
                self._hyper_selected_script = None
                self.hyper_scripts_list.clear()
                self.hyper_flash_btn.setEnabled(False)
                self.hyper_cleanup_btn.setEnabled(False)
                self.hyper_selected_label.setText("Nenhum script selecionado.")
                self.hyper_selected_label.setStyleSheet(
                    "font-size: 12px; color: #4B5563; font-style: italic;"
                )
                self.hyper_flash_status.setText("🗑  Arquivos removidos.")
                self.hyper_flash_status.setStyleSheet("font-size: 12px; color: #9CA3AF;")
            except Exception as e:
                self.hyper_extract_log.append_line(f"✗  Erro ao remover: {e}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    # Dark palette base
    palette = app.palette()
    palette.setColor(QPalette.Window,          QColor("#0C0E12"))
    palette.setColor(QPalette.WindowText,      QColor("#D8DEE9"))
    palette.setColor(QPalette.Base,            QColor("#111318"))
    palette.setColor(QPalette.AlternateBase,   QColor("#151820"))
    palette.setColor(QPalette.Text,            QColor("#D8DEE9"))
    palette.setColor(QPalette.Button,          QColor("#1A1D25"))
    palette.setColor(QPalette.ButtonText,      QColor("#9CA3AF"))
    palette.setColor(QPalette.Highlight,       QColor("#1C2E4A"))
    palette.setColor(QPalette.HighlightedText, QColor("#7EB8F7"))
    app.setPalette(palette)

    window = RomManager()
    window.show()
    sys.exit(app.exec())


    #DESENVOLVIDO POR @ALYSONSB#