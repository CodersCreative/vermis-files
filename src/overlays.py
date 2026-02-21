from constants import *
from widgets import *
import customtkinter as ctk


class Overlay(ctk.CTkFrame):
    def __init__(self, master, on_pause, on_spray, on_rise, **kwargs):
        super().__init__(master, fg_color=TEXT_COLOUR, **kwargs)
        row_frame = ctk.CTkFrame(self, fg_color="transparent")
        row_frame.pack(padx=10)
        quit = ctk.CTkButton(
            row_frame,
            text="",
            image=master.assets.close,
            width=18,
            command=master.quit_app,
            fg_color="transparent",
            text_color=DEFAULT_COLOUR,
            hover_color=ACCENT_COLOUR,
        )
        quit.pack(side="left", padx=(0, PADDING_SMALL))
        options = ctk.CTkButton(
            row_frame,
            text="",
            image=master.assets.settings,
            width=18,
            command=master.open_settings,
            fg_color="transparent",
            text_color=DEFAULT_COLOUR,
            hover_color=ACCENT_COLOUR,
        )
        options.pack(side="left", padx=PADDING_SMALL)
        pause = ctk.CTkButton(
            row_frame,
            text="",
            image=master.assets.pause,
            width=18,
            command=on_pause,
            fg_color="transparent",
            text_color=DEFAULT_COLOUR,
            hover_color=ACCENT_COLOUR,
        )
        pause.pack(side="left", padx=PADDING_SMALL)
        spray = ctk.CTkButton(
            row_frame,
            text="",
            image=master.assets.spray,
            width=18,
            command=on_spray,
            fg_color="transparent",
            text_color=DEFAULT_COLOUR,
            hover_color=ACCENT_COLOUR,
        )
        spray.pack(side="left", padx=PADDING_SMALL)
        rise = ctk.CTkButton(
            row_frame,
            text="",
            image=master.assets.arrow_up,
            width=18,
            command=on_rise,
            fg_color="transparent",
            text_color=DEFAULT_COLOUR,
            hover_color=ACCENT_COLOUR,
        )
        rise.pack(side="left", padx=(PADDING_SMALL, 0))
        buttons_seperator = Line(self, color=DEFAULT_COLOUR)
        buttons_seperator.pack(pady=PADDING_SMALL, fill="x", padx=10)
        confidence = ctk.CTkLabel(
            self, text="10%", font=MEDIUM_FONT, text_color=DEFAULT_COLOUR, anchor="w"
        )
        confidence.pack(fill="x", pady=0, ipady=0, padx=10)
        confidence_seperator = Line(self, color=DEFAULT_COLOUR)
        confidence_seperator.pack(pady=PADDING_SMALL, fill="x", padx=10)
        stage_label = ctk.CTkLabel(
            self,
            text="Stage : Searching...",
            font=TINY_BOLD_FONT,
            text_color=DEFAULT_COLOUR,
            anchor="w",
        )
        stage_label.pack(fill="x", pady=0, padx=10)
        stage_label = ctk.CTkLabel(
            self,
            text="Uptime : 10hrs",
            font=TINY_BOLD_FONT,
            text_color=DEFAULT_COLOUR,
            anchor="w",
        )
        stage_label.pack(fill="x", pady=0, padx=10)
        stage_label = ctk.CTkLabel(
            self,
            text="Battery : 90%",
            font=TINY_BOLD_FONT,
            text_color=DEFAULT_COLOUR,
            anchor="w",
        )
        stage_label.pack(fill="x", pady=0, padx=10)
        stage_label = ctk.CTkLabel(
            self,
            text="Distance : 10km",
            font=TINY_BOLD_FONT,
            text_color=DEFAULT_COLOUR,
            anchor="w",
        )
        stage_label.pack(fill="x", pady=0, padx=10)
