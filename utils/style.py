import tkinter as tk
from tkinter import ttk

def apply_styles(root):
    style = ttk.Style(root)
    
    # Green button style
    style.configure(
        'GreenButton.TButton',
        background='green',
        foreground='black',
        padding=20,
        relief='flat',
        font=('Arial', 20, 'bold')
    )

    style.map(
        'GreenButton.TButton',
        background=[('active', 'darkgreen')],
        foreground=[('disabled', 'grey')]
    )

    style.configure(
        'Key.TButton',
        background='grey',
        foreground='black',
        font=('Arial', 18, 'bold'),
        padding=15
    )

    style.map(
        'Key.TButton',
        background=[('active', 'darkgreen')],
        foreground=[('disabled', 'grey')]
    )

    style.configure(
        'EntryLabel.TLabel',
        font=('Arial', 12)
    )

    style.configure(
        'EntryTitle.TLabel',
        anchor='center',
        font=('Arial', 18, 'bold', 'underline')
    )

    style.configure(
        'EntryText.TEntry',
        font=('Arial 12')
    )