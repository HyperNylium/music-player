###~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
###
### Author/Creator: HyperNylium
###
### Website: http://www.hypernylium.com/
###
### GitHub: https://github.com/HyperNylium/
###
### License: Mozilla Public License Version 2.0
###~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#

# Imports
from os import system, execl, listdir
from os.path import exists, join, splitext, expanduser, abspath, splitdrive
from tkinter.messagebox import showerror, askyesno
from tkinter import BooleanVar, IntVar
from json import load as JSload, dump as JSdump
from datetime import timedelta
from tkinter.filedialog import askdirectory
from threading import Thread
from time import sleep
import sys

try:
    from customtkinter import (
        CTk,
        CTkFrame, 
        CTkScrollableFrame, 
        CTkLabel, 
        CTkButton, 
        CTkImage, 
        CTkProgressBar, 
        CTkSlider, 
        set_appearance_mode
    )
    from PIL.Image import open as PILopen, fromarray as PILfromarray
    from vlc import MediaPlayer, Media as vlcMedia
    from numpy import array as nparray
    from tinytag import TinyTag
    from CTkToolTip import CTkToolTip
except ImportError as importError:
    ModuleNotFound = str(importError).split("'")[1]
    usr_choice = askyesno(title="Import error", message=f"An error occurred while importing '{ModuleNotFound}'.\nWould you like to run the setup.bat script?")
    if usr_choice is True:
        system("setup.bat")
    sys.exit()


# Sets the appearance mode of the window to dark 
# (in simpler terms, sets the window to dark mode).
# Don't want to burn them eyes now do we?
set_appearance_mode("dark") 


SETTINGSFILE = "settings.json" # The settings file name
after_events = {} # dict to store after events
prev_x = 0 # variable to store previous x coordinate of the window
prev_y = 0 # variable to store previous y coordinate of the window


