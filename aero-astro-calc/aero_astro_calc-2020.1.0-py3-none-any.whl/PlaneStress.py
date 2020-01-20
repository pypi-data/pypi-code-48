from math import sqrt

from bokeh.models import Arrow
from bokeh.plotting import figure, output_file, show

from aero_astro_calc.dependencies.LatexLabel import LatexLabel


class PlaneStress:
    def __init__(self, sigma_x, sigma_y, tau_xy):
        self.sigma_x = sigma_x
        self.sigma_y = sigma_y
        self.tau_xy = tau_xy

        self.tau_max = sqrt(((self.sigma_x - self.sigma_y) / 2) ** 2 + self.tau_xy ** 2)
        self.sigma_1 = ((self.sigma_x + self.sigma_y) / 2) + self.tau_max
        self.sigma_2 = ((self.sigma_x + self.sigma_y) / 2) - self.tau_max

    def plane(self):
        # Settings to make the plot look correct.
        plot = figure(x_range=(-5, 5), y_range=(-5, 5))
        plot.axis.major_label_text_font_size = "0pt"
        plot.axis.major_tick_line_color = None
        plot.axis[0].ticker.num_minor_ticks = 0
        plot.axis[1].ticker.num_minor_ticks = 0
        plot.grid.visible = False
        plot.axis.visible = False

        # Draw the rectangle
        plot.rect(0, 0, 4, 4, fill_alpha=0, line_color="black", line_width=3)

        # sigma_x
        plot.add_layout(Arrow(x_start=2, y_start=0, x_end=4.5, y_end=0))
        plot.add_layout(Arrow(x_start=-2, y_start=0, x_end=-4.5, y_end=0))
        plot.add_layout(
            LatexLabel(
                x=3.0, y=0.7, text=f"\\sigma_{{x}} = {self.sigma_x}", render_mode="css"
            )
        )

        # sigma_y
        plot.add_layout(Arrow(x_start=0, y_start=2, x_end=0, y_end=4.5))
        plot.add_layout(Arrow(x_start=0, y_start=-2, x_end=0, y_end=-4.5))
        plot.add_layout(
            LatexLabel(
                x=0.25, y=4, text=f"\\sigma_{{y}} = {self.sigma_y}", render_mode="css"
            )
        )

        # tau_xy
        plot.add_layout(Arrow(x_start=2.5, y_start=-2, x_end=2.5, y_end=2.2))
        plot.add_layout(Arrow(y_start=2.5, x_start=-2, y_end=2.5, x_end=2.2))
        plot.add_layout(Arrow(x_start=-2.5, y_start=2, x_end=-2.5, y_end=-2.2))
        plot.add_layout(Arrow(y_start=-2.5, x_start=2, y_end=-2.5, x_end=-2.2))
        plot.add_layout(
            LatexLabel(
                x=2.5, y=2.6, text=f"\\tau_{{xy}} = {self.tau_xy}", render_mode="css"
            )
        )

        # Other calculations
        plot.add_layout(
            LatexLabel(
                x=-1.8,
                y=1.8,
                text=f"\sigma_1 = {round(self.sigma_1,4)}",
                render_mode="css",
            )
        )
        plot.add_layout(
            LatexLabel(
                x=-1.8,
                y=1.4,
                text=f"\sigma_2 = {round(self.sigma_2,4)}",
                render_mode="css",
            )
        )
        plot.add_layout(
            LatexLabel(
                x=-1.8,
                y=1,
                text=f"\\tau_{{max}} = {round(self.tau_max,4)}",
                render_mode="css",
            )
        )

        show(plot)

