
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
from urllib.request import urlopen, Request
from urllib.parse import urlencode
import io
import threading
import subprocess
import os

API = "https://wallhaven.cc/api/v1/search"
CACHE = os.path.expanduser("~/Projects/erynwall/cache")

os.makedirs(CACHE, exist_ok=True)

root = tk.Tk()
root.title("ErynWall")
root.geometry("950x650")
root.configure(bg="#202020")

images = []

def search_wallpapers():
    query = search_entry.get().strip()

    status.config(text="Завантаження...")
    search_button.config(state="disabled")

    def worker():
        try:
            params = {
                "q": query,
                "categories": "111",
                "purity": "100",
                "sorting": "date_added",
                "order": "desc",
                "page": 1
            }

            url = API + "?" + urlencode(params)

            request = Request(
                url,
                headers={"User-Agent": "ErynWall/1.0"}
            )

            with urlopen(request, timeout=20) as response:
                import json
                data = json.loads(response.read())

            root.after(0, lambda: display_results(data["data"]))

        except Exception as error:
            root.after(0, lambda: status.config(
                text=f"Помилка: {error}"
            ))
            root.after(0, lambda: search_button.config(
                state="normal"
            ))

    threading.Thread(target=worker, daemon=True).start()


def display_results(results):
    global images
    images.clear()

    for widget in gallery.winfo_children():
        widget.destroy()

    if not results:
        status.config(text="Нічого не знайдено")
        search_button.config(state="normal")
        return

    for item in results:
        try:
            request = Request(
                item["thumbs"]["small"],
                headers={"User-Agent": "ErynWall/1.0"}
            )

            with urlopen(request, timeout=15) as response:
                image_data = response.read()

            image = Image.open(io.BytesIO(image_data))
            image.thumbnail((190, 115))

            photo = ImageTk.PhotoImage(image)
            images.append(photo)

            card = tk.Button(
                gallery,
                image=photo,
                text=f'{item["resolution"]} | {item["id"]}',
                compound="top",
                bg="#303030",
                fg="white",
                activebackground="#454545",
                relief="flat",
                command=lambda data=item: download_wallpaper(data)
            )

            card.image = photo
            card.pack(side="left", padx=8, pady=8)

        except Exception as error:
            print(error)

    status.config(text=f"Знайдено: {len(results)} шпалер")
    search_button.config(state="normal")


def download_wallpaper(item):
    def worker():
        try:
            filename = os.path.join(
                CACHE,
                item["id"] + ".jpg"
            )

            request = Request(
                item["path"],
                headers={"User-Agent": "ErynWall/1.0"}
            )

            with urlopen(request, timeout=30) as response:
                content = response.read()

            with open(filename, "wb") as file:
                file.write(content)

            root.after(
                0,
                lambda: apply_wallpaper(filename)
            )

        except Exception as error:
            root.after(
                0,
                lambda: messagebox.showerror(
                    "ErynWall", str(error)
                )
            )

    threading.Thread(target=worker, daemon=True).start()


def apply_wallpaper(path):
    try:
        subprocess.run(
            ["feh", "--bg-fill", path],
            check=True
        )
        status.config(text="Шпалеру встановлено!")
    except Exception as error:
        messagebox.showerror("ErynWall", str(error))


header = tk.Frame(root, bg="#252525")
header.pack(fill="x", padx=12, pady=12)

tk.Label(
    header,
    text="ErynWall",
    font=("Sans", 19, "bold"),
    bg="#252525",
    fg="white"
).pack(side="left", padx=10)

search_entry = tk.Entry(
    header,
    font=("Sans", 12),
    bg="#353535",
    fg="white",
    insertbackground="white",
    relief="flat"
)
search_entry.pack(side="left", fill="x", expand=True, padx=10)

search_button = tk.Button(
    header,
    text="Search",
    command=search_wallpapers
)
search_button.pack(side="left", padx=5)

gallery = tk.Frame(root, bg="#202020")
gallery.pack(fill="both", expand=True, padx=10)

status = tk.Label(
    root,
    text="Шукай шпалери на Wallhaven",
    bg="#252525",
    fg="#aaaaaa",
    anchor="w"
)
status.pack(fill="x", side="bottom", padx=5, pady=5)

search_entry.bind("<Return>", lambda event: search_wallpapers())

search_wallpapers()

root.mainloop()
