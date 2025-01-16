import customtkinter as ctk
import pygame
from pygame import mixer
from mutagen.mp3 import MP3
import os
import fnmatch
from tkinter import filedialog
from PIL import Image, ImageTk


class MusicPlayer:
    def __init__(self, master):
        # Создание главного окна
        self.master = master
        self.master.config(bg="#000000")
        self.master.geometry("400x650")
        self.master.title("Music Player")
        
        # Кнопка "Выбрать папку"
        self.select_folder_button = ctk.CTkButton(master, text="Выбрать папку", command=self.select_folder, height=40,
                                                  width=100, bg_color="#000000", fg_color="#584563")
        self.select_folder_button.place(x=10, y=10)
        
        # Создание выпадающего списка (OptionMenu)
        self.music_files = []
        self.current_index = 0
        self.option_var = ctk.StringVar(value="Выберите трек")
        self.option_menu = ctk.CTkOptionMenu(master, variable=self.option_var, values=self.music_files,
                                             command=self.load_track, bg_color="#000000", fg_color="#584563",
                                             text_color="#D386E4", width=200, height=30)
        self.option_menu.place(x=10, y=60)
        
        # Создание кнопок
        self.play_pause_button = ctk.CTkButton(master, text=">", command=self.toggle_play_pause, height=40, width=40,
                                               bg_color="#000000", fg_color="#584563")
        self.play_next_button = ctk.CTkButton(master, text="—>", command=self.play_next, height=40, width=40,
                                              bg_color="#000000", fg_color="#584563")
        self.play_prev_button = ctk.CTkButton(master, text="<—", command=self.play_prev, height=40, width=40,
                                              bg_color="#000000", fg_color="#584563")
        self.label = ctk.CTkLabel(master, text="", bg_color="#000000", text_color="#584563")
        
        self.slider = ctk.CTkSlider(master, height=10, width=310, from_=0, to=100, bg_color="#000000",
                                    fg_color="#584563",
                                    command=self.update_music_position)
        self.mix_btn = ctk.CTkButton(master, text="mix", command=self.toggle_shuffle, height=40, width=40,
                                     bg_color="#000000", fg_color="#584563")
        self.repeat_btn = ctk.CTkButton(master, text="rep", command=self.toggle_repeat, height=40, width=40,
                                        bg_color="#000000", fg_color="#584563")
        
        # Создание метки для отображения анимированной GIF
        self.gif_label = ctk.CTkLabel(master, text="", bg_color="#000000", width=390, height=390)
        self.gif_label.place(x=5, y=100)
        
        # Размещение виджетов в окне
        self.label.place(x=10, y=510)
        self.play_pause_button.place(x=180, y=540)
        self.play_next_button.place(x=230, y=540)
        self.play_prev_button.place(x=130, y=540)
        self.slider.place(x=45, y=570)
        self.mix_btn.place(x=80, y=540)
        self.repeat_btn.place(x=280, y=540)
        
        # Инициализация pygame
        pygame.mixer.init()
        self.current_music = None
        self.is_paused = False
        self.rootpath = ""
        self.shuffle = False
        self.repeat = False
        self.song_length = 0
        
        # Загрузка анимированной GIF
        self.gif_path = r"C:\Users\mihmo\PycharmProjects\pythonProject5\1be08b145612bdecf14a4ba4585c2b80.gif"  # Укажите путь к вашей GIF-файлу
        self.gif_frames = []
        self.frame_duration = 100  # По умолчанию установим длительность кадра в 100 миллисекунд
        self.load_gif_frames(self.gif_path)
        self.current_frame = 0
        self.update_gif()
        
        # Установка события окончания воспроизведения
        self.END_EVENT = pygame.USEREVENT + 1
        pygame.mixer.music.set_endevent(self.END_EVENT)
        
        # Обработка событий
        self.master.after(100, self.check_end_event)
    
    def load_gif_frames(self, gif_path):
        gif_image = Image.open(gif_path)
        self.frame_duration = gif_image.info.get('duration',
                                                 100)  # Получаем длительность кадра из GIF или устанавливаем значение по умолчанию
        try:
            while True:
                frame = gif_image.copy().resize((390, 390),
                                                Image.ANTIALIAS)  # Используем ANTIALIAS для старых версий Pillow
                self.gif_frames.append(ImageTk.PhotoImage(frame))
                gif_image.seek(len(self.gif_frames))  # Переход к следующему кадру
        except EOFError:
            pass  # Конец файла достигнут
    
    def update_gif(self):
        if self.gif_frames:
            self.gif_label.configure(image=self.gif_frames[self.current_frame])
            self.current_frame = (self.current_frame + 1) % len(self.gif_frames)
            self.master.after(int(self.frame_duration), self.update_gif)  # Обновление кадра через интервал времени
    
    def select_folder(self):
        self.rootpath = filedialog.askdirectory()
        if not self.rootpath:
            return
        self.music_files = []
        for root, dirs, files in os.walk(self.rootpath):
            for filename in fnmatch.filter(files, "*.mp3"):
                self.music_files.append(filename)
        self.option_menu.configure(values=self.music_files)
    
    def load_track(self, track_name):
        if track_name and track_name != "Выберите трек":
            self.current_index = self.music_files.index(track_name)
            self.label.configure(text=track_name)
            self.play_current_track()
    
    def toggle_play_pause(self):
        if not self.music_files:
            return
        if not self.is_paused:
            # Если музыка не играет, начать воспроизведение
            if not mixer.music.get_busy():
                self.play_current_track()
                self.play_pause_button.configure(text="||")
            else:
                # Если музыка играет, поставить на паузу
                mixer.music.pause()
                self.play_pause_button.configure(text=">")
                self.is_paused = True
        else:
            # Если музыка на паузе, возобновить воспроизведение
            mixer.music.unpause()
            self.play_pause_button.configure(text="||")
            self.is_paused = False
    
    def stop(self):
        mixer.music.stop()
        self.label.configure(text="")
        self.play_pause_button.configure(text=">")
        self.is_paused = False
    
    def play_next(self):
        self.current_index = (self.current_index + 1) % len(self.music_files)
        self.play_current_track()
    
    def play_prev(self):
        self.current_index = (self.current_index - 1) % len(self.music_files)
        self.play_current_track()
    
    def play_current_track(self):
        if self.music_files:
            next_song_name = self.music_files[self.current_index]
            self.label.configure(text=next_song_name)
            mixer.music.load(os.path.join(self.rootpath, next_song_name))
            mixer.music.play()
            self.song_length = MP3(os.path.join(self.rootpath, next_song_name)).info.length
            self.update_slider()
            self.play_pause_button.configure(text="||")
            self.is_paused = False
    
    def update_slider(self):
        if mixer.music.get_busy():
            current_pos = mixer.music.get_pos() / 1000  # convert milliseconds to seconds
            self.slider.set(current_pos / self.song_length * 100)
            self.master.after(1000, self.update_slider)
    
    def toggle_shuffle(self):
        self.shuffle = not self.shuffle
        if self.shuffle:
            self.music_files = self.music_files.copy()
            import random
            random.shuffle(self.music_files)
            self.option_menu.configure(values=self.music_files)
    
    def toggle_repeat(self):
        self.repeat = not self.repeat
    
    def check_end_event(self):
        if pygame.mixer.get_init():  # Проверяем, инициализирован ли pygame.mixer
            for event in pygame.event.get():
                if event.type == self.END_EVENT:
                    if self.repeat:
                        self.play_current_track()
                    else:
                        self.play_next()
        self.master.after(100, self.check_end_event)
    
    def update_music_position(self, value):
        if mixer.music.get_busy():
            new_position = float(value) / 100 * self.song_length
            mixer.music.set_pos(new_position)
            if self.is_paused:
                mixer.music.pause()
            else:
                mixer.music.unpause()
            self.update_slider()


root = ctk.CTk()
player = MusicPlayer(root)
root.mainloop() 