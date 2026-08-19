import os
import threading
import tkinter as tk
from tkinter import ttk
import speech_recognition as sr
from gtts import gTTS
from playsound3 import playsound
from deep_translator import GoogleTranslator


# =========================================================
# FILE PATHS
# =========================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

ICON_PATH = os.path.join(BASE_DIR, "icon.png")
VOICE_PATH = os.path.join(BASE_DIR, "voice.mp3")


# =========================================================
# TKINTER WINDOW
# =========================================================

win = tk.Tk()

win.geometry("700x450")
win.title("Real-Time Voice 🎙️ Translator 🔊")


# Use icon only if the file exists
if os.path.exists(ICON_PATH):
    icon = tk.PhotoImage(file=ICON_PATH)
    win.iconphoto(False, icon)


# =========================================================
# TEXT BOXES
# =========================================================

input_label = tk.Label(
    win,
    text="Recognized Text"
)
input_label.pack()

input_text = tk.Text(
    win,
    height=5,
    width=60
)
input_text.pack()


output_label = tk.Label(
    win,
    text="Translated Text"
)
output_label.pack()

output_text = tk.Text(
    win,
    height=5,
    width=60
)
output_text.pack()


tk.Label(win, text="").pack()


# =========================================================
# LANGUAGES
# =========================================================

language_codes = {
    "English": "en",
    "Hindi": "hi",
    "Bengali": "bn",
    "Spanish": "es",
    "Chinese": "zh-CN",
    "Russian": "ru",
    "Japanese": "ja",
    "Korean": "ko",
    "German": "de",
    "French": "fr",
    "Tamil": "ta",
    "Telugu": "te",
    "Kannada": "kn",
    "Gujarati": "gu",
    "Punjabi": "pa"
}

language_names = list(language_codes.keys())


# =========================================================
# INPUT LANGUAGE
# =========================================================

input_lang_label = tk.Label(
    win,
    text="Select Input Language:"
)
input_lang_label.pack()

input_lang = ttk.Combobox(
    win,
    values=language_names,
    state="readonly"
)

input_lang.set("English")
input_lang.pack()


def get_input_language():
    selected = input_lang.get()

    if selected in language_codes:
        return language_codes[selected]

    return "en"


# =========================================================
# OUTPUT LANGUAGE
# =========================================================

tk.Label(win, text="▼").pack()

output_lang_label = tk.Label(
    win,
    text="Select Output Language:"
)
output_lang_label.pack()

output_lang = ttk.Combobox(
    win,
    values=language_names,
    state="readonly"
)

output_lang.set("Tamil")
output_lang.pack()


def get_output_language():
    selected = output_lang.get()

    if selected in language_codes:
        return language_codes[selected]

    return "ta"


tk.Label(win, text="").pack()


# =========================================================
# TRANSLATOR CONTROL
# =========================================================

keep_running = False


# =========================================================
# TRANSLATION FUNCTION
# =========================================================

def update_translation():

    global keep_running

    if not keep_running:
        return

    recognizer = sr.Recognizer()

    try:

        with sr.Microphone() as source:

            print("Adjusting microphone...")

            recognizer.adjust_for_ambient_noise(
                source,
                duration=1
            )

            print("Speak Now!")

            audio = recognizer.listen(
                source,
                timeout=10,
                phrase_time_limit=10
            )


        # ---------------------------------------------
        # SPEECH TO TEXT
        # ---------------------------------------------

        speech_text = recognizer.recognize_google(
            audio,
            language=get_input_language()
        )

        print("Recognized:", speech_text)


        # ---------------------------------------------
        # STOP COMMAND
        # ---------------------------------------------

        if speech_text.lower().strip() in {"exit", "stop"}:

            keep_running = False

            win.after(
                0,
                lambda: output_text.insert(
                    tk.END,
                    "Translation stopped.\n"
                )
            )

            return


        # ---------------------------------------------
        # UPDATE INPUT TEXT
        # ---------------------------------------------

        win.after(
            0,
            lambda text=speech_text:
            input_text.insert(
                tk.END,
                text + "\n"
            )
        )


        # ---------------------------------------------
        # TRANSLATION
        # ---------------------------------------------

        source_language = get_input_language()
        target_language = get_output_language()

        translated_text = GoogleTranslator(
            source=source_language,
            target=target_language
        ).translate(
            speech_text
        )

        print("Translated:", translated_text)


        # ---------------------------------------------
        # UPDATE OUTPUT TEXT
        # ---------------------------------------------

        win.after(
            0,
            lambda text=translated_text:
            output_text.insert(
                tk.END,
                text + "\n"
            )
        )


        # ---------------------------------------------
        # TEXT TO SPEECH
        # ---------------------------------------------

        voice = gTTS(
            text=translated_text,
            lang=target_language
        )

        voice.save(VOICE_PATH)


        # ---------------------------------------------
        # PLAY AUDIO
        # ---------------------------------------------

        playsound(VOICE_PATH)


        # ---------------------------------------------
        # DELETE AUDIO FILE
        # ---------------------------------------------

        if os.path.exists(VOICE_PATH):
            os.remove(VOICE_PATH)


    except sr.WaitTimeoutError:

        win.after(
            0,
            lambda: output_text.insert(
                tk.END,
                "No speech detected.\n"
            )
        )


    except sr.UnknownValueError:

        win.after(
            0,
            lambda: output_text.insert(
                tk.END,
                "Could not understand the speech.\n"
            )
        )


    except sr.RequestError:

        win.after(
            0,
            lambda: output_text.insert(
                tk.END,
                "Could not connect to Google Speech Recognition.\n"
            )
        )


    except Exception as e:

        print("ERROR:", e)

        win.after(
            0,
            lambda error=str(e):
            output_text.insert(
                tk.END,
                f"Error: {error}\n"
            )
        )


    # Continue listening
    if keep_running:

        win.after(
            100,
            start_translation_thread
        )


# =========================================================
# START TRANSLATION THREAD
# =========================================================

def start_translation_thread():

    if not keep_running:
        return

    thread = threading.Thread(
        target=update_translation,
        daemon=True
    )

    thread.start()


# =========================================================
# RUN BUTTON
# =========================================================

def run_translator():

    global keep_running

    if not keep_running:

        keep_running = True

        output_text.insert(
            tk.END,
            "Translation started. Speak now...\n"
        )

        start_translation_thread()


# =========================================================
# STOP BUTTON
# =========================================================

def kill_execution():

    global keep_running

    keep_running = False

    output_text.insert(
        tk.END,
        "Translation stopped.\n"
    )


# =========================================================
# ABOUT WINDOW
# =========================================================

def open_about_page():

    about_window = tk.Toplevel(win)

    about_window.title("About")

    about_window.geometry("500x300")

    if os.path.exists(ICON_PATH):
        about_window.iconphoto(
            False,
            icon
        )


    github_link = ttk.Label(
        about_window,
        text="GitHub: SamirPaulb/real-time-voice-translator",
        foreground="blue",
        cursor="hand2"
    )

    github_link.pack(
        pady=10
    )


    def open_webpage():

        import webbrowser

        webbrowser.open(
            "https://github.com/SamirPaulb/real-time-voice-translator"
        )


    github_link.bind(
        "<Button-1>",
        lambda event: open_webpage()
    )


    about_text = tk.Text(
        about_window,
        height=10,
        width=55
    )

    about_text.insert(
        "1.0",
        """
Real-Time Voice Translator

This application listens to speech,
converts speech to text,
translates the text,
and converts the translated text
back into speech.

Select the input and output languages
and press Start Translation.
"""
    )

    about_text.config(
        state="disabled"
    )

    about_text.pack(
        pady=10
    )


    close_button = tk.Button(
        about_window,
        text="Close",
        command=about_window.destroy
    )

    close_button.pack(
        pady=5
    )


# =========================================================
# BUTTONS
# =========================================================

run_button = tk.Button(
    win,
    text="Start Translation",
    command=run_translator,
    width=18
)

run_button.place(
    relx=0.25,
    rely=0.9,
    anchor="c"
)


kill_button = tk.Button(
    win,
    text="Stop Translation",
    command=kill_execution,
    width=18
)

kill_button.place(
    relx=0.5,
    rely=0.9,
    anchor="c"
)


about_button = tk.Button(
    win,
    text="About",
    command=open_about_page,
    width=18
)

about_button.place(
    relx=0.75,
    rely=0.9,
    anchor="c"
)


# =========================================================
# START TKINTER
# =========================================================

win.mainloop()