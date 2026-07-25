#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#========================================================================================
# Code developed by Eduardo Miguel Dias da Silva, FEUP Student, Mechanical Engineering
# Developed in the context of being a member of PST-Porto Space Team, ICARUS, 1U CubeSat
#========================================================================================

"""
===============================================================================
PROGRAM TO CALCULATE THE CENTER OF GRAVITY (CG) OF A CUBESAT
WITH AN INTERACTIVE TKINTER GUI (IMPROVED VERSION)
--------------------------------------------------------------------------------
Date  : 2024-12-30

This program exemplifies a professional tool to calculate the Center of Gravity (CG)
of a CubeSat, with checking of minimum and maximum distances between components, including:

  - Interactive GUI with two tabs (Main and Settings).
  - Multiple language support (Portuguese and English) with dynamic switching.
  - Functions to save and load settings (JSON file).
  - Visualization of the best configuration results (CG within the range).
  - Individual adjustment of masses, thicknesses, and distance constraints between pairs of components.
  - Definition of the desired CG range, and other extras.
  - Dynamic addition and removal of internal and external components.
  - For each component (internal and external), you may now input its actual
    center-of-mass (COM) position within the component. If the value is zero,
    the geometric center (thickness/2 or height/2) is used.
  - The algorithm now iterates over gap configurations (using branch-and-bound)
    for the movable internal components (all but the first and last, which are fixed).
    The last internal component’s effective COM is computed as:
         Total Height – (thickness_last – (user COM if provided, else thickness_last/2))
    A brief explanation is added in the CG Range tab, and the final result also
    shows the number of iterations run.
  
Requirements:
-------------
  - Python 3.x
  - tk/tkinter (native in Python)
  - itertools (native)
  - numpy (installed via pip or package manager)
  - json (native)
  - subprocess, sys, os (native)

Usage:
------
  python3 satelite_gui.py
===============================================================================
"""

import tkinter as tk
import tkinter.ttk as ttk
import tkinter.filedialog as fdlg
import tkinter.simpledialog as simpledialog
import json
import sys
import subprocess
import os
import itertools

# ---------------------------------------------------------------------
# 1) Auxiliary function to install numpy if possible
# ---------------------------------------------------------------------
def install_numpy_if_possible():
    """
    Tries to install NumPy via pip, unless the environment is
    externally managed (PEP 668). In that case, it shows a warning
    to install via apt-get or use a venv/conda.
    """
    externally_managed = False
    try:
        import sysconfig
        scheme_path = sysconfig.get_paths()["platlib"]
        marker_file = os.path.join(os.path.dirname(scheme_path), "EXTERNALLY-MANAGED")
        if os.path.exists(marker_file):
            externally_managed = True
    except:
        pass
    if externally_managed:
        print("This Python is externally managed (PEP 668).")
        print("Please install NumPy via your package manager, e.g.:")
        print("    sudo apt-get install python3-numpy")
        print("Or use a virtualenv/conda environment.")
        return
    print("Attempting to install 'numpy' in the current Python environment...")
    try:
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'numpy'])
        print("NumPy successfully installed.")
    except subprocess.CalledProcessError as e:
        print(f"Error installing 'numpy': {e}")
        print("Try using --user, creating a venv, or install via apt-get/conda.")
        sys.exit(1)

