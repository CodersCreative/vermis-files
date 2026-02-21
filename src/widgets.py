from constants import *
import customtkinter as ctk


class NamedSlider(ctk.CTkFrame):
    def __init__(
        self,
        master,
        input_var,
        label=">",
        from_=0,
        to=1,
        height=12,
        fg_color=ACCENT_COLOUR,
        txt_color=TEXT_COLOUR,
        handle_colour=TEXT_COLOUR,
        active_color=TEXT_COLOUR,
        active_hover_colour=TEXT_COLOUR,
        **kwargs,
    ):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.label = ctk.CTkLabel(
            self, text=label, font=SMALL_FONT, text_color=txt_color
        )
        self.label.pack(side="left", anchor="w", padx=PADDING_SMALL)

        self.slider = ctk.CTkSlider(
            self,
            variable=input_var,
            from_=from_,
            to=to,
            height=height,
            fg_color=fg_color,
            progress_color=active_color,
            button_color=handle_colour,
            button_hover_color=active_hover_colour,
        )
        self.slider.pack(
            side="left", anchor="e", expand=True, fill="x", padx=PADDING_SMALL
        )

        self.value = ctk.CTkLabel(
            self, textvariable=input_var, font=SMALL_FONT, text_color=txt_color
        )
        self.value.pack(side="left", anchor="w", padx=PADDING_SMALL)


class NamedEntry(ctk.CTkFrame):
    def __init__(
        self,
        master,
        input_var,
        label=">",
        fg_color=DEFAULT_COLOUR,
        txt_color=TEXT_COLOUR,
        **kwargs,
    ):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.label = ctk.CTkLabel(
            self, text=label, font=SMALL_FONT, text_color=txt_color
        )
        self.label.pack(side="left", anchor="w", padx=PADDING_SMALL)

        self.entry = ctk.CTkEntry(
            self,
            textvariable=input_var,
            fg_color=fg_color,
            text_color=txt_color,
            border_color=ALTERNATE_DARK_COLOUR,
            font=SMALL_FONT,
        )
        self.entry.pack(
            side="left", anchor="e", expand=True, fill="x", padx=PADDING_SMALL
        )


class NamedCheckbox(ctk.CTkFrame):
    def __init__(
        self,
        master,
        input_var,
        label=">",
        fg_color=DEFAULT_COLOUR,
        txt_color=TEXT_COLOUR,
        hover_color=TEXT_COLOUR,
        **kwargs,
    ):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.label = ctk.CTkLabel(
            self, text=label, font=SMALL_FONT, text_color=txt_color
        )
        self.label.pack(
            side="left", anchor="w", expand=True, fill="x", padx=PADDING_SMALL
        )

        self.checkbox = ctk.CTkCheckBox(
            self,
            variable=input_var,
            fg_color=fg_color,
            hover_color=hover_color,
            font=SMALL_FONT,
            text="",
        )
        self.checkbox.pack(side="left", anchor="e", padx=PADDING_SMALL)


class Line(ctk.CTkFrame):
    def __init__(
        self,
        master,
        orientation="horizontal",
        width=None,
        height=None,
        color=ACCENT_COLOUR,
        **kwargs,
    ):
        if orientation == "horizontal":
            height = 2 if height is None else height
            width = 1 if width is None else width
        else:
            width = 2 if width is None else width
            height = 1 if height is None else height

        super().__init__(master, width=width, height=height, fg_color=color, **kwargs)