class MusicManager:
    def __init__(self):
        self.song_info = {} # Dictionary to store song info: {"song_name"(str): {"duration"(str): duration_in_seconds(int)}}
        self.song_list = []
        self.current_song_index = 0
        self.current_song_paused = False
        self.has_started_before = False
        self.music_dir_exists = None
        self.updating = False
        self.event_loop_running = False
        self.player = MediaPlayer()
        self.player.audio_set_volume(musicVolumeVar.get())

    def cleanup(self):
        """Cleans up the music player"""
        self.event_loop_running = False
        try:
            self.player.stop()
            self.player.release()
        except:
            pass
        return

    def event_loop(self):
        """Event loop for the music player"""
        while self.event_loop_running:
            if self.is_playing() and not self.current_song_paused:
                current_pos_secs = self.player.get_time() / 1000 # Get current position in seconds
                total_duration = self.song_info[self.get_current_playing_song()]["duration"]
                remaining_time = total_duration - current_pos_secs

                formatted_remaining_time = str(timedelta(seconds=remaining_time)).split(".")[0]
                formatted_total_duration = str(timedelta(seconds=total_duration)).split(".")[0]

                time_left_label.configure(text=formatted_remaining_time)
                song_progressbar.set((current_pos_secs / total_duration))
                total_time_label.configure(text=formatted_total_duration)

                del current_pos_secs, total_duration, remaining_time, formatted_remaining_time, formatted_total_duration
                
            if not self.is_playing() and not self.current_song_paused and self.has_started_before:
                if settings["MusicSettings"]["LoopState"] == "all":
                    self.next()
                elif settings["MusicSettings"]["LoopState"] == "one":
                    self.player.stop()
                    self.play()
                elif settings["MusicSettings"]["LoopState"] == "off":
                    self.player.stop()
                    pre_song_btn.configure(state="disabled")
                    next_song_btn.configure(state="disabled")
                    play_pause_song_btn.configure(image=playimage, command=music_manager.play)
                    if self.updating is False:
                        SaveSettingsToJson("CurrentlyPlaying", False)
            sleep(1)
        return

    def start_event_loop(self):
        """Starts the event loop for the music player"""
        self.event_loop_running = True
        Thread(target=self.event_loop, daemon=True, name="MusicManager").start()

    def get_current_playing_song(self):
        """Returns the current playing song"""
        if self.event_loop_running:
            return self.song_list[self.current_song_index]

    def is_playing(self):
        """Returns True if a song is playing and False if not"""
        if self.event_loop_running:
            return bool(self.player.is_playing())

    def stop(self):
        """Stops the current song, resets the player and releases the media"""
        if self.is_playing():
            self.player.stop()

        if self.player.get_media():
            self.player.get_media().release()

        if not self.updating:
            SaveSettingsToJson("CurrentlyPlaying", False)

        self.current_song_index = 0
        self.current_song_paused = False
        self.has_started_before = False

        stop_song_btn.configure(state="disabled")
        play_pause_song_btn.configure(image=playimage, command=self.play)
        all_music_frame.configure(label_text="Not playing anything")

        song_progressbar.set(0.0)
        time_left_label.configure(text="0:00:00")
        total_time_label.configure(text="0:00:00")

    def play(self):
        """Plays the current song or the first song in the list if no song is playing"""
        if len(self.song_list) > 0:
            if self.current_song_paused:
                self.player.play()
                self.current_song_paused = False
            else:
                song_path = join(settings["MusicSettings"]["MusicDir"], self.get_current_playing_song())
                self.player.set_media(vlcMedia(song_path))
                self.player.play()
                self.has_started_before = True
                self.current_song_paused = False
                if not self.updating:
                    all_music_frame.configure(label_text=f"Currently Playing: {splitext(self.get_current_playing_song())[0]}")
            stop_song_btn.configure(state="normal")
            pre_song_btn.configure(state="normal")
            next_song_btn.configure(state="normal")
            stop_song_btn.configure(state="normal")
            play_pause_song_btn.configure(image=pauseimage, command=music_manager.pause)
            SaveSettingsToJson("CurrentlyPlaying", True)
        return

    def pause(self):
        """Pauses the current playing song"""
        self.player.pause()
        self.current_song_paused = True
        stop_song_btn.configure(state="disabled")
        pre_song_btn.configure(state="disabled")
        next_song_btn.configure(state="disabled")
        play_pause_song_btn.configure(image=playimage, command=music_manager.play)
        if not self.updating:
            SaveSettingsToJson("CurrentlyPlaying", False)
        return

    def next(self):
        """Plays the next song in the list"""
        if len(self.song_list) > 0:
            self.current_song_index = (self.current_song_index + 1) % len(self.song_list)
            self.play()
        return

    def previous(self):
        """Plays the previous song in the list"""
        if len(self.song_list) > 0:
            self.current_song_index = (self.current_song_index - 1) % len(self.song_list)
            self.play()
        return

    def volume(self):
        """Sets the volume of the music player"""
        def savevolume():
            SaveSettingsToJson("Volume", musicVolumeVar.get())
        self.player.audio_set_volume(musicVolumeVar.get())
        volume_label.configure(text=f"{musicVolumeVar.get()}%")
        schedule_cancel(window, savevolume)
        schedule_create(window, 420, savevolume)
        return

    def loop(self):
        """Loops the current song or the whole playlist (keep in mind the playlist is the whole music directory)"""
        self.loopstate = settings["MusicSettings"]["LoopState"]
        if self.loopstate == "all":
            loop_playlist_btn.configure(image=CTkImage(change_image_clr(PILopen('assets/MusicPlayer/loop-1.png'), "#00ff00"), size=(25, 25)))
            SaveSettingsToJson("LoopState", "one")
        elif self.loopstate == "one":
            loop_playlist_btn.configure(image=CTkImage(change_image_clr(PILopen('assets/MusicPlayer/loop.png'), "#ff0000"), size=(25, 25)))
            SaveSettingsToJson("LoopState", "off")
        elif self.loopstate == "off":
            loop_playlist_btn.configure(image=CTkImage(change_image_clr(PILopen('assets/MusicPlayer/loop.png'), "#00ff00"), size=(25, 25)))
            SaveSettingsToJson("LoopState", "all")
        del self.loopstate
        return

    def changedir(self):
        """Changes the music directory"""
        if settings["MusicSettings"]["MusicDir"] != "" and exists(settings["MusicSettings"]["MusicDir"]):
            tmp_music_dir = askdirectory(title="Select Your Music Directory", initialdir=settings["MusicSettings"]["MusicDir"])
        else:
            tmp_music_dir = askdirectory(title="Select Your Music Directory", initialdir=expanduser("~"))
        if tmp_music_dir != "":
            SaveSettingsToJson("MusicDir", tmp_music_dir)
            self.stop()
            self.update()

        del tmp_music_dir
        return

    def update_all_music_frame(self):
        """Updates the all_music_frame frame"""
        delete_widgets = []
        for widget in all_music_frame.winfo_children():
            window.after(0, widget.grid_forget)
            delete_widgets.append(widget)

        for index, song_name in enumerate(self.song_list):
            CTkLabel(all_music_frame, text=f"{str(index+1)}. {splitext(song_name)[0]}", font=("sans-serif", 20)).grid(
                row=index, column=1, padx=(20, 0), pady=5, sticky="w")

        if len(delete_widgets) > 0:
            for widget in delete_widgets:
                window.after(0, widget.destroy)
                del widget

        all_music_frame.update()
        if self.music_dir_exists:
            all_music_frame.configure(label_text=f"Currently Playing: {splitext(self.get_current_playing_song())[0]}" if self.has_started_before and len(self.song_list) > 0 else "Not playing anything")

        self.updating = False

        del delete_widgets
        return

    def update(self):
        """Updates the music player"""
        def update_song_list():
            MusicDir = str(settings["MusicSettings"]["MusicDir"])
            if exists(MusicDir):
                self.music_dir_exists = True
                self.song_list = [file for file in listdir(MusicDir) if file.endswith(tuple(TinyTag.SUPPORTED_FILE_EXTENSIONS))]
                for song_name in self.song_list:
                    song_path = join(MusicDir, song_name)
                    tag = TinyTag.get(song_path)
                    self.song_info[song_name] = {"duration": tag.duration}
            else:
                self.music_dir_exists = False
                self.song_list = []
                all_music_frame.configure(label_text="Please choose a valid music directory by clicking the 'Change' button")

            Thread(target=self.update_all_music_frame, daemon=True, name="update_all_music_frame").start()

            update_music_list.configure(state="normal")
            change_music_dir.configure(state="normal")
            pre_song_btn.configure(state="normal")
            play_pause_song_btn.configure(state="normal")
            next_song_btn.configure(state="normal")
            volume_slider.configure(state="normal")
            music_dir_label.configure(text=f"Music Directory: {shorten_path(MusicDir, 25)}" if MusicDir != "" else "Music Directory: None")
            music_dir_tooltip.configure(message=f"Reading music from: {MusicDir}" if MusicDir != "" else "Reading music from: no directory selected")

            if settings["MusicSettings"]["CurrentlyPlaying"] == True:
                self.play()
            return

        self.updating = True
        update_music_list.configure(state="disabled")
        change_music_dir.configure(state="disabled")
        stop_song_btn.configure(state="disabled")
        pre_song_btn.configure(state="disabled")
        play_pause_song_btn.configure(state="disabled")
        next_song_btn.configure(state="disabled")
        volume_slider.configure(state="disabled")
        all_music_frame.configure(label_text="Updating...")
        song_progressbar.set(0.0)
        time_left_label.configure(text="0:00:00")
        total_time_label.configure(text="0:00:00")

        if self.is_playing() and not self.current_song_paused:
            self.pause()

        Thread(target=update_song_list, daemon=True, name="MusicManager_updater").start()