# ---------------------------------------------------------------------
# 2) Translations (PT and EN)
# ---------------------------------------------------------------------
LANG_TEXTS = {
    "pt": {
        "title": "Calculadora de CG para CubeSat",
        "tab_main": "Principal",
        "tab_settings": "Configurações",
        "btn_calculate": "Calcular CG",
        "lbl_components_int": "Componentes Internos (Massas/Espessuras)",
        "lbl_components_ext": "Componentes Externos",
        "lbl_range": "Faixa de CG Desejada\n(OBS: O primeiro componente é fixo no fundo e o último no topo)",
        "lbl_distances": "Distâncias entre Pares (Mínima e Máxima)",
        "lbl_component": "Componente",
        "lbl_mass": "Massa (g):",
        "lbl_thickness": "Espessura (mm):",
        "lbl_com": "Pos. do CG (mm):",
        "lbl_height": "Altura (mm):",
        "lbl_min_cg": "CG mínimo (mm):",
        "lbl_max_cg": "CG máximo (mm):",
        "lbl_total_height": "Altura Total CubeSat (mm):",
        "lbl_internal_gap": "Dist. Mín. Adj. (mm):",
        "lbl_dist": "Distância {A} - {B}:",
        "lbl_min": "Mín:",
        "lbl_max": "Máx:",
        "res_no_numpy": "Numpy não encontrado. Tente rodar o script novamente.\n",
        "res_error": "Erro ao ler parâmetros e executar cálculo: ",
        "res_best_config": "\nMelhor configuração encontrada!\n",
        "res_comp_height": "  {name} -> COM: {height:.2f} mm\n",
        "res_cg": "Centro de Gravidade (CG): {val:.2f} mm\nIterações: {iters}\n",
        "res_no_config": "\nNenhuma configuração válida encontrada dentro dos parâmetros desejados.\n\n",
        "res_error_iteration": "Erro durante a geração e teste de configurações: ",
        "lbl_language": "Idioma:",
        "lbl_load_config": "Carregar Config.",
        "lbl_save_config": "Salvar Config.",
        "msg_config_loaded": "Configurações carregadas com sucesso!\n",
        "msg_config_saved": "Configurações salvas com sucesso!\n",
        "default_config_name": "config.json"
    },
    "en": {
        "title": "CubeSat CG Calculator",
        "tab_main": "Main",
        "tab_settings": "Settings",
        "btn_calculate": "Calculate CG",
        "lbl_components_int": "Internal Components (Mass/Thickness)",
        "lbl_components_ext": "External Components",
        "lbl_range": "Desired CG Range\n(Note: First internal is fixed at bottom and last at top)",
        "lbl_distances": "Distances Between Pairs (Min & Max)",
        "lbl_component": "Component",
        "lbl_mass": "Mass (g):",
        "lbl_thickness": "Thickness (mm):",
        "lbl_com": "COM Height (mm):",
        "lbl_height": "Height (mm):",
        "lbl_min_cg": "Min CG (mm):",
        "lbl_max_cg": "Max CG (mm):",
        "lbl_total_height": "CubeSat Total Height (mm):",
        "lbl_internal_gap": "Internal Gap (mm):",
        "lbl_dist": "Distance {A} - {B}:",
        "lbl_min": "Min:",
        "lbl_max": "Max:",
        "res_no_numpy": "Numpy not found. Please rerun the script.\n",
        "res_error": "Error reading parameters or executing calculation: ",
        "res_best_config": "\nBest configuration found!\n",
        "res_comp_height": "  {name} -> COM: {height:.2f} mm\n",
        "res_cg": "Center of Gravity (CG): {val:.2f} mm\nIterations: {iters}\n",
        "res_no_config": "\nNo valid configuration found within the desired parameters.\n\n",
        "res_error_iteration": "Error during generation/testing of configurations: ",
        "lbl_language": "Language:",
        "lbl_load_config": "Load Config",
        "lbl_save_config": "Save Config",
        "msg_config_loaded": "Configuration successfully loaded!\n",
        "msg_config_saved": "Configuration successfully saved!\n",
        "default_config_name": "config.json"
    }
}

