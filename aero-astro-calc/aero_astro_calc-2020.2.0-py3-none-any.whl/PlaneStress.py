from aero_astro_calc.dependencies.LatexLabel import LatexLabel
from bokeh.models import Arrow
from bokeh.plotting import figure, show
from numpy import cos, linspace, pi, sin, sqrt


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
                text=f"\\sigma_1 = {round(self.sigma_1,4)}",
                render_mode="css",
            )
        )
        plot.add_layout(
            LatexLabel(
                x=-1.8,
                y=1.4,
                text=f"\\sigma_2 = {round(self.sigma_2,4)}",
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

    def mohr(self):
        padding = 1.3
        midpoint = (self.sigma_1 + self.sigma_2) / 2

        plot = figure(
            x_range=[
                (midpoint - self.tau_max) * padding,
                (midpoint + self.tau_max) * padding,
            ],
            y_range=[-self.tau_max * padding, self.tau_max * padding],
        )

        # Bokeh circle is stupid so it has to be done the hard way.
        theta = linspace(0, 2 * pi, 200)
        sig1 = self.tau_max * cos(theta) + midpoint
        sig2 = self.tau_max * sin(theta)
        plot.line(x=sig1, y=sig2)

        # x axis
        plot.line(
            x=[
                (midpoint - self.tau_max) * padding,
                (midpoint + self.tau_max) * padding,
            ],
            y=[0, 0],
            line_color="black",
        )

        # y axis
        plot.line(
            x=[0, 0],
            y=[self.tau_max * padding, self.tau_max * -padding],
            line_color="black",
        )

        # Labels
        # sigma_1
        plot.circle(x=midpoint + self.tau_max, y=0, size=self.tau_max * 0.2)
        plot.add_layout(
            LatexLabel(
                x=midpoint + self.tau_max,
                y=self.tau_max * -0.1,
                text=f"\\sigma_1 = {round(self.sigma_1)}",
                render_mode="css",
            )
        )

        # sigma_2
        plot.circle(x=midpoint - self.tau_max, y=0, size=self.tau_max * 0.2)
        plot.add_layout(
            LatexLabel(
                x=midpoint - self.tau_max,
                y=self.tau_max * -0.1,
                text=f"\\sigma_2 = {round(self.sigma_2)}",
                render_mode="css",
            )
        )

        # tau_max
        plot.circle(x=midpoint, y=self.tau_max, size=sqrt(self.tau_max))
        plot.add_layout(
            LatexLabel(
                x=midpoint,
                y=self.tau_max * 0.9,
                text=f"\\tau_{{max}} = {round(self.tau_max)}",
                render_mode="css",
            )
        )

        show(plot)
