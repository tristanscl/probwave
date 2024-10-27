import src
import custom_ttk as cttk
import ttkbootstrap as ttk
import datetime as dt
from ttkbootstrap.dialogs import Messagebox
import matplotlib.pyplot as plt
import pandas as pd
from tkinter import filedialog


DATE_FORMAT = r"%Y-%d-%m"

app = cttk.CApp("Probwave")
app.columnconfigure((0, 1), weight=1, uniform="equal")
app.rowconfigure((0, 1), weight=1, uniform="equal")

data_params = cttk.CFrame(app).grid(0, 0)
data_plot = cttk.CMatplotlibFigure(app).grid(0, 1)
forecast_params = cttk.CScrollableFrame(app).grid(1, 0)
forecast_plot = cttk.CMatplotlibFigure(app).grid(1, 1)

data: pd.Series = pd.Series()
cur: str = "USD"
asset: str = ""


def download() -> None:
    global cur, asset
    asset = asset_le.entry.get()
    start = dt.datetime.strptime(start_le.entry.get(), DATE_FORMAT).date()
    end = dt.datetime.strptime(end_le.entry.get(), DATE_FORMAT).date()
    cur = cur_le.entry.get()

    try:
        global data
        data = src.get_data(asset, start, end)
        data = src.clean_data(data)
        data = src.unsplit(data)
        data = src.convert_data(data, cur)
        data = src.unsplit(data)

        plt.figure()
        plt.clf()
        plt.plot(data.index, data)
        plt.title("Data - " + data.name)  # type: ignore
        plt.grid()
        plt.xticks(rotation=45)
        plt.ylabel(cur)
        plt.tight_layout()
        fig = plt.gcf()
        data_plot.figure = fig
        data_plot.grid(0, 1)

        forecast_button.configure("normal")

        save_data_plot_button.pack(expand=False)

    except Exception as e:
        Messagebox.show_error(str(e), "Error")


def forecast() -> None:
    model_name = model_variable.get()
    if model_name == "GBM":
        model = src.GBM()
    elif model_name == "AR1":
        model = src.AR1()
    forecast_start = dt.datetime.strptime(
        forecast_start_le.entry.get(), DATE_FORMAT
    ).date()
    n_days = int(n_days_le.entry.get())
    n_sim = int(n_sim_le.entry.get())
    n_sim_plot = int(n_sim_plot_le.entry.get())
    n_levels = int(n_levels_le.entry.get())
    alpha_sim_plot = float(alpha_sim_plot_le.entry.get())
    n_days_plot = int(n_days_plot_le.entry.get())

    try:
        train_set = data[:forecast_start]  # type: ignore
        model.fit(train_set)
        sim = model.sample(n_days, n_sim)

        plt.figure()
        plt.clf()
        src.prob_wave_plot(
            sim,
            forecast_start,
            data.iloc[-n_days_plot:],
            cur,
            n_levels,
            n_sim_plot,
            alpha_sim_plot,
        )
        fig = plt.gcf()
        forecast_plot.figure = fig
        forecast_plot.grid(1, 1)

        save_forecast_plot_button.pack(expand=False)

    except Exception as e:
        Messagebox.show_error(str(e), "Error")


def save_data_fig(event=None) -> None:
    path = filedialog.asksaveasfilename(
        defaultextension=".png",
        filetypes=[("PNG", ".png"), ("JPEG", ".jpeg"), ("PDF", ".pdf")],
        initialfile=asset + "_data",
    )
    if path:
        data_plot.canvas.figure.savefig(path)


def save_forecast_fig(event=None) -> None:
    path = filedialog.asksaveasfilename(
        defaultextension=".png",
        filetypes=[("PNG", ".png"), ("JPEG", ".jpeg"), ("PDF", ".pdf")],
        initialfile=asset + "_forecast",
    )
    if path:
        forecast_plot.canvas.figure.savefig(path)


asset_le = cttk.CLabelEntry(data_params.widget, "Asset").pack(expand=False)
start_le = cttk.CLabelEntry(data_params.widget, "Start", "2000-01-01").pack(
    expand=False
)
end_le = cttk.CLabelEntry(
    data_params.widget, "End", dt.datetime.now().strftime(DATE_FORMAT)
).pack(expand=False)
cur_le = cttk.CLabelEntry(data_params.widget, "Currency", "EUR").pack(expand=False)
download_button = cttk.CButton(data_params.widget, "Download", download).pack(
    expand=False
)
save_data_plot_button = cttk.CButton(
    data_params.widget, "Save data", command=save_data_fig
)

model_variable = ttk.StringVar(value="GBM")
model_choice = cttk.CLabelChoice(
    forecast_params.widget, model_variable, ["GBM", "AR1"], label="Model"
).pack(expand=False)
forecast_start_le = cttk.CLabelEntry(
    forecast_params.widget, "Forecast start", dt.datetime.now().strftime(DATE_FORMAT)
).pack(expand=False)
n_days_le = cttk.CLabelEntry(
    forecast_params.widget, "Number of simulated days", str(src.TRADING_YEAR)
).pack(expand=False)
n_sim_le = cttk.CLabelEntry(
    forecast_params.widget, "Number of simulations", str(10_000)
).pack(expand=False)
n_sim_plot_le = cttk.CLabelEntry(
    forecast_params.widget, "Number of plotted simulations", str(3)
).pack(expand=False)
n_levels_le = cttk.CLabelEntry(forecast_params.widget, "Number of levels", str(10))
alpha_sim_plot_le = cttk.CLabelEntry(
    forecast_params.widget, "Opacity of plotted simulations", str(0.3)
).pack(expand=False)
n_days_plot_le = cttk.CLabelEntry(
    forecast_params.widget, "Number of plotted days", str(1000)
).pack(expand=False)
forecast_button = cttk.CButton(
    forecast_params.widget, "Forecast", forecast, state="disabled"
).pack(expand=False)
save_forecast_plot_button = cttk.CButton(
    forecast_params.widget, "Save forecast", command=save_forecast_fig
)


if __name__ == "__main__":
    app.mainloop()