def StartUp():
    """Main function that gets the app going. Should be called only once at the start of the app"""

    # try:
    #     window.iconbitmap("assets/AppIcon/Management_Panel_Icon.ico")
    # except Exception as e:
    #     showerror(title="Error loading window icon", message=f"An error occurred while loading the window icon\n{e}")
    #     sys.exit()

    global settings, musicVolumeVar, music_manager, settingsAlwayOnTopVar

    default_settings = {
        "MusicSettings": {
            "MusicDir": "",
            "Volume": 0,
            "CurrentlyPlaying": False,
            "LoopState": "all"
        },
        "AppSettings": {
            "AlwaysOnTop": False,
            "Window_State": "normal",
            "Window_Width": "",
            "Window_Height": "",
            "Window_X": "",
            "Window_Y": ""
        }
    }
    try:
        with open(SETTINGSFILE, 'r') as settings_file:
            settings = JSload(settings_file)

    except FileNotFoundError:
        with open(SETTINGSFILE, 'w') as settings_file:
            JSdump(default_settings, settings_file, indent=2)
        settings = default_settings

    settingsAlwayOnTopVar = BooleanVar()
    musicVolumeVar = IntVar()

    if settings["AppSettings"]["AlwaysOnTop"] == True:
        window.attributes('-topmost', True)
        settingsAlwayOnTopVar.set(True)

    if isinstance(settings["MusicSettings"]["Volume"], int):
        musicVolumeVar.set(settings["MusicSettings"]["Volume"])
    elif isinstance(settings["MusicSettings"]["Volume"], float):
        musicVolumeVar.set(int(settings["MusicSettings"]["Volume"]))

    music_manager = MusicManager()
