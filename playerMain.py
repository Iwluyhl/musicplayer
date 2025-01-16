import os
import pygame
import tkinter as tk
from tkinter import filedialog, messagebox
import customtkinter as ctk


class MusicPlayer:
    def __init__(self, root):
        self.root = root
        self.root.title("Music Player")
        self.root.geometry("900x400")
        
        self.playlist = []
        self.track_index = 0
        self.paused = False
        self.shuffle = False
        self.repeat = False
        
        pygame.mixer.init()
        
        # GUI Components
        self.create_gui()
    
    def create_gui(self):
        # Main Frame
        main_frame = ctk.CTkFrame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Buttons Frame
        button_frame = ctk.CTkFrame(main_frame)
        button_frame.pack(side=tk.TOP, pady=5)
        
        self.btn_load_folder = ctk.CTkButton(button_frame, text="Load Folder", command=self.load_folder)
        self.btn_load_folder.pack(side=tk.LEFT, padx=5)
        
        self.btn_shuffle = ctk.CTkButton(button_frame, text="Shuffle", command=self.toggle_shuffle)
        self.btn_shuffle.pack(side=tk.LEFT, padx=5)
        
        self.btn_repeat = ctk.CTkButton(button_frame, text="Repeat", command=self.toggle_repeat)
        self.btn_repeat.pack(side=tk.LEFT, padx=5)
        
        # Playlist Frame
        playlist_frame = ctk.CTkFrame(main_frame)
        playlist_frame.pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=5)
        
        self.playlist_box = tk.Listbox(playlist_frame, width=30, height=20)
        self.playlist_box.pack(side=tk.LEFT, fill=tk.Y)
        self.playlist_box.bind("<Double-1>", self.on_playlist_double_click)
        
        self.scrollbar = tk.Scrollbar(playlist_frame, orient=tk.VERTICAL, command=self.playlist_box.yview)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.playlist_box.config(yscrollcommand=self.scrollbar.set)
        
        # Track Info Frame
        track_info_frame = ctk.CTkFrame(main_frame)
        track_info_frame.pack(side=tk.TOP, pady=5)
        
        self.track_info_label = ctk.CTkLabel(track_info_frame, text="No track selected", wraplength=300)
        self.track_info_label.pack(side=tk.LEFT, padx=10)
        
        # Progress Bar and Volume Control
        control_frame = ctk.CTkFrame(main_frame)
        control_frame.pack(side=tk.TOP, pady=5)
        
        self.progress_bar = ctk.CTkSlider(control_frame, from_=0, to=100, orientation="horizontal", width=400,
                                          command=self.set_position)
        self.progress_bar.pack(side=tk.LEFT, padx=10)
        self.progress_bar.set(0)  # Default value for progress bar
        
        self.volume_scale = ctk.CTkSlider(control_frame, from_=0, to=100, orientation="horizontal",
                                          command=self.set_volume)
        self.volume_scale.set(70)  # Default volume
        self.volume_scale.pack(side=tk.LEFT, padx=10)
        
        # Playback Control
        playback_frame = ctk.CTkFrame(main_frame)
        playback_frame.pack(side=tk.BOTTOM, pady=5)
        
        self.btn_play_pause = ctk.CTkButton(playback_frame, text="Play", command=self.play_pause)
        self.btn_play_pause.pack(side=tk.LEFT, padx=5)
        
        self.btn_next = ctk.CTkButton(playback_frame, text="Next", command=self.next_track)
        self.btn_next.pack(side=tk.LEFT, padx=5)
        
        self.btn_prev = ctk.CTkButton(playback_frame, text="Prev", command=self.prev_track)
        self.btn_prev.pack(side=tk.LEFT, padx=5)
    
    def load_folder(self):
        folder_selected = filedialog.askdirectory()
        if folder_selected:
            self.playlist = [os.path.join(folder_selected, f) for f in os.listdir(folder_selected) if
                             f.endswith('.mp3')]
            self.update_playlist_box()
            messagebox.showinfo("Info", f"Loaded {len(self.playlist)} tracks.")
    
    def update_playlist_box(self):
        self.playlist_box.delete(0, tk.END)
        for track in self.playlist:
            self.playlist_box.insert(tk.END, os.path.basename(track))
    
    def toggle_shuffle(self):
        self.shuffle = not self.shuffle
    
    def toggle_repeat(self):
        self.repeat = not self.repeat
    
    def load_track(self, index=None):
        if index is None:
            index = self.track_index
        else:
            self.track_index = index
        if 0 <= self.track_index < len(self.playlist):
            track_path = self.playlist[self.track_index]
            try:
                pygame.mixer.music.load(track_path)
                audio_length = pygame.mixer.Sound(track_path).get_length()
                self.progress_bar.configure(to=int(audio_length))
                self.update_track_info(track_path, audio_length)
                self.play_pause()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load track: {e}")
    
    def update_track_info(self, track_path, audio_length):
        minutes, seconds = divmod(int(audio_length), 60)
        self.track_info_label.configure(
            text=f"{os.path.basename(track_path)} - {minutes}:{seconds:02d}"
        )
        self.progress_bar.set(0)  # Reset progress bar to 0 when loading a new track
    
    def play_pause(self):
        if pygame.mixer.music.get_busy():
            pygame.mixer.music.pause()
            self.paused = True
            self.btn_play_pause.configure(text="Play")
            self.progress_bar.set(0)  # Reset progress bar when pausing
        else:
            if self.paused:
                pygame.mixer.music.unpause()
                self.paused = False
                self.btn_play_pause.configure(text="Pause")
            else:
                self.load_track()
                pygame.mixer.music.play()
                self.btn_play_pause.configure(text="Pause")
                self.update_progress()
    
    def next_track(self):
        if self.shuffle:
            self.track_index = (self.track_index + 1) % len(self.playlist)
        else:
            self.track_index = (self.track_index + 1) % len(self.playlist)
        self.load_track()
    
    def prev_track(self):
        if self.shuffle:
            self.track_index = (self.track_index - 1) % len(self.playlist)
        else:
            self.track_index = (self.track_index - 1) % len(self.playlist)
        self.load_track()
    
    def set_volume(self, value):
        pygame.mixer.music.set_volume(int(value) / 100)
    
    def set_position(self, value):
        pygame.mixer.music.set_pos(float(value))
    
    def update_progress(self):
        if pygame.mixer.music.get_busy():
            current_pos = pygame.mixer.music.get_pos() / 1000
            self.progress_bar.set(current_pos)
            self.root.after(1000, self.update_progress)
        elif self.repeat:
            self.load_track()
            pygame.mixer.music.play()
        elif self.track_index < len(self.playlist) - 1:
            self.next_track()
    
    def on_playlist_double_click(self, event):
        selected_index = self.playlist_box.curselection()[0]
        self.load_track(selected_index)


if __name__ == "__main__":
    root = ctk.CTk()
    app = MusicPlayer(root)
    root.mainloop()