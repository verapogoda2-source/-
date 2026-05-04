import tkinter as tk
from tkinter import messagebox, ttk
import requests
import json
import os

# Конфигурация
FAVORITES_FILE = "favorites.json"
GITHUB_API_URL = "https://api.github.com/users/"

class GitHubUserFinder:
    def __init__(self, root):
        self.root = root
        self.root.title("GitHub User Finder")
        self.root.geometry("600x500")

        # Загрузка избранных пользователей
        self.favorites = self.load_favorites()

        self.setup_ui()

    def setup_ui(self):
        # Поле ввода
        input_frame = tk.Frame(self.root)
        input_frame.pack(pady=10, fill="x", padx=20)

        tk.Label(input_frame, text="GitHub Username:").pack(side="left")
        self.search_entry = tk.Entry(input_frame, width=30)
        self.search_entry.pack(side="left", padx=5)
        self.search_entry.bind("<Return>", lambda event: self.search_user())

        search_btn = tk.Button(input_frame, text="Search", command=self.search_user)
        search_btn.pack(side="left")

        # Результаты поиска
        results_frame = tk.LabelFrame(self.root, text="Search Results", padx=10, pady=10)
        results_frame.pack(fill="both", expand=True, padx=20, pady=10)

        columns = ("Username", "Name", "Location", "Public Repos")
        self.tree = ttk.Treeview(results_frame, columns=columns, show="headings", height=10)

        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=120)

        self.tree.pack(fill="both", expand=True)

        # Кнопки для избранного
        buttons_frame = tk.Frame(results_frame)
        buttons_frame.pack(pady=5)

        add_fav_btn = tk.Button(buttons_frame, text="Add to Favorites", command=self.add_to_favorites)
        add_fav_btn.pack(side="left", padx=5)

        show_fav_btn = tk.Button(buttons_frame, text="Show Favorites", command=self.show_favorites)
        show_fav_btn.pack(side="left", padx=5)

        # Область избранного
        favorites_frame = tk.LabelFrame(self.root, text="Favorites", padx=10, pady=10)
        favorites_frame.pack(fill="x", padx=20, pady=10)

        self.fav_listbox = tk.Listbox(favorites_frame, height=5)
        self.fav_listbox.pack(fill="x")

        remove_fav_btn = tk.Button(favorites_frame, text="Remove from Favorites", command=self.remove_from_favorites)
        remove_fav_btn.pack(pady=5)

    def search_user(self):
        username = self.search_entry.get().strip()
        if not username:
            messagebox.showerror("Error", "Search field cannot be empty!")
            return

        try:
            response = requests.get(f"{GITHUB_API_URL}{username}")
            if response.status_code == 200:
                user_data = response.json()
                self.display_user(user_data)
            else:
                messagebox.showerror("Error", f"User not found: {username}")
        except requests.RequestException as e:
            messagebox.showerror("Error", f"Network error: {e}")

    def display_user(self, user_data):
        # Очистка предыдущих результатов
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Добавление найденного пользователя
        self.tree.insert("", "end", values=(
            user_data.get("login", "N/A"),
            user_data.get("name", "N/A"),
            user_data.get("location", "N/A"),
            user_data.get("public_repos", 0)
        ))

    def add_to_favorites(self):
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Select a user from search results first!")
            return

        user_data = self.tree.item(selection[0])["values"]
        username = user_data[0]

        if username not in self.favorites:
            self.favorites[username] = {
                "name": user_data[1],
                "location": user_data[2],
                "public_repos": user_data[3]
            }
            self.save_favorites()
            self.update_favorites_list()
            messagebox.showinfo("Success", f"{username} added to favorites!")

    def show_favorites(self):
        # Очистка результатов поиска
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Отображение избранных
        for username, data in self.favorites.items():
            self.tree.insert("", "end", values=(
                username,
                data["name"],
                data["location"],
                data["public_repos"]
            ))

    def remove_from_favorites(self):
        selection = self.fav_listbox.curselection()
        if not selection:
            messagebox.showwarning("Warning", "Select a favorite user to remove!")
            return

        username = self.fav_listbox.get(selection[0])
        del self.favorites[username]
        self.save_favorites()
        self.update_favorites_list()
        messagebox.showinfo("Success", f"{username} removed from favorites!")

    def load_favorites(self):
        if os.path.exists(FAVORITES_FILE):
            try:
                with open(FAVORITES_FILE, "r") as f:
                    return json.load(f)
            except json.JSONDecodeError:
                return {}
        return {}

    def save_favorites(self):
        with open(FAVORITES_FILE, "w") as f:
            json.dump(self.favorites, f, indent=4)

    def update_favorites_list(self):
        self.fav_listbox.delete(0, tk.END)
        for username in self.favorites.keys():
            self.fav_listbox.insert(tk.END, username)

if __name__ == "__main__":
    root = tk.Tk()
    app = GitHubUserFinder(root)
    root.mainloop()