def restart():
    """Restarts app"""
    python = sys.executable
    execl(python, python, *sys.argv)
def on_closing():
    """App termination function"""
    SaveSettingsToJson("CurrentlyPlaying", False)
    music_manager.cleanup()
    window.destroy()
    sys.exit()
def schedule_create(widget, ms, func, cancel_after_finished=False, *args, **kwargs):
    """Schedules a function to run after a given time in milliseconds and saves the event id in a dictionary with the function name as the key"""
    event_id = widget.after(ms, lambda: func(*args, **kwargs))
    after_events[func.__name__] = event_id
    if cancel_after_finished:
        widget.after(ms, lambda: schedule_cancel(widget, func))
def schedule_cancel(widget, func):
    """Cancels a scheduled function and deletes the event id from the dictionary using the function name as the parameter instead of the event id"""
    try:
        event_id = after_events.get(func.__name__)
        if event_id is not None:
            widget.after_cancel(event_id)
            del after_events[func.__name__]
    except: 
        pass
def SaveSettingsToJson(key: str, value):
    """Saves data to settings.json file"""
    for Property in ['URLs', 'GameShortcutURLs', 'OpenAISettings', 'MusicSettings', 'AppSettings']:
        if Property in settings and key in settings[Property]:
            settings[Property][key] = value
            break
    else:
        showerror(title="settings error", message=f"There was an error while writing to the settings file\nProperty: {Property}\nKey: {key}\nValue: {value}")
        return

    with open(SETTINGSFILE, 'w') as SettingsToWrite:
        JSdump(settings, SettingsToWrite, indent=2)

def on_drag_end(event):
    global prev_x, prev_y

    # Check if x and y values have changed
    if prev_x != event.x or prev_y != event.y:
        # Update the x and y values
        prev_x = event.x
        prev_y = event.y

        # The main point about the upcoming code is that when you start to
        # drag the window, it first cancels any existing function call to on_drag_stopped()
        # but then creates a new one right after that. This means that instead of the on_drag_stopped()
        # function being called every single pixel you move the window, it will
        # be called only after the window has stopped moving for 420ms.
        # this happens because the on_drag_end() gets called probably hundreds of times
        # you move the window. But with this code, it will only call the on_drag_stopped()
        # function once after you stop moving the window for 420ms because it keeps cancelling
        # the function call before it can even start. Cool, right? This is a more modefied version
        # so it works with this project (i am sure it would work with any project though)
        # you can find the full version that was built with tkinter and uses the .after() method
        # intead of my custom schedule_create() and schedule_cancel() functions here: https://github.com/HyperNylium/tkinter-window-drag-detection

        # Cancel any existing threshold check
        schedule_cancel(window, on_drag_stopped)

        # Schedule a new threshold check after 420ms
        schedule_create(window, 420, on_drag_stopped)
    return
def on_drag_stopped():
    if window.state() == "zoomed":
        SaveSettingsToJson("Window_State", "maximized")
    elif window.state() == "normal":
        SaveSettingsToJson("Window_State", "normal")
        SaveSettingsToJson("Window_Width", window.winfo_width())
        SaveSettingsToJson("Window_Height", window.winfo_height())
        SaveSettingsToJson("Window_X", window.winfo_x())
        SaveSettingsToJson("Window_Y", window.winfo_y())
    return