# ---------------------------------------------------------------------
# 3) Main application class
# ---------------------------------------------------------------------
class SateliteApp:
    """
    Main application class, containing all GUI elements and the CG calculation logic.
    """
    def __init__(self, master):
        self.master = master
        self.current_lang = "en"

        self.style = ttk.Style(self.master)
        try:
            self.style.theme_use('clam')
        except:
            pass
        self.style.configure('TLabelFrame', font=('Arial', 11, 'bold'), padding=10)
        self.style.configure('TLabel', font=('Arial', 10))
        self.style.configure('TButton', font=('Arial', 10, 'bold'), padding=5)
        self.style.configure('TEntry', padding=5)

        self.master.title(self.tr("title"))
        self.master.geometry("1600x500")
        self.master.resizable(True, True)

        # Dynamic Internal and External Components
        self.internal_components = [
            {'name': 'PL', 'mass': tk.DoubleVar(value=100.0),
             'thickness': tk.DoubleVar(value=20.0),
             'com': tk.DoubleVar(value=10.0)},
            {'name': 'EPS', 'mass': tk.DoubleVar(value=329.7),
             'thickness': tk.DoubleVar(value=30.0),
             'com': tk.DoubleVar(value=15.0)},
            {'name': 'OBC', 'mass': tk.DoubleVar(value=100.0),
             'thickness': tk.DoubleVar(value=15.0),
             'com': tk.DoubleVar(value=7.5)},
            {'name': 'RAD', 'mass': tk.DoubleVar(value=100.0),
             'thickness': tk.DoubleVar(value=15.0),
             'com': tk.DoubleVar(value=7.5)}
        ]
        self.external_components = [
            {'name': 'Solar', 'mass': tk.DoubleVar(value=57.0),
             'height': tk.DoubleVar(value=104.5),
             'com': tk.DoubleVar(value=104.5)},
            {'name': 'Antenna', 'mass': tk.DoubleVar(value=90.0),
             'height': tk.DoubleVar(value=103.5),
             'com': tk.DoubleVar(value=103.5)},
            {'name': 'Chassis', 'mass': tk.DoubleVar(value=120.0),
             'height': tk.DoubleVar(value=48.0),
             'com': tk.DoubleVar(value=48.0)}
        ]
        self._update_internal_component_pairs()

        # Other Input Variables
        self.var_total_height = tk.DoubleVar(value=95.2)
        self.var_target_min = tk.DoubleVar(value=40.0)
        self.var_target_max = tk.DoubleVar(value=60.0)

        # Creating Notebook tabs (Main and Settings)
        self.notebook = ttk.Notebook(self.master)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        self.tab_main = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_main, text=self.tr("tab_main"))
        self.tab_settings = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_settings, text=self.tr("tab_settings"))

        self._build_tab_main()
        self._build_tab_settings()

    # -------------------------------------------------------------------------
    # Translation function
    # -------------------------------------------------------------------------
    def tr(self, key):
        return LANG_TEXTS[self.current_lang].get(key, key)

    def set_language(self, lang):
        if lang in LANG_TEXTS:
            self.current_lang = lang
            self.master.title(self.tr("title"))
            self.notebook.tab(self.tab_main, text=self.tr("tab_main"))
            self.notebook.tab(self.tab_settings, text=self.tr("tab_settings"))
            self._update_tab_main_texts()
            self._update_tab_settings_texts()

    # -------------------------------------------------------------------------
    # Build Main Tab
    # -------------------------------------------------------------------------
    def _build_tab_main(self):
        self.frame_main_top = ttk.Frame(self.tab_main)
        self.frame_main_top.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Internal Components Panel
        self.frame_comp_int = ttk.LabelFrame(self.frame_main_top, text=self.tr("lbl_components_int"))
        self.frame_comp_int.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        self._build_dynamic_internal_components()

        # External Components Panel
        self.frame_comp_ext = ttk.LabelFrame(self.frame_main_top, text=self.tr("lbl_components_ext"))
        self.frame_comp_ext.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        self._build_dynamic_external_components()

        # CG Range Panel
        self.frame_cg_range = ttk.LabelFrame(self.frame_main_top, text=self.tr("lbl_range"))
        self.frame_cg_range.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        self._fill_frame_cg_range()

        # Distances Constraints Panel
        self.frame_dists = ttk.LabelFrame(self.frame_main_top, text=self.tr("lbl_distances"))
        self.frame_dists.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        self._build_dynamic_internal_distances()

        # -----------------------------------------------------------------
        # NEW: Diagram Panel (shows your provided image)
        # -----------------------------------------------------------------
        self.frame_diagram = ttk.LabelFrame(self.frame_main_top, text="Diagram")
        self.frame_diagram.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        try:
            # build an absolute path to resources/cubesat_diagram.png
            script_dir = os.path.dirname(os.path.abspath(__file__))
            resources_dir = os.path.join(script_dir, 'resources')
            diagram_path = os.path.join(resources_dir, 'cubesat_diagram.png')

            # load it
            self.diagram_image = tk.PhotoImage(file=diagram_path)
            lbl_img = ttk.Label(self.frame_diagram, image=self.diagram_image)
            lbl_img.pack(fill=tk.BOTH, expand=True)
        except Exception as e:
            lbl_err = ttk.Label(
                self.frame_diagram,
                text=f"Unable to load image:\n{e}"
            )
            lbl_err.pack(fill=tk.BOTH, expand=True)

        # Bottom: Calculate button and results
        self.frame_main_bottom = ttk.Frame(self.tab_main)
        self.frame_main_bottom.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.btn_calcular = ttk.Button(self.frame_main_bottom, text=self.tr("btn_calculate"), command=self._on_calcular)
        self.btn_calcular.pack(side=tk.LEFT, padx=5, pady=5)
        self.text_result = tk.Text(self.frame_main_bottom, height=20, width=100)
        self.text_result.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.text_result.configure(state=tk.DISABLED)

    # -------------------------------------------------------------------------
    # Dynamic Internal Components
    # -------------------------------------------------------------------------
    def _build_dynamic_internal_components(self):
        for widget in self.frame_comp_int.winfo_children():
            widget.destroy()
        # Headers
        ttk.Label(self.frame_comp_int, text=self.tr("lbl_component")).grid(row=0, column=0, padx=5)
        ttk.Label(self.frame_comp_int, text=self.tr("lbl_mass")).grid(row=0, column=1, padx=5)
        ttk.Label(self.frame_comp_int, text=self.tr("lbl_thickness")).grid(row=0, column=2, padx=5)
        ttk.Label(self.frame_comp_int, text=self.tr("lbl_com")).grid(row=0, column=3, padx=5)
        for i, comp in enumerate(self.internal_components):
            name_label = ttk.Label(self.frame_comp_int, text=comp['name'])
            name_label.grid(row=i+1, column=0, padx=5)
            name_label.bind("<Double-Button-1>", lambda e, idx=i: self._edit_internal_component_name(idx))
            ttk.Entry(self.frame_comp_int, textvariable=comp['mass'], width=10).grid(row=i+1, column=1, padx=5)
            ttk.Entry(self.frame_comp_int, textvariable=comp['thickness'], width=10).grid(row=i+1, column=2, padx=5)
            ttk.Entry(self.frame_comp_int, textvariable=comp['com'], width=10).grid(row=i+1, column=3, padx=5)
        btn_add_int = ttk.Button(self.frame_comp_int, text="Add Internal Component", command=self._add_internal_component)
        btn_add_int.grid(row=len(self.internal_components)+1, column=0, columnspan=2, pady=5)
        btn_remove_int = ttk.Button(self.frame_comp_int, text="Remove Internal Component", command=self._remove_internal_component)
        btn_remove_int.grid(row=len(self.internal_components)+1, column=2, columnspan=2, pady=5)

    def _edit_internal_component_name(self, idx):
        new_name = simpledialog.askstring("Edit Internal Component Name",
                                          "Enter new name:",
                                          initialvalue=self.internal_components[idx]['name'])
        if new_name:
            self.internal_components[idx]['name'] = new_name
            self._build_dynamic_internal_components()
            self._update_internal_component_pairs()
            self._build_dynamic_internal_distances()

    def _add_internal_component(self):
        new_name = simpledialog.askstring("New Internal Component", "Enter component name:")
        if not new_name:
            new_name = f"INT{len(self.internal_components)+1}"
        new_comp = {
            'name': new_name,
            'mass': tk.DoubleVar(value=0.0),
            'thickness': tk.DoubleVar(value=0.0),
            'com': tk.DoubleVar(value=0.0)
        }
        self.internal_components.append(new_comp)
        self._build_dynamic_internal_components()
        self._update_internal_component_pairs()
        self._build_dynamic_internal_distances()

    def _remove_internal_component(self):
        if len(self.internal_components) > 2:
            self.internal_components.pop()
            self._build_dynamic_internal_components()
            self._update_internal_component_pairs()
            self._build_dynamic_internal_distances()
        else:
            self._append_texto("At least 2 internal components are required.\n")

    def _update_internal_component_pairs(self):
        n = len(self.internal_components)
        self.internal_component_pairs = list(itertools.combinations(range(n), 2))
        self.min_dist_vars_internal = {}
        self.max_dist_vars_internal = {}
        for pair in self.internal_component_pairs:
            self.min_dist_vars_internal[pair] = tk.DoubleVar(value=0.0)
            self.max_dist_vars_internal[pair] = tk.DoubleVar(value=9999.0)

    def _build_dynamic_internal_distances(self):
        for widget in self.frame_dists.winfo_children():
            widget.destroy()
        ttk.Label(self.frame_dists, text="Internal Component Distances").grid(row=0, column=0, columnspan=5, pady=5)
        row_idx = 1
        for pair, min_var in self.min_dist_vars_internal.items():
            i, j = pair
            comp_i = self.internal_components[i]['name']
            comp_j = self.internal_components[j]['name']
            label_text = self.tr("lbl_dist").format(A=comp_i, B=comp_j)
            ttk.Label(self.frame_dists, text=label_text).grid(row=row_idx, column=0, sticky=tk.W, padx=5, pady=2)
            ttk.Label(self.frame_dists, text=self.tr("lbl_min")).grid(row=row_idx, column=1, sticky=tk.E)
            ttk.Entry(self.frame_dists, textvariable=min_var, width=6).grid(row=row_idx, column=2, sticky=tk.W)
            ttk.Label(self.frame_dists, text=self.tr("lbl_max")).grid(row=row_idx, column=3, sticky=tk.E)
            ttk.Entry(self.frame_dists, textvariable=self.max_dist_vars_internal[pair], width=6).grid(row=row_idx, column=4, sticky=tk.W)
            row_idx += 1

    # -------------------------------------------------------------------------
    # Dynamic External Components
    # -------------------------------------------------------------------------
    def _build_dynamic_external_components(self):
        for widget in self.frame_comp_ext.winfo_children():
            widget.destroy()
        ttk.Label(self.frame_comp_ext, text=self.tr("lbl_component")).grid(row=0, column=0, padx=5)
        ttk.Label(self.frame_comp_ext, text=self.tr("lbl_mass")).grid(row=0, column=1, padx=5)
        ttk.Label(self.frame_comp_ext, text=self.tr("lbl_height")).grid(row=0, column=2, padx=5)
        ttk.Label(self.frame_comp_ext, text=self.tr("lbl_com")).grid(row=0, column=3, padx=5)
        for i, comp in enumerate(self.external_components):
            ttk.Label(self.frame_comp_ext, text=comp['name']).grid(row=i+1, column=0, padx=5)
            ttk.Entry(self.frame_comp_ext, textvariable=comp['mass'], width=10).grid(row=i+1, column=1, padx=5)
            ttk.Entry(self.frame_comp_ext, textvariable=comp['height'], width=10).grid(row=i+1, column=2, padx=5)
            ttk.Entry(self.frame_comp_ext, textvariable=comp.setdefault('com', tk.DoubleVar(value=0.0)), width=10).grid(row=i+1, column=3, padx=5)
        btn_add_ext = ttk.Button(self.frame_comp_ext, text="Add External Component", command=self._add_external_component)
        btn_add_ext.grid(row=len(self.external_components)+1, column=0, columnspan=2, pady=5)
        btn_remove_ext = ttk.Button(self.frame_comp_ext, text="Remove External Component", command=self._remove_external_component)
        btn_remove_ext.grid(row=len(self.external_components)+1, column=2, columnspan=2, pady=5)

    def _add_external_component(self):
        new_name = simpledialog.askstring("New External Component", "Enter component name:")
        if not new_name:
            new_name = f"EXT{len(self.external_components)+1}"
        new_comp = {
            'name': new_name,
            'mass': tk.DoubleVar(value=0.0),
            'height': tk.DoubleVar(value=0.0),
            'com': tk.DoubleVar(value=0.0)
        }
        self.external_components.append(new_comp)
        self._build_dynamic_external_components()

    def _remove_external_component(self):
        if self.external_components:
            self.external_components.pop()
            self._build_dynamic_external_components()
        else:
            self._append_texto("No external components to remove.\n")

    # -------------------------------------------------------------------------
    # CG Range Panel
    # -------------------------------------------------------------------------
    def _fill_frame_cg_range(self):
        ttk.Label(self.frame_cg_range, text=self.tr("lbl_min_cg")).grid(row=0, column=0, sticky=tk.W)
        ttk.Entry(self.frame_cg_range, textvariable=self.var_target_min, width=10).grid(row=0, column=1)
        ttk.Label(self.frame_cg_range, text=self.tr("lbl_max_cg")).grid(row=1, column=0, sticky=tk.W)
        ttk.Entry(self.frame_cg_range, textvariable=self.var_target_max, width=10).grid(row=1, column=1)
        ttk.Label(self.frame_cg_range, text=self.tr("lbl_total_height")).grid(row=2, column=0, sticky=tk.W)
        ttk.Entry(self.frame_cg_range, textvariable=self.var_total_height, width=10).grid(row=2, column=1)
        justification = ("Note: The first internal component is fixed at the bottom and "
                         "the last at the top (position = Total Height - thickness_last + COM_last). "
                         "Gaps for intermediate components are iterated using the min/max distance constraints.")
        ttk.Label(self.frame_cg_range, text=justification, wraplength=250).grid(row=3, column=0, columnspan=2, pady=5)

    # -------------------------------------------------------------------------
    # Update Tab Texts
    # -------------------------------------------------------------------------
    def _update_tab_main_texts(self):
        self.frame_comp_int.config(text=self.tr("lbl_components_int"))
        self.frame_comp_ext.config(text=self.tr("lbl_components_ext"))
        self.frame_cg_range.config(text=self.tr("lbl_range"))
        self.frame_dists.config(text=self.tr("lbl_distances"))
        self.btn_calcular.config(text=self.tr("btn_calculate"))
        self._build_dynamic_internal_components()
        self._build_dynamic_external_components()
        self._build_dynamic_internal_distances()

    def _build_tab_settings(self):
        frame_lang = ttk.LabelFrame(self.tab_settings, text=self.tr("tab_settings"))
        frame_lang.pack(side=tk.TOP, fill=tk.X, padx=10, pady=10)
        ttk.Label(frame_lang, text=self.tr("lbl_language")).pack(side=tk.LEFT, padx=5)
        self.cmb_language = ttk.Combobox(frame_lang, values=["pt", "en"], width=5)
        self.cmb_language.set(self.current_lang)
        self.cmb_language.pack(side=tk.LEFT, padx=5)
        self.btn_apply_lang = ttk.Button(frame_lang, text="OK", command=self._on_apply_lang)
        self.btn_apply_lang.pack(side=tk.LEFT, padx=5)
        frame_config = ttk.LabelFrame(self.tab_settings)
        frame_config.config(text=self.tr("tab_settings"))
        frame_config.pack(side=tk.TOP, fill=tk.X, padx=10, pady=10)
        self.btn_load_config = ttk.Button(frame_config, text=self.tr("lbl_load_config"), command=self._on_load_config)
        self.btn_load_config.pack(side=tk.LEFT, padx=5, pady=5)
        self.btn_save_config = ttk.Button(frame_config, text=self.tr("lbl_save_config"), command=self._on_save_config)
        self.btn_save_config.pack(side=tk.LEFT, padx=5, pady=5)

    def _update_tab_settings_texts(self):
        for f in self.tab_settings.winfo_children():
            if isinstance(f, ttk.LabelFrame):
                f.config(text=self.tr("tab_settings"))
                for child in f.winfo_children():
                    if isinstance(child, ttk.Label):
                        if child.cget("text") in [LANG_TEXTS["pt"]["lbl_language"], LANG_TEXTS["en"]["lbl_language"]]:
                            child.config(text=self.tr("lbl_language"))
                    if isinstance(child, ttk.Button):
                        txt = child.cget("text")
                        if txt in [LANG_TEXTS["pt"]["lbl_load_config"], LANG_TEXTS["en"]["lbl_load_config"]]:
                            child.config(text=self.tr("lbl_load_config"))
                        elif txt in [LANG_TEXTS["pt"]["lbl_save_config"], LANG_TEXTS["en"]["lbl_save_config"]]:
                            child.config(text=self.tr("lbl_save_config"))

    def _on_apply_lang(self):
        new_lang = self.cmb_language.get()
        if new_lang in ("pt", "en"):
            self.set_language(new_lang)

    # -------------------------------------------------------------------------
    # Save and Load Configurations (JSON)
    # -------------------------------------------------------------------------
    def _on_save_config(self):
        filename = fdlg.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            initialfile=self.tr("default_config_name")
        )
        if not filename:
            return
        cfg = self._export_config()
        try:
            with open(filename, "w", encoding="utf-8") as f:
                json.dump(cfg, f, indent=2)
            self._append_texto(self.tr("msg_config_saved"))
        except Exception as e:
            self._append_texto(f"{self.tr('res_error')}{str(e)}\n")

    def _on_load_config(self):
        filename = fdlg.askopenfilename(
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        if not filename:
            return
        try:
            with open(filename, "r", encoding="utf-8") as f:
                cfg = json.load(f)
            # Rebuild internal components
            new_internal = []
            for comp in cfg.get("internal_components", []):
                new_internal.append({
                    'name': comp.get("name", ""),
                    'mass': tk.DoubleVar(value=comp.get("mass", 0.0)),
                    'thickness': tk.DoubleVar(value=comp.get("thickness", 0.0)),
                    'com': tk.DoubleVar(value=comp.get("com", 0.0))
                })
            self.internal_components = new_internal
            # Rebuild external components
            new_external = []
            for comp in cfg.get("external_components", []):
                new_external.append({
                    'name': comp.get("name", ""),
                    'mass': tk.DoubleVar(value=comp.get("mass", 0.0)),
                    'height': tk.DoubleVar(value=comp.get("height", 0.0)),
                    'com': tk.DoubleVar(value=comp.get("com", 0.0))
                })
            self.external_components = new_external

            self.var_total_height.set(cfg.get("total_height", 98.0))
            self.var_target_min.set(cfg.get("target_min", 40.0))
            self.var_target_max.set(cfg.get("target_max", 60.0))
            self._update_internal_component_pairs()
            min_dists = cfg.get("min_dists_internal", {})
            max_dists = cfg.get("max_dists_internal", {})
            for pair in self.internal_component_pairs:
                key = f"{pair[0]}_{pair[1]}"
                if key in min_dists:
                    self.min_dist_vars_internal[pair].set(min_dists[key])
                if key in max_dists:
                    self.max_dist_vars_internal[pair].set(max_dists[key])
            if "language" in cfg:
                self.set_language(cfg["language"])
            self._build_dynamic_internal_components()
            self._build_dynamic_external_components()
            self._build_dynamic_internal_distances()
            self._append_texto(self.tr("msg_config_loaded"))
        except Exception as e:
            self._append_texto(f"{self.tr('res_error')}{str(e)}\n")

    def _export_config(self):
        data = {
            "internal_components": [
                {"name": comp['name'],
                 "mass": comp['mass'].get(),
                 "thickness": comp['thickness'].get(),
                 "com": comp['com'].get()}
                for comp in self.internal_components
            ],
            "external_components": [
                {"name": comp['name'],
                 "mass": comp['mass'].get(),
                 "height": comp['height'].get(),
                 "com": comp['com'].get()}
                for comp in self.external_components
            ],
            "total_height": self.var_total_height.get(),
            "target_min": self.var_target_min.get(),
            "target_max": self.var_target_max.get(),
            "min_dists_internal": {
                f"{i}_{j}": self.min_dist_vars_internal[(i, j)].get()
                for (i, j) in self.internal_component_pairs
            },
            "max_dists_internal": {
                f"{i}_{j}": self.max_dist_vars_internal[(i, j)].get()
                for (i, j) in self.internal_component_pairs
            },
            "language": self.current_lang
        }
        return data

    # -------------------------------------------------------------------------
    # Calculation with Iterative Search (Branch-and-Bound)
    # -------------------------------------------------------------------------
    def _on_calcular(self):
        self._limpar_texto()
        try:
            import numpy as np
        except ImportError:
            self._append_texto(self.tr("res_no_numpy"))
            return
        try:
            n_int = len(self.internal_components)
            if n_int < 2:
                self._append_texto("At least 2 internal components are required.\n")
                return

            internal_masses = np.array([comp['mass'].get() for comp in self.internal_components], dtype=float)
            internal_thicknesses = np.array([comp['thickness'].get() for comp in self.internal_components], dtype=float)
            external_masses = np.array([comp['mass'].get() for comp in self.external_components], dtype=float) if self.external_components else np.array([])
            effective_external = []
            for comp in self.external_components:
                com_val = comp['com'].get()
                if com_val == 0:
                    com_val = comp['height'].get() / 2.0
                effective_external.append(com_val)
            effective_external = np.array(effective_external, dtype=float)
            total_mass_internal = sum(internal_masses)
            total_mass_external = sum(external_masses)
            total_height = self.var_total_height.get()
            target_range = (self.var_target_min.get(), self.var_target_max.get())
            ideal_cg = total_height / 2.0

            num_gaps = n_int - 2
            gap_ranges = []
            for i in range(num_gaps):
                key = (i, i+1)
                min_gap = self.min_dist_vars_internal[key].get()
                max_gap = self.max_dist_vars_internal[key].get()
                gap_ranges.append(range(int(min_gap), int(max_gap)+1))

            iteration_counter = 0
            best_loss = float('inf')
            best_gaps = None
            best_internal_effective = None
            best_overall_cg = None

            def search_gap_config(current_index, current_gaps, current_gap_sum):
                nonlocal iteration_counter, best_loss, best_gaps, best_internal_effective, best_overall_cg
                remaining_min = 0
                for idx in range(current_index, num_gaps):
                    remaining_min += min(gap_ranges[idx])
                provisional_height = sum(internal_thicknesses[:-1]) + current_gap_sum + remaining_min
                last_com = self.internal_components[-1]['com'].get()
                if last_com == 0:
                    last_com = internal_thicknesses[-1] / 2.0
                effective_last = total_height - (internal_thicknesses[-1] - last_com)
                if provisional_height > effective_last:
                    return

                if current_index == num_gaps:
                    iteration_counter += 1
                    effective = []
                    com0 = self.internal_components[0]['com'].get()
                    if com0 == 0:
                        com0 = internal_thicknesses[0] / 2.0
                    effective.append(com0)
                    for i in range(1, n_int - 1):
                        pos = 0.0
                        for k in range(i):
                            gap = current_gaps[k] if k < len(current_gaps) else 0.0
                            pos += internal_thicknesses[k] + gap
                        com_i = self.internal_components[i]['com'].get()
                        if com_i == 0:
                            com_i = internal_thicknesses[i] / 2.0
                        effective.append(pos + com_i)
                    last_com = self.internal_components[-1]['com'].get()
                    if last_com == 0:
                        last_com = internal_thicknesses[-1] / 2.0
                    effective.append(total_height - (internal_thicknesses[-1] - last_com))
                    effective = np.array(effective, dtype=float)

                    # Verify pairwise distances
                    for pair in self.internal_component_pairs:
                        i, j = pair
                        if effective[i] <= effective[j]:
                            gap_val = (effective[j] - internal_thicknesses[j]/2.0) - (effective[i] + internal_thicknesses[i]/2.0)
                        else:
                            gap_val = (effective[i] - internal_thicknesses[i]/2.0) - (effective[j] + internal_thicknesses[j]/2.0)
                        min_gap_val = self.min_dist_vars_internal[pair].get()
                        max_gap_val = self.max_dist_vars_internal[pair].get()
                        if gap_val < min_gap_val or gap_val > max_gap_val:
                            return

                    internal_moment = sum(effective * internal_masses)
                    external_moment = sum(effective_external * external_masses)
                    overall_cg = (internal_moment + external_moment) / (total_mass_internal + total_mass_external)
                    if overall_cg < target_range[0] or overall_cg > target_range[1]:
                        return
                    loss = abs(overall_cg - ideal_cg)
                    if loss < best_loss:
                        best_loss = loss
                        best_gaps = list(current_gaps)
                        best_internal_effective = effective
                        best_overall_cg = overall_cg
                    return

                for gap_val in gap_ranges[current_index]:
                    search_gap_config(current_index + 1, current_gaps + [gap_val], current_gap_sum + gap_val)

            search_gap_config(0, [], 0)

            if best_gaps is None:
                self._append_texto(self.tr("res_no_config"))
                return

            res = self.tr("res_best_config")
            res += "\nInternal Components (Effective COM positions):\n"
            for i, comp in enumerate(self.internal_components):
                res += self.tr("res_comp_height").format(name=comp['name'], height=best_internal_effective[i])
            res += "\nExternal Components:\n"
            for i, comp in enumerate(self.external_components):
                com_val = comp['com'].get()
                if com_val == 0:
                    com_val = comp['height'].get() / 2.0
                res += f"  {comp['name']} -> COM: {com_val:.2f} mm\n"
            res += "\nOverall CG: " + self.tr("res_cg").format(val=best_overall_cg, iters=iteration_counter)
            self._append_texto(res)
        except Exception as e:
            self._append_texto(f"{self.tr('res_error')}{str(e)}\n")

    def _build_distance_matrix_dynamic(self, dist_vars_dict, np, size):
        matrix = np.zeros((size, size), dtype=float)
        for i in range(size):
            matrix[i][i] = 0.0
        for pair, var in dist_vars_dict.items():
            i, j = pair
            matrix[i][j] = var.get()
            matrix[j][i] = var.get()
        return matrix

    def verifica_distancias_minmax(self, heights, thicknesses, min_distance_matrix, max_distance_matrix):
        n = len(heights)
        edges = {}
        for i in range(n):
            edges[i] = (heights[i] - thicknesses[i] / 2.0, heights[i] + thicknesses[i] / 2.0)
        for i in range(n):
            for j in range(i + 1, n):
                if heights[i] <= heights[j]:
                    lower, higher = i, j
                else:
                    lower, higher = j, i
                dist_between = edges[higher][0] - edges[lower][1]
                if dist_between < min_distance_matrix[lower][higher]:
                    return False
                if dist_between > max_distance_matrix[lower][higher]:
                    return False
        return True

    # -------------------------------------------------------------------------
    # Helper functions for the results text
    # -------------------------------------------------------------------------
    def _limpar_texto(self):
        self.text_result.configure(state=tk.NORMAL)
        self.text_result.delete("1.0", tk.END)
        self.text_result.configure(state=tk.DISABLED)

    def _append_texto(self, texto):
        self.text_result.configure(state=tk.NORMAL)
        self.text_result.insert(tk.END, texto)
        self.text_result.configure(state=tk.DISABLED)

# ---------------------------------------------------------------------
# 4) main
# ---------------------------------------------------------------------
def main():
    try:
        import numpy  # noqa
        print("NumPy is already installed. Continuing...")
    except ImportError:
        install_numpy_if_possible()
        try:
            import numpy  # noqa
            print("NumPy imported successfully after installation.")
        except ImportError:
            print("Failed to import 'numpy' even after attempted installation.")
            sys.exit(1)
    print("Starting application...")
    root = tk.Tk()
    app = SateliteApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
