import ttkbootstrap as ttk
from abc import ABC, abstractmethod
from typing import Self, Callable
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from enum import Enum
from ttkbootstrap.constants import *  # type: ignore

PAD = 10
BIG = 20
SMALL = 12
MEDIUM = 16
FONT = "Microsoft JhengHei Light"


class CApp(ttk.Window):
    def __init__(self, app_name: str = "App") -> None:
        super().__init__(app_name, "superhero")
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        app_width = 2 * screen_width // 3
        app_height = 2 * screen_height // 3
        app_x = (screen_width - app_width) // 2
        app_y = (screen_height - app_height) // 2
        self.geometry(f"{app_width}x{app_height}+{app_x}+{app_y}")
        self.state("zoomed")


class CWidget(ABC):
    @abstractmethod
    def __init__(self) -> None:
        pass

    def pack(self, pad: bool = True, expand: bool = True, anchor: str = "w") -> Self:
        if pad and expand:
            self.widget.pack(padx=PAD, pady=PAD, expand=expand, anchor=anchor)  # type: ignore
        elif pad and not expand:
            self.widget.pack(padx=PAD, pady=PAD, anchor=anchor)  # type: ignore
        elif not pad and expand:
            self.widget.pack(expand=expand, anchor=anchor)  # type: ignore
        else:
            self.widget.pack(anchor=anchor)  # type: ignore
        return self

    def grid(self, line: int, col: int, pad: bool = True, expand: bool = True) -> Self:
        if pad and expand:
            self.widget.grid(row=line, column=col, padx=PAD, pady=PAD, sticky="nsew")  # type: ignore
        elif pad and not expand:
            self.widget.grid(row=line, column=col, padx=PAD, pady=PAD)  # type: ignore
        elif not pad and expand:
            self.widget.grid(row=line, column=col, sticky="nsew")  # type: ignore
        else:
            self.widget.grid(row=line, column=col)  # type: ignore
        return self


class CFrame(CWidget):
    def __init__(self, master) -> None:
        self.widget = ttk.Frame(master)


class CScrollableFrame(CWidget):
    def __init__(self, master) -> None:
        # Création d'un Frame pour le Canvas et la Scrollbar
        self.container = ttk.Frame(master)

        # Création du Canvas
        self.canvas = ttk.Canvas(self.container)
        self.canvas.pack(expand=True, fill="both", anchor="center")

        # Création de la Scrollbar verticale et liaison avec le Canvas
        scrollbar = ttk.Scrollbar(
            self.container, orient="vertical", command=self.canvas.yview
        )
        scrollbar.place(relx=1, rely=0, relheight=1, anchor="ne")
        self.canvas.configure(yscrollcommand=scrollbar.set)

        # Création de la Frame à l'intérieur du Canvas
        self.widget = ttk.Frame(self.canvas)
        self.canvas.create_window(
            (self.canvas.winfo_width() // 2, self.canvas.winfo_height() // 2),
            window=self.widget,
            anchor="center",
        )

        # Configuration de la Frame pour qu'elle s'ajuste au contenu
        def on_frame_configure(event):
            self.canvas.configure(scrollregion=self.canvas.bbox("all"))

        self.widget.bind("<Configure>", on_frame_configure)

        self.canvas.bind_all(
            "<MouseWheel>",
            lambda e: self.canvas.yview_scroll(int(-1 * (e.delta / 120)), "units"),
        )

    def pack(self, pad: bool = True, expand: bool = True, anchor: str = "w") -> Self:
        if pad and expand:
            self.container.pack(padx=PAD, pady=PAD, expand=expand, anchor=anchor)  # type: ignore
        elif pad and not expand:
            self.container.pack(padx=PAD, pady=PAD, anchor=anchor)  # type: ignore
        elif not pad and expand:
            self.container.pack(expand=expand, anchor=anchor)  # type: ignore
        else:
            self.container.pack(anchor=anchor)  # type: ignore
        return self

    def grid(self, line: int, col: int, pad: bool = True, expand: bool = True) -> Self:
        if pad and expand:
            self.container.grid(row=line, column=col, padx=PAD, pady=PAD, sticky="nsew")  # type: ignore
        elif pad and not expand:
            self.container.grid(row=line, column=col, padx=PAD, pady=PAD)  # type: ignore
        elif not pad and expand:
            self.container.grid(row=line, column=col, sticky="nsew")  # type: ignore
        else:
            self.container.grid(row=line, column=col)  # type: ignore
        return self


class CLabel(CWidget):
    def __init__(self, master, label: str) -> None:
        self.widget = ttk.Label(master, text=label)


class CEntry(CWidget):
    def __init__(self, master, default_value: str = "") -> None:
        self.widget = ttk.Entry(master)
        self.widget.insert(0, default_value)


class CLabelEntry(CWidget):
    def __init__(self, master, label: str, default_value: str = "") -> None:
        self.widget = ttk.Frame(master)
        self.label = ttk.Label(self.widget, text=label)
        self.label.grid(row=0, column=0, padx=PAD, pady=PAD)
        self.entry = ttk.Entry(self.widget)
        self.entry.insert(0, default_value)
        self.entry.grid(row=0, column=1, padx=PAD, pady=PAD)


class CRadiobutton(CWidget):
    def __init__(self, master, variable, value: str) -> None:
        self.widget = ttk.Radiobutton(
            master, variable=variable, value=value, text=value
        )


class CChoice(CWidget):
    def __init__(self, master, variable, values: list[str]) -> None:
        self.widget = ttk.Frame(master)
        for i in range(len(values)):
            value = values[i]
            ttk.Radiobutton(
                self.widget, variable=variable, value=value, text=value
            ).grid(row=0, column=i, padx=PAD, pady=PAD)


class CLabelChoice(CWidget):
    def __init__(self, master, variable, values: list[str], label: str) -> None:
        self.widget = ttk.Frame(master)
        ttk.Label(self.widget, text=label).grid(row=0, column=0, padx=PAD, pady=PAD)
        for i in range(len(values)):
            value = values[i]
            ttk.Radiobutton(
                self.widget, variable=variable, value=value, text=value
            ).grid(row=0, column=i + 1, padx=PAD, pady=PAD)


class CButton(CWidget):
    def __init__(
        self, master, text: str, command: Callable = lambda: None, state: str = "normal"
    ) -> None:
        self.widget = ttk.Button(master, text=text, command=command, state=state)

    def configure(self, state: str):
        self.widget.configure(state=state)


class CMatplotlibFigure(CWidget):
    def __init__(
        self, master, figure=None, default_message="Plot will appear here."
    ) -> None:
        self.widget = ttk.Frame(master)
        if figure is not None:
            self.canvas = FigureCanvasTkAgg(figure, self.widget)
            self.canvas.draw()
            self.canvas.get_tk_widget().pack(expand=True)  # type: ignore
            self._figure = figure
        else:
            self.label = ttk.Label(self.widget, text=default_message)
            self.label.pack(padx=PAD, pady=PAD, expand=True)

    @property
    def figure(self):
        return self._figure

    @figure.setter
    def figure(self, value):
        self.label.pack_forget()
        if hasattr(self, "canvas"):
            self.canvas.get_tk_widget().pack_forget()
        self._figure = value
        self.canvas = FigureCanvasTkAgg(value, self.widget)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(expand=True)