def CenterWindowToDisplay(Screen: CTk, width: int, height: int, scale_factor: float = 1.0):
    """Centers the window to the main display/monitor"""
    screen_width = Screen.winfo_screenwidth()
    screen_height = Screen.winfo_screenheight()
    x = int(((screen_width/2) - (width/2)) * scale_factor)
    y = int(((screen_height/2) - (height/1.5)) * scale_factor)
    return f"{width}x{height}+{x}+{y}"
def ResetWindowPos():
    """Resets window positions in settings.json"""
    SaveSettingsToJson("Window_State", "normal")
    SaveSettingsToJson("Window_Width", "")
    SaveSettingsToJson("Window_Height", "")
    SaveSettingsToJson("Window_X", "")
    SaveSettingsToJson("Window_Y", "")
    restart()
def AlwaysOnTopTrueFalse():
    """Sets the window to always be on top or not and saves the state to settings.json"""
    value = settingsAlwayOnTopVar.get()
    window.attributes('-topmost', value)
    SaveSettingsToJson("AlwaysOnTop", value)
    del value
    return

def responsive_grid(frame: CTkFrame, rows: int, columns: int):
    """Makes a grid responsive for a frame"""
    for row in range(rows+1):
        frame.grid_rowconfigure(row, weight=1)
    for column in range(columns+1):
        frame.grid_columnconfigure(column, weight=1)
def check_window_properties():
    """Checks if the window properties are set"""
    if (
        "AppSettings" in settings and
        all(key in settings["AppSettings"] for key in ["Window_Width", "Window_Height", "Window_X", "Window_Y", "Window_State"]) and
        all(settings["AppSettings"][key] != "" for key in ["Window_Width", "Window_Height", "Window_X", "Window_Y", "Window_State"])
    ):
        return True
    return False
def update_widget(widget, update=False, update_idletasks=False):
    """Updates a widget"""
    if update:
        widget.update()
    if update_idletasks:
        widget.update_idletasks()
def hextorgb(new_color_hex: str):
    new_color_hex = new_color_hex.lower().lstrip('#')
    new_color_rgb = tuple(int(new_color_hex[i:i+2], 16) for i in (0, 2, 4))
    return new_color_rgb
def change_image_clr(image, hex_color: str):
    target_rgb = hextorgb(hex_color)
    image = image.convert('RGBA')
    data = nparray(image)

    # red, green, blue, alpha = data[..., 0], data[..., 1], data[..., 2], data[..., 3]
    alpha = data[..., 3]

    # Find areas with non-transparent pixels
    non_transparent_areas = alpha > 0

    # Replace the RGB values of non-transparent areas with the target RGB color
    data[..., 0][non_transparent_areas] = target_rgb[0]
    data[..., 1][non_transparent_areas] = target_rgb[1]
    data[..., 2][non_transparent_areas] = target_rgb[2]

    image_with_color = PILfromarray(data)
    return image_with_color
def shorten_path(text, max_length, replacement: str = "..."):
    if len(text) > max_length:
        return text[:max_length - 3] + replacement  # Replace the last three characters with "..."
    return text
def file_path():
    """Gets the file path of the current file regardless of if its a .pyw file or a .exe file"""
    if getattr(sys, 'frozen', False):
        return sys.executable
    else:
        drive, rest_of_path = splitdrive(abspath(__file__))
        formatted_path = drive.upper() + rest_of_path
        return formatted_path

window = CTk()
window.title("Music Player")
window.protocol("WM_DELETE_WINDOW", on_closing)
window.minsize(520, 370)
screen_scale = window._get_window_scaling()
StartUp()

if check_window_properties():
    WINDOW_STATE = str(settings["AppSettings"]["Window_State"])
    WIDTH = int(settings["AppSettings"]["Window_Width"] / screen_scale)
    HEIGHT = int(settings["AppSettings"]["Window_Height"] / screen_scale)
    X = int(settings["AppSettings"]["Window_X"])
    Y = int(settings["AppSettings"]["Window_Y"])

    window.geometry(f"{WIDTH}x{HEIGHT}+{X}+{Y}")

    if WINDOW_STATE == "maximized":
        # Thank you Akascape for helping me out (https://github.com/TomSchimansky/CustomTkinter/discussions/1819)
        schedule_create(window, 50,  lambda: window.state('zoomed'), True)

    del WIDTH, HEIGHT, X, Y, WINDOW_STATE
