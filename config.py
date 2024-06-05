import os
import sys
import json
import logging
from tkinter import messagebox
from tkinter import ttk


def apply_style(root):
    style = ttk.Style(root)
    style.theme_use('clam')
    theme_color = "#f0f0f0"
    accent_color = "#1d79ac"
    text_color = "#000000"
    style.configure("TFrame", background=theme_color)
    style.configure("TButton", font=("Arial", 12), background=theme_color, foreground=text_color)
    style.map("TButton", background=[('active', accent_color), ('!disabled', theme_color)])
    style.configure("TLabel", font=("Arial", 12), background=theme_color, foreground=text_color)
    style.configure("TEntry", font=("Arial", 12), relief="flat", background=theme_color)
    style.configure("TCheckbutton", font=("Arial", 12), background=theme_color, foreground=text_color)

def load_config():
    try:
        config_path = os.path.join(sys._MEIPASS, "config.json") if getattr(sys, 'frozen', False) else "config.json"
        with open(config_path, 'r') as config_file:
            config = json.load(config_file)
        logging.info("Configuration loaded successfully.")
        return config
    except Exception as e:
        logging.error(f"Error loading config file: {e}")
        messagebox.showerror("Error", f"Failed to load config file: {str(e)}")
        return None