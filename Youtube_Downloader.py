import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk # type: ignore
import customtkinter as ctk
import yt_dlp  # type: ignore
import threading
import os
import sys

def resource_path(relative_path):
    """Get the absolute path to a resource bundled with the app."""
    try:
        # PyInstaller creates a _MEIPASS folder to extract resources into.
        base_path = sys._MEIPASS
    except Exception:
        # Running in normal mode (not bundled).
        base_path = os.path.abspath(".")
    
    return os.path.join(base_path, relative_path)

# Validate YouTube Link
def validate_link(link):
    return link.startswith("http://") or link.startswith("https://")


# List Formats and Populate Dropdown
def list_formats():
    yt_link = link_entry.get().strip()
    if not validate_link(yt_link):
        finish_label.configure(text="Invalid YouTube Link!", text_color="red")
        return

    try:
        finish_label.configure(text="Fetching Formats...", text_color="blue")
        with yt_dlp.YoutubeDL() as ydl:
            info = ydl.extract_info(yt_link, download=False)
            formats = info.get('formats', [])

            # Populate dropdown with simplified summaries
            format_options = []
            format_id_map.clear()
            for fmt in formats:
                resolution = f"{fmt.get('height', 'Audio')}p" if fmt.get('height') else "Audio Only"
                fps = f"{fmt.get('fps', 'N/A')}fps" if fmt.get('fps') else ""
                codec = fmt.get('vcodec', 'N/A')
                summary = f"{resolution} - {fps} - {codec}".strip(" - ")
                format_options.append(summary)
                format_id_map[summary] = fmt['format_id']

            format_var.set("Select Format")
            format_dropdown.configure(values=format_options)

        finish_label.configure(text="Formats Fetched!", text_color="green")

    except Exception as e:
        finish_label.configure(text=f"Error: {str(e)}", text_color="red")


# Start Download in a Thread
def start_download_thread():
    threading.Thread(target=start_download, daemon=True).start()


# Start Download
def start_download():
    yt_link = link_entry.get().strip()
    if not validate_link(yt_link):
        finish_label.configure(text="Invalid YouTube Link!", text_color="red")
        return

    selected_format = format_var.get()
    if selected_format not in format_id_map:
        finish_label.configure(text="Select a valid format!", text_color="red")
        return

    format_id = format_id_map[selected_format]  # Get format ID

    try:
        finish_label.configure(text="Downloading...", text_color="blue")
        percentage_label.configure(text="0%")
        progress_bar.set(0)

        ydl_opts = {
            'format': format_id,  # Use selected format ID
            'outtmpl': os.path.join(os.getcwd(), '%(title)s.%(ext)s'),
            'progress_hooks': [on_progress],
            'noplaylist': True,
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([yt_link])

        finish_label.configure(text="Downloaded!", text_color="green")

    except Exception as e:
        finish_label.configure(text=f"Error: {str(e)}", text_color="red")


# Progress Hook
def on_progress(d):
    if d['status'] == 'downloading':
        total_bytes = d.get('total_bytes') or d.get('total_bytes_estimate', 0)
        downloaded_bytes = d.get('downloaded_bytes', 0)

        if total_bytes > 0:
            percentage = (downloaded_bytes / total_bytes) * 100
            percentage_label.configure(text=f"{percentage:.2f}%")
            progress_bar.set(percentage / 100)


# App Setup
ctk.set_appearance_mode("light")
ctk.set_default_color_theme("green")

app = ctk.CTk()
app.geometry("800x800")
app.title("YouTube Downloader")

# Set the app icon
app.iconbitmap(resource_path("icon.ico"))  # Use the resource_path function

# Load and set the background image
background_image_path = resource_path("background.jpg")  # Use the resource_path function
background_image = Image.open(background_image_path)
# Resize the image to fit the window size
background_image = background_image.resize((1920, 1080), Image.LANCZOS)
background_photo = ImageTk.PhotoImage(background_image)
background_label = tk.Label(app, image=background_photo)
background_label.place(relwidth=1, relheight=1)  # Fullscreen background


# Create UI Elements
title_label = ctk.CTkLabel(app, text="Insert YouTube Link", font=("Arial", 20), width=200, height=50)
title_label.pack(padx=10, pady=10)

link_var = tk.StringVar()
link_entry = ctk.CTkEntry(app, width=550, height=40, textvariable=link_var)
link_entry.pack(padx=10, pady=10)

# Finish download message
finish_label = ctk.CTkLabel(app, text="")
finish_label.pack(pady=5)

# Fetch Formats Button
fetch_formats_button = ctk.CTkButton(app, text="Fetch Available Formats", command=list_formats)
fetch_formats_button.pack(pady=10)

# Dropdown for Available Formats
format_var = ctk.StringVar(value="Select Format")
format_id_map = {}  # To map simplified descriptions to format IDs
format_dropdown = ctk.CTkOptionMenu(app, values=[], variable=format_var)
format_dropdown.pack(pady=10)

# Progress bar and percentage label
percentage_label = ctk.CTkLabel(app, text="0%")
percentage_label.pack(padx=10, pady=10)

progress_bar = ctk.CTkProgressBar(app, width=600)
progress_bar.set(0)
progress_bar.pack(padx=10, pady=10)

# Download button
download_button = ctk.CTkButton(app, text="Download Selected Format", command=start_download_thread)
download_button.pack(pady=10)

# Add a text watermark at the bottom
watermark_label = ctk.CTkLabel(
    app,
    text="© SaiAbhishekVissapragada 2024",
    font=("Arial", 12, "italic"),
    text_color="gray"
)
watermark_label.place(relx=0.5, rely=0.95, anchor="center")  # Position it at the bottom center



# Run the app
app.mainloop()