else:
    window.geometry(CenterWindowToDisplay(window, 750, 420, screen_scale))

del screen_scale

# Bind keys Ctrl + Shift + Del to reset the windows positional values in settings.json
window.bind('<Control-Shift-Delete>', lambda event: ResetWindowPos())
window.bind('<Configure>', on_drag_end)

# Importing all icons and assigning them to there own variables to use later
try:
    previousimage = CTkImage(change_image_clr(PILopen('assets/MusicPlayer/previous.png'), "#ffffff"), size=(25, 25))
    pauseimage = CTkImage(change_image_clr(PILopen("assets/MusicPlayer/pause.png"), "#ffffff"), size=(25, 25))
    playimage = CTkImage(change_image_clr(PILopen('assets/MusicPlayer/play.png'), "#ffffff"), size=(25, 25))
    nextimage = CTkImage(change_image_clr(PILopen('assets/MusicPlayer/next.png'), "#ffffff"), size=(25, 25))
    stopimage = CTkImage(change_image_clr(PILopen('assets/MusicPlayer/stop.png'), "#ffffff"), size=(25, 25))
    if settings["MusicSettings"]["LoopState"] == "all":
        loopimage = CTkImage(change_image_clr(PILopen('assets/MusicPlayer/loop.png'), "#00ff00"), size=(25, 25))
    elif settings["MusicSettings"]["LoopState"] == "one":
        loopimage = CTkImage(change_image_clr(PILopen('assets/MusicPlayer/loop-1.png'), "#00ff00"), size=(25, 25))
    elif settings["MusicSettings"]["LoopState"] == "off":
        loopimage = CTkImage(change_image_clr(PILopen('assets/MusicPlayer/loop.png'), "#ff0000"), size=(25, 25))
    else:
        loopimage = CTkImage(change_image_clr(PILopen('assets/MusicPlayer/loop.png'), "#00ff00"), size=(25, 25))
        SaveSettingsToJson("LoopState", "all")
except Exception as e:
    showerror(title="Icon import error", message=f"Couldn't import an icon.\nDetails: {e}")
    on_closing()


# Frames that hold everything together
music_frame_container = CTkFrame(window, corner_radius=0, fg_color="transparent")
all_music_frame = CTkScrollableFrame(window, height=150, corner_radius=0, fg_color="transparent", border_width=2, border_color="#333", label_text="Updating...", label_font=("sans-serif", 18))
music_info_frame = CTkFrame(window, corner_radius=0, fg_color="transparent")
music_controls_frame = CTkFrame(music_frame_container, corner_radius=0, fg_color="transparent")
music_volume_frame = CTkFrame(music_frame_container, corner_radius=0, fg_color="transparent")
music_progress_frame = CTkFrame(music_frame_container, corner_radius=0, fg_color="transparent")

all_music_frame.pack(fill="both", expand=True, anchor="s", pady=0)
music_info_frame.pack(fill="x", expand=True, anchor="s", pady=0)
music_frame_container.pack(fill="x", expand=True, anchor="s", pady=0)
music_controls_frame.pack(fill="x", expand=True, anchor="s", pady=0)
music_volume_frame.pack(fill="x", expand=True, anchor="s", pady=0)
music_progress_frame.pack(fill="x", expand=True, anchor="s", pady=0)

music_controls_frame.grid_columnconfigure([0, 5], weight=1)


# Where the selected music directory is displayed and where the update and change buttons are
music_dir_label = CTkLabel(music_info_frame, text=f"Music Directory: {shorten_path(settings['MusicSettings']['MusicDir'], 45)}" if settings['MusicSettings']['MusicDir'] != "" else "Music Directory: None", font=("sans-serif", 18))
update_music_list = CTkButton(music_info_frame, width=80, text="Update", compound="top", fg_color=("gray75", "gray30"), font=("sans-serif", 18), corner_radius=10, command=music_manager.update)
change_music_dir = CTkButton(music_info_frame, width=80, text="Change", compound="top", fg_color=("gray75", "gray30"), font=("sans-serif", 18), corner_radius=10, command=music_manager.changedir)

