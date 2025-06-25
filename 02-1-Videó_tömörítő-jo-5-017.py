import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import json
import time
import logging
from pathlib import Path

# --- Naplózás beállítása ---
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('video_compressor.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# --- Konstansok ---
SETTINGS_FILE = "settings.json"
SCRIPT_NAME = os.path.basename(__file__)
PROFILES = {
    "Alacsony": {"crf": "28", "preset": "fast"},
    "Közepes": {"crf": "23", "preset": "medium"},
    "Magas": {"crf": "18", "preset": "slow"}
}

# --- Globális változók ---
root = tk.Tk()
root.title("Videó Tömörítő")
input_dir_path = ""
output_dir_path = ""
log_output_dir_path = ""
ffmpeg_path = "ffmpeg"
ffprobe_path = "ffprobe"
selected_profile = PROFILES[list(PROFILES.keys())[0]] if PROFILES else {}
program_start_time = None

# --- Tkinter változók ---
input_dir_path_var = tk.StringVar(root)
output_dir_path_var = tk.StringVar(root)
log_output_dir_path_var = tk.StringVar(root)
ffmpeg_path_var = tk.StringVar(root, value="ffmpeg")
ffprobe_path_var = tk.StringVar(root, value="ffprobe")
selected_profile_name_var = tk.StringVar(root)
if PROFILES:
    selected_profile_name_var.set(list(PROFILES.keys())[0])
num_threads_var = tk.IntVar(root, value=1)
excel_log_var = tk.BooleanVar(root, value=True)
pdf_log_var = tk.BooleanVar(root, value=False)
txt_log_var = tk.BooleanVar(root, value=True)
json_log_var = tk.BooleanVar(root, value=True)
file_type_var = tk.StringVar(root, value="ch")
progress_var = tk.DoubleVar(root)

# --- GUI elemek globális változói ---
browse_input_folder_button = None
browse_output_folder_button = None
select_log_output_dir_button = None
convert_button = None
pause_resume_button = None
stop_processing_button = None
load_files_button = None
clear_all_data_button = None
save_settings_button = None
verzio_log_button = None
exit_program_button = None
cancel_button = None
tree = None
status_label = None
loading_status_label = None
progress_bar = None
progress_percent_label = None
program_start_time_label = None
program_elapsed_time_label = None
session_elapsed_time_label = None
remaining_time_label = None
estimated_completion_label = None
processing_completed_label = None

# --- Beállítások betöltése ---
def load_app_settings():
    global selected_profile, ffmpeg_path, ffprobe_path, input_dir_path, output_dir_path, log_output_dir_path
    logger.debug("Beállítások betöltése elkezdődött")
    try:
        if os.path.exists(SETTINGS_FILE):
            with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
                settings = json.load(f)

            input_dir_path_var.set(settings.get("input_dir", ""))
            output_dir_path_var.set(settings.get("output_dir", ""))
            log_output_dir_path_var.set(settings.get("log_output_dir", ""))
            input_dir_path = input_dir_path_var.get()
            output_dir_path = output_dir_path_var.get()
            log_output_dir_path = log_output_dir_path_var.get()

            profile_name = settings.get("selected_profile_name")
            if profile_name and profile_name in PROFILES:
                selected_profile_name_var.set(profile_name)
                selected_profile = PROFILES[profile_name]
            else:
                if PROFILES:
                    selected_profile_name_var.set(list(PROFILES.keys())[0])
                    selected_profile = PROFILES[selected_profile_name_var.get()]

            num_threads_var.set(settings.get("num_threads", 1))
            excel_log_var.set(settings.get("excel_log", True))
            pdf_log_var.set(settings.get("pdf_log", False))
            txt_log_var.set(settings.get("txt_log", True))
            json_log_var.set(settings.get("json_log", True))
            file_type_var.set(settings.get("file_type_choice", "ch"))

            ffmpeg_path = settings.get("ffmpeg_path", "ffmpeg")
            ffprobe_path = settings.get("ffprobe_path", "ffprobe")
            ffmpeg_path_var.set(ffmpeg_path)
            ffprobe_path_var.set(ffprobe_path)

            logger.info("Beállítások sikeresen betöltve")
        else:
            logger.warning("Nincs mentett beállításfájl, alapértelmezett értékek használata")
            input_dir_path_var.set("")
            output_dir_path_var.set("")
            log_output_dir_path_var.set("")
            input_dir_path = ""
            output_dir_path = ""
            log_output_dir_path = ""
    except Exception as e:
        logger.error(f"Hiba a beállítások betöltésekor: {e}")
        input_dir_path_var.set("")
        output_dir_path_var.set("")
        log_output_dir_path_var.set("")
        input_dir_path = ""
        output_dir_path = ""
        log_output_dir_path = ""

# --- Munkamenet állapot betöltése ---
def load_session_state():
    logger.debug("Munkamenet állapot betöltése elkezdődött")
    try:
        # Placeholder: Munkamenet állapot betöltése (pl. Treeview adatok)
        logger.info("Munkamenet állapot sikeresen betöltve")
        return False  # Visszaadja, hogy folytatódott-e a munkamenet
    except Exception as e:
        logger.error(f"Hiba a munkamenet állapot betöltésekor: {e}")
        return False

# --- Beállítások mentése ---
def save_settings():
    logger.debug("Beállítások mentése elkezdődött")
    try:
        settings = {
            "input_dir": input_dir_path_var.get(),
            "output_dir": output_dir_path_var.get(),
            "log_output_dir": log_output_dir_path_var.get(),
            "selected_profile_name": selected_profile_name_var.get(),
            "num_threads": num_threads_var.get(),
            "excel_log": excel_log_var.get(),
            "pdf_log": pdf_log_var.get(),
            "txt_log": txt_log_var.get(),
            "json_log": json_log_var.get(),
            "file_type_choice": file_type_var.get(),
            "ffmpeg_path": ffmpeg_path_var.get(),
            "ffprobe_path": ffprobe_path_var.get()
        }
        with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
            json.dump(settings, f, indent=4)
        logger.info("Beállítások sikeresen mentve")
    except Exception as e:
        logger.error(f"Hiba a beállítások mentésekor: {e}")

# --- Mappa tallózása ---
def browse_input_folder():
    folder = filedialog.askdirectory()
    if folder:
        input_dir_path_var.set(folder)
        save_settings()
        logger.info(f"Bemeneti mappa kiválasztva: {folder}")

def browse_output_folder():
    folder = filedialog.askdirectory()
    if folder:
        output_dir_path_var.set(folder)
        save_settings()
        logger.info(f"Kimeneti mappa kiválasztva: {folder}")

def select_log_output_dir():
    folder = filedialog.askdirectory()
    if folder:
        log_output_dir_path_var.set(folder)
        save_settings()
        logger.info(f"Napló mappa kiválasztva: {folder}")

# --- FFmpeg/FFprobe útvonal beállítása ---
def set_ffmpeg_paths():
    ffmpeg_file = filedialog.askopenfilename(title="FFmpeg kiválasztása")
    if ffmpeg_file:
        ffmpeg_path_var.set(ffmpeg_file)
        logger.info(f"FFmpeg útvonal beállítva: {ffmpeg_file}")
    ffprobe_file = filedialog.askopenfilename(title="FFprobe kiválasztása")
    if ffprobe_file:
        ffprobe_path_var.set(ffprobe_file)
        logger.info(f"FFprobe útvonal beállítva: {ffprobe_file}")
    save_settings()

# --- Profil frissítése ---
def update_selected_profile_and_save_settings(*args):
    global selected_profile
    profile_name = selected_profile_name_var.get()
    if profile_name in PROFILES:
        selected_profile = PROFILES[profile_name]
        save_settings()
        logger.info(f"Profil frissítve: {profile_name}")

# --- Fájlok betöltése a Treeview-ba ---
def load_files_to_treeview():
    logger.debug("Fájlok betöltése a Treeview-ba elkezdődött")
    try:
        input_dir = input_dir_path_var.get()
        if not input_dir or not os.path.exists(input_dir):
            messagebox.showerror("Hiba", "Érvénytelen bemeneti mappa!")
            logger.error("Érvénytelen bemeneti mappa megadva")
            return
        # Placeholder: Fájlok betöltése (pl. os.listdir használata)
        for item in tree.get_children():
            tree.delete(item)
        # Példa fájlok hozzáadása
        for i, filename in enumerate(os.listdir(input_dir), 1):
            tree.insert("", "end", values=(i, filename, "-", "-", "-", "-", "-", "-", "-", "-", "-", "-", "-", "Készenlét", "-"))
        logger.info(f"Fájlok betöltve a Treeview-ba: {input_dir}")
    except Exception as e:
        logger.error(f"Hiba a fájlok betöltésekor: {e}")
        messagebox.showerror("Hiba", f"Hiba a fájlok betöltésekor: {e}")

# --- Feldolgozás indítása ---
def start_processing_thread():
    logger.debug("Feldolgozás indítása")
    try:
        # Placeholder: Feldolgozás logika
        status_label.config(text="Feldolgozás folyamatban...")
        logger.info("Feldolgozás sikeresen elindítva")
        set_ui_processing_state(True)
    except Exception as e:
        logger.error(f"Hiba a feldolgozás indításakor: {e}")
        messagebox.showerror("Hiba", f"Hiba a feldolgozás indításakor: {e}")

# --- Feldolgozás szüneteltetése/folytatása ---
def pause_resume_processing():
    logger.debug("Feldolgozás szüneteltetése/folytatása")
    try:
        # Placeholder: Szünet/folytatás logika
        logger.info("Feldolgozás szüneteltetve/folytatva")
    except Exception as e:
        logger.error(f"Hiba a szüneteltetés/folytatás során: {e}")

# --- Feldolgozás leállítása ---
def stop_processing():
    logger.debug("Feldolgozás leállítása")
    try:
        # Placeholder: Leállítás logika
        status_label.config(text="Feldolgozás leállítva.")
        logger.info("Feldolgozás sikeresen leállítva")
        set_ui_processing_state(False)
    except Exception as e:
        logger.error(f"Hiba a feldolgozás leállításakor: {e}")

# --- Feldolgozás megszakítása ---
def cancel_processing():
    logger.debug("Feldolgozás megszakítása")
    try:
        # Placeholder: Megszakítás logika
        status_label.config(text="Feldolgozás megszakítva.")
        logger.info("Feldolgozás sikeresen megszakítva")
        set_ui_processing_state(False)
    except Exception as e:
        logger.error(f"Hiba a feldolgozás megszakításakor: {e}")

# --- Adatok törlése ---
def clear_all_data():
    logger.debug("Adatok törlése")
    try:
        for item in tree.get_children():
            tree.delete(item)
        status_label.config(text="Adatok törölve.")
        logger.info("Adatok sikeresen törölve")
    except Exception as e:
        logger.error(f"Hiba az adatok törlésekor: {e}")

# --- Verzió log megnyitása ---
def open_verzio_log():
    logger.debug("Verzió log megnyitása")
    try:
        # Placeholder: Verzió log megnyitása
        messagebox.showinfo("Verzió log", "Nincs verzió log implementálva.")
        logger.info("Verzió log megnyitása megkísérelve")
    except Exception as e:
        logger.error(f"Hiba a verzió log megnyitásakor: {e}")

# --- Program kilépése ---
def exit_program():
    logger.debug("Program kilépése")
    try:
        save_settings()
        root.destroy()
        logger.info("Program sikeresen bezárva")
    except Exception as e:
        logger.error(f"Hiba a program bezárásakor: {e}")

# --- GUI állapot beállítása ---
def set_ui_processing_state(is_processing_active):
    logger.debug(f"set_ui_processing_state hívása - is_processing_active: {is_processing_active}")
    try:
        if browse_input_folder_button:
            browse_input_folder_button.config(state=tk.DISABLED if is_processing_active else tk.NORMAL)
        if browse_output_folder_button:
            browse_output_folder_button.config(state=tk.DISABLED if is_processing_active else tk.NORMAL)
        if select_log_output_dir_button:
            select_log_output_dir_button.config(state=tk.DISABLED if is_processing_active else tk.NORMAL)
        if convert_button:
            convert_button.config(state=tk.DISABLED if is_processing_active else tk.NORMAL)
        if pause_resume_button:
            pause_resume_button.config(state=tk.NORMAL if is_processing_active else tk.DISABLED)
        if stop_processing_button:
            stop_processing_button.config(state=tk.NORMAL if is_processing_active else tk.DISABLED)
        if load_files_button:
            load_files_button.config(state=tk.DISABLED if is_processing_active else tk.NORMAL)
        if clear_all_data_button:
            clear_all_data_button.config(state=tk.DISABLED if is_processing_active else tk.NORMAL)
        if save_settings_button:
            save_settings_button.config(state=tk.DISABLED if is_processing_active else tk.NORMAL)
        logger.debug("GUI állapot sikeresen frissítve")
    except Exception as e:
        logger.error(f"Hiba a GUI állapot beállításakor: {e}")

# --- Időkijelzők frissítése ---
def update_time_displays():
    logger.debug("Időkijelzők frissítése")
    try:
        if program_start_time:
            elapsed = time.time() - program_start_time
            hours, rem = divmod(elapsed, 3600)
            minutes, seconds = divmod(rem, 60)
            program_elapsed_time_label.config(text=f"Program futási ideje: {int(hours):02d}:{int(minutes):02d}:{int(seconds):02d}")
        root.after(1000, update_time_displays)
    except Exception as e:
        logger.error(f"Hiba az időkijelzők frissítésekor: {e}")

# --- GUI Inicializálás ---
def initialize_gui():
    global browse_input_folder_button, browse_output_folder_button, select_log_output_dir_button
    global convert_button, pause_resume_button, stop_processing_button, load_files_button
    global clear_all_data_button, save_settings_button, verzio_log_button, exit_program_button
    global cancel_button, tree, status_label, loading_status_label, progress_bar
    global progress_percent_label, program_start_time_label, program_elapsed_time_label
    global session_elapsed_time_label, remaining_time_label, estimated_completion_label
    global processing_completed_label

    logger.debug("GUI inicializálás elkezdődött")
    root.grid_rowconfigure(1, weight=1)
    root.grid_columnconfigure(0, weight=1)

    # Felső frame: Beállítások
    top_frame = ttk.LabelFrame(root, text="Beállítások")
    top_frame.grid(row=0, column=0, padx=10, pady=5, sticky="ew")

    ttk.Label(top_frame, text="Bemeneti mappa:").grid(row=0, column=0, padx=5, pady=2, sticky="w")
    input_dir_entry = ttk.Entry(top_frame, textvariable=input_dir_path_var, width=50)
    input_dir_entry.grid(row=0, column=1, padx=5, pady=2)
    browse_input_folder_button = ttk.Button(top_frame, text="Tallóz", command=browse_input_folder)
    browse_input_folder_button.grid(row=0, column=2, padx=5, pady=2)

    ttk.Label(top_frame, text="Kimeneti mappa:").grid(row=1, column=0, padx=5, pady=2, sticky="w")
    output_dir_entry = ttk.Entry(top_frame, textvariable=output_dir_path_var, width=50)
    output_dir_entry.grid(row=1, column=1, padx=5, pady=2)
    browse_output_folder_button = ttk.Button(top_frame, text="Tallóz", command=browse_output_folder)
    browse_output_folder_button.grid(row=1, column=2, padx=5, pady=2)

    ttk.Label(top_frame, text="Napló mappa:").grid(row=2, column=0, padx=5, pady=2, sticky="w")
    log_output_dir_entry = ttk.Entry(top_frame, textvariable=log_output_dir_path_var, width=50)
    log_output_dir_entry.grid(row=2, column=1, padx=5, pady=2)
    select_log_output_dir_button = ttk.Button(top_frame, text="Tallóz", command=select_log_output_dir)
    select_log_output_dir_button.grid(row=2, column=2, padx=5, pady=2)

    ttk.Label(top_frame, text="FFmpeg/FFprobe útvonal:").grid(row=3, column=0, padx=5, pady=2, sticky="w")
    ffmpeg_path_entry = ttk.Entry(top_frame, textvariable=ffmpeg_path_var, width=25)
    ffmpeg_path_entry.grid(row=3, column=1, padx=5, pady=2, sticky="w")
    ffprobe_path_entry = ttk.Entry(top_frame, textvariable=ffprobe_path_var, width=24)
    ffprobe_path_entry.grid(row=3, column=1, padx=5, pady=2, sticky="e")
    set_ffmpeg_paths_button = ttk.Button(top_frame, text="Beállít", command=set_ffmpeg_paths)
    set_ffmpeg_paths_button.grid(row=3, column=2, padx=5, pady=2)

    ttk.Label(top_frame, text="Profil:").grid(row=4, column=0, padx=5, pady=2, sticky="w")
    profile_menu = ttk.OptionMenu(top_frame, selected_profile_name_var, selected_profile_name_var.get(), *PROFILES.keys(),
                                  command=update_selected_profile_and_save_settings)
    profile_menu.grid(row=4, column=1, padx=5, pady=2, sticky="ew")

    ttk.Label(top_frame, text="Fájl típus:").grid(row=5, column=0, padx=5, pady=2, sticky="w")
    ttk.Radiobutton(top_frame, text="ch_YYYYMMDDHHMMSS", variable=file_type_var, value="ch", command=save_settings).grid(
        row=5, column=1, padx=5, pady=2, sticky="w")
    ttk.Radiobutton(top_frame, text="Egyéb (YYYY_MYD_HMS)", variable=file_type_var, value="other", command=save_settings).grid(
        row=5, column=1, padx=5, pady=2, sticky="e")

    ttk.Label(top_frame, text="Szálak száma:").grid(row=6, column=0, padx=5, pady=2, sticky="w")
    ttk.Spinbox(top_frame, from_=1, to=os.cpu_count() or 1, textvariable=num_threads_var, width=5, command=save_settings).grid(
        row=6, column=1, padx=5, pady=2, sticky="w")

    ttk.Label(top_frame, text="Napló formátumok:").grid(row=7, column=0, padx=5, pady=2, sticky="w")
    ttk.Checkbutton(top_frame, text="Excel", variable=excel_log_var, command=save_settings).grid(row=7, column=1, padx=5, pady=2, sticky="w")
    ttk.Checkbutton(top_frame, text="PDF", variable=pdf_log_var, command=save_settings).grid(row=7, column=1, padx=50, pady=2)
    ttk.Checkbutton(top_frame, text="TXT", variable=txt_log_var, command=save_settings).grid(row=7, column=1, padx=100, pady=2)
    ttk.Checkbutton(top_frame, text="JSON", variable=json_log_var, command=save_settings).grid(row=7, column=1, padx=150, pady=2, sticky="w")

    # Középső frame: Treeview
    middle_frame = ttk.Frame(root)
    middle_frame.grid(row=1, column=0, padx=10, pady=5, sticky="nsew")
    middle_frame.grid_rowconfigure(0, weight=1)
    middle_frame.grid_columnconfigure(0, weight=1)

    columns = (
        "Index", "Fájlnév", "Bemenet (MB)", "Időtartam", "Kész%", "Futás", "Kimenet", "Méret", "Idő", "Tömörítés",
        "Kezdő Idő", "Végző Idő", "Futásidő", "Státusz", "Típus", "InputPath", "DurationSec"
    )
    tree = ttk.Treeview(middle_frame, columns=columns, show="headings")
    for col in columns:
        tree.heading(col, text=col)
        tree.column(col, width=100, anchor="center")
    tree.column("Index", width=50)
    tree.column("Fájlnév", width=150, anchor="w")
    tree.column("Bemenet (MB)", width=100)
    tree.column("Időtartam", width=80)
    tree.column("Kimenet", width=150, anchor="w")
    tree["displaycolumns"] = (
        "Index", "Fájlnév", "Bemenet (MB)", "Időtartam", "Kész%", "Futás", "Kimenet", "Méret", "Idő", "Tömörítés",
        "Kezdő Idő", "Végző Idő", "Futásidő", "Státusz", "Típus"
    )
    tree_scrollbar_y = ttk.Scrollbar(middle_frame, orient="vertical", command=tree.yview)
    tree_scrollbar_x = ttk.Scrollbar(middle_frame, orient="horizontal", command=tree.xview)
    tree.configure(yscrollcommand=tree_scrollbar_y.set, xscrollcommand=tree_scrollbar_x.set)
    tree.grid(row=0, column=0, sticky="nsew")
    tree_scrollbar_y.grid(row=0, column=1, sticky="ns")
    tree_scrollbar_x.grid(row=1, column=0, sticky="ew")

    # Alsó frame: Gombok és státusz
    bottom_frame = ttk.Frame(root)
    bottom_frame.grid(row=2, column=0, padx=10, pady=5, sticky="ew")

    button_frame = ttk.Frame(bottom_frame)
    button_frame.grid(row=0, column=0, columnspan=3, pady=10, sticky="ew")
    button_frame.grid_columnconfigure(0, weight=1)
    button_frame.grid_columnconfigure(1, weight=1)
    button_frame.grid_columnconfigure(2, weight=1)

    convert_button = ttk.Button(button_frame, text="Start", command=start_processing_thread)
    convert_button.grid(row=0, column=0, padx=5, pady=5, sticky="ew")
    pause_resume_button = ttk.Button(button_frame, text="Szünet/Folytatás", command=pause_resume_processing)
    pause_resume_button.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
    stop_processing_button = ttk.Button(button_frame, text="Stop", command=stop_processing)
    stop_processing_button.grid(row=0, column=2, padx=5, pady=5, sticky="ew")
    load_files_button = ttk.Button(button_frame, text="Fájlok betöltése", command=load_files_to_treeview)
    load_files_button.grid(row=1, column=0, padx=5, pady=5, sticky="ew")
    save_settings_button = ttk.Button(button_frame, text="Beállítások mentése", command=save_settings)
    save_settings_button.grid(row=1, column=1, padx=5, pady=5, sticky="ew")
    clear_all_data_button = ttk.Button(button_frame, text="Adatok törlése", command=clear_all_data)
    clear_all_data_button.grid(row=1, column=2, padx=5, pady=5, sticky="ew")
    verzio_log_button = ttk.Button(button_frame, text="Verzió log", command=open_verzio_log)
    verzio_log_button.grid(row=2, column=0, padx=5, pady=5, sticky="ew")
    exit_program_button = ttk.Button(button_frame, text="Kilépés", command=exit_program)
    exit_program_button.grid(row=2, column=1, padx=5, pady=5, sticky="ew")
    cancel_button = ttk.Button(button_frame, text="Mégse", command=cancel_processing)
    cancel_button.grid(row=2, column=2, padx=5, pady=5, sticky="ew")

    status_label = ttk.Label(bottom_frame, text="Készenlétben.", anchor="w")
    status_label.grid(row=1, column=0, columnspan=3, padx=5, pady=2, sticky="ew")
    loading_status_label = ttk.Label(bottom_frame, text="", anchor="w", foreground="blue")
    loading_status_label.grid(row=2, column=0, columnspan=3, padx=5, pady=2, sticky="ew")
    progress_bar = ttk.Progressbar(bottom_frame, variable=progress_var, maximum=100)
    progress_bar.grid(row=3, column=0, columnspan=2, padx=5, pady=2, sticky="ew")
    progress_percent_label = ttk.Label(bottom_frame, text="0.0 %", width=8)
    progress_percent_label.grid(row=3, column=2, padx=5, pady=2)
    program_start_time_label = ttk.Label(bottom_frame, text="Program kezdési időpontja: --:--:--", anchor="center")
    program_start_time_label.grid(row=4, column=0, columnspan=3, padx=5, pady=2, sticky="ew")
    program_elapsed_time_label = ttk.Label(bottom_frame, text="Program futási ideje: 00:00:00", anchor="center")
    program_elapsed_time_label.grid(row=5, column=0, columnspan=3, padx=5, pady=2, sticky="ew")
    session_elapsed_time_label = ttk.Label(bottom_frame, text="Munkamenet futási ideje:  00:00:00", anchor="center")
    session_elapsed_time_label.grid(row=6, column=0, columnspan=3, padx=5, pady=2, sticky="ew")
    remaining_time_label = ttk.Label(bottom_frame, text="Hátralévő idő: --:--:--", anchor="center")
    remaining_time_label.grid(row=7, column=0, columnspan=3, padx=5, pady=2, sticky="ew")
    estimated_completion_label = ttk.Label(bottom_frame, text="Vélt záró időpont: --:--:--", anchor="center")
    estimated_completion_label.grid(row=8, column=0, columnspan=3, padx=5, pady=2, sticky="ew")
    processing_completed_label = ttk.Label(bottom_frame, text="Lezárt időpont: --:--:--", anchor="center")
    processing_completed_label.grid(row=9, column=0, columnspan=3, padx=5, pady=2, sticky="ew")

    logger.info("GUI inicializálás sikeresen befejeződött")

# --- Főprogram ---
if __name__ == "__main__":
    logger.info(f"Program indítása: {SCRIPT_NAME}")
    program_start_time = time.time()
    program_start_time_label.config(text=f"Program kezdési időpontja: {time.strftime('%H:%M:%S', time.localtime(program_start_time))}")

    # Beállítások és munkamenet állapot betöltése
    load_app_settings()
    session_loaded_and_continued = load_session_state()

    # GUI inicializálása
    initialize_gui()

    # Tkinter események
    root.update_idletasks()

    # GUI kezdeti állapot beállítása
    set_ui_processing_state(False)

    # Időkijelzők indítása
    update_time_displays()

    # Fájlok betöltése, ha van bemeneti mappa
    if input_dir_path_var.get():
        logger.debug("Bemeneti mappa betöltve, fájlok betöltése a Treeview-ba")
        load_files_to_treeview()

    # Fő ciklus
    root.mainloop()