music_dir_label.grid(row=2, column=1, padx=10, pady=5, sticky="w")
update_music_list.grid(row=2, column=2, padx=5, pady=5, sticky="e")
change_music_dir.grid(row=2, column=3, padx=5, pady=5, sticky="w")
music_info_frame.grid_columnconfigure([0, 3], weight=1)


# Music controls (start, stop, pause, next, previous, loop)
stop_song_btn = CTkButton(music_controls_frame, width=40, height=40, text="", fg_color="transparent", image=stopimage, anchor="w", hover_color=("gray70", "gray30"), command=music_manager.stop)
pre_song_btn = CTkButton(music_controls_frame, width=40, height=40, text="", fg_color="transparent", image=previousimage, anchor="w", hover_color=("gray70", "gray30"), command=music_manager.previous)
play_pause_song_btn = CTkButton(music_controls_frame, width=40, height=40, text="", fg_color="transparent", image=playimage, anchor="w", hover_color=("gray70", "gray30"), command=music_manager.play)
next_song_btn = CTkButton(music_controls_frame, width=40, height=40, text="", fg_color="transparent", image=nextimage, anchor="w", hover_color=("gray70", "gray30"), command=music_manager.next)
loop_playlist_btn = CTkButton(music_controls_frame, width=40, height=40, text="", fg_color="transparent", image=loopimage, anchor="w", hover_color=("gray70", "gray30"), command=music_manager.loop)

stop_song_btn.grid(row=1, column=1, padx=5, pady=0, sticky="w")
pre_song_btn.grid(row=1, column=2, padx=10, pady=0, sticky="e")
play_pause_song_btn.grid(row=1, column=3, padx=10, pady=0, sticky="e")
next_song_btn.grid(row=1, column=4, padx=10, pady=0, sticky="e")
loop_playlist_btn.grid(row=1, column=5, padx=10, pady=0, sticky="w")


# Music volume slider
volume_slider = CTkSlider(music_volume_frame, width=250, from_=0, to=100, command=lambda volume: music_manager.volume(), variable=musicVolumeVar, button_color="#fff", button_hover_color="#ccc")
volume_label = CTkLabel(music_volume_frame, text=f"{musicVolumeVar.get()}%", font=("sans-serif", 18, "bold"), fg_color="transparent")

volume_label.grid(row=1, column=1, padx=0, pady=0, sticky="w")
volume_slider.grid(row=1, column=1, padx=40, pady=0, sticky="e")
music_volume_frame.grid_columnconfigure([0, 2], weight=1)


# Music progress bar and time labels
time_left_label = CTkLabel(music_progress_frame, text="0:00:00", font=("sans-serif", 18, "bold"), fg_color="transparent")
song_progressbar = CTkProgressBar(music_progress_frame, mode="determinate", height=15)
song_progressbar.set(0.0)
total_time_label = CTkLabel(music_progress_frame, text="0:00:00", font=("sans-serif", 18, "bold"), fg_color="transparent")

time_left_label.grid(row=1, column=0, padx=10, pady=0, sticky="w")
song_progressbar.grid(row=1, column=1, padx=10, pady=0, sticky="ew")
total_time_label.grid(row=1, column=2, padx=10, pady=0, sticky="e")
music_progress_frame.grid_columnconfigure(1, weight=1)


# Creating all tooltips
music_dir_tooltip = CTkToolTip(music_dir_label, message=f"Reading music from: {settings['MusicSettings']['MusicDir']}" if settings['MusicSettings']['MusicDir'] != "" else "Reading music from: no directory selected")
CTkToolTip(update_music_list, message="Refresh the music list")
CTkToolTip(change_music_dir, message="Change the directory where the music is read from")
CTkToolTip(stop_song_btn, message="Stops the current song, resets the player, and releases the media")
CTkToolTip(pre_song_btn, message="Plays the previous song")
CTkToolTip(play_pause_song_btn, message="Plays or pauses the current song")
CTkToolTip(next_song_btn, message="Plays the next song")
CTkToolTip(loop_playlist_btn, message="Loops the current song or the whole playlist (keep in mind the 'playlist' is the whole music directory)")
CTkToolTip(volume_slider, message="Sets the volume of the music player")


# initialize and start the MusicManager
music_manager.update()
music_manager.start_event_loop()


window.mainloop()