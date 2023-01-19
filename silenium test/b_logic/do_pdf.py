import numpy as np
from fpdf import FPDF, ViewerPreferences
import datetime
import csv


class PDF(FPDF):

    def filters_name(self):
        self.filter_full = None
        self.filter_short = None

    def header(self):
        # Rendering logo:
        self.image(
            "b_logic/static/logo.png",
            x=10,
            y=10,
            w=8,
            link="https://t.me/AutomaticCarBot",
            title='@AutomaticCarBot',
            alt_text='@AutomaticCarBot',
        )

        # Moving cursor to the right:
        self.cell(13)
        self.set_font(size=9)
        self.set_text_color(60, 60, 60)
        self.cell(0, 0, f'{self.filter_short}', align="L")
        self.cell(0, 0, f'{datetime.datetime.now()}', align="R")
        self.ln(4)
        self.cell(13)
        self.cell(10, 3, f'{self.filter_full}', align="L")
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_text_color(60, 60, 60)
        self.set_font(size=9)
        # Printing page number:
        self.cell(0, 10, f"страница {self.page_no()}/{{nb}}", align="C")

    def colored_table(self, headings, rows, col_widths=(8, 45, 15, 80, 35, 35, 35, 25)):
        self.render_table_header(headings=headings, col_widths=col_widths)
        line_height = self.font_size * 3
        self.set_fill_color(240, 240, 240)
        self.set_text_color(0)
        fill = False
        for row in rows:
            if self.will_page_break(line_height):
                self.render_table_header(headings=headings, col_widths=col_widths)
            i = 0
            for datum in row:
                self.multi_cell(
                    w=col_widths[i],
                    h=line_height,
                    txt=datum,
                    align="L",
                    border=1,
                    new_x="RIGHT",
                    new_y="TOP",
                    max_line_height=self.font_size,
                    link='',
                    fill=fill,
                )
                i += 1
            fill = not fill
            self.ln(line_height)

    def render_table_header(self, headings, col_widths):
        self.set_font(size=9)
        self.set_fill_color(60, 60, 60)
        self.set_text_color(240, 240, 240)
        self.set_draw_color(180, 180, 180)
        self.set_line_width(0.1)
        for col_width, heading in zip(col_widths, headings):
            self.cell(
                w=col_width,
                h=5,
                txt=heading,
                border=1,
                align="C",
                fill=True,
            )
        self.ln()
        # Color and font restoration:
        self.set_fill_color(240, 240, 240)
        self.set_text_color(0)


def load_data_from_csv(csv_filepath):
    headings, rows = [], []
    with open(csv_filepath, encoding="utf8") as csv_file:
        for row in csv.reader(csv_file, delimiter=","):
            if not headings:  # extracting column names from first row:
                headings = row
            else:
                rows.append(row)
    return headings, rows


def do_pdf(data: [[str], ] = None, name=None, filter_full=None, filter_short=None):
    data = np.load('parse_av_by.npy')
    col_names = ['#', 'марка', 'цена', 'характеристики', 'VIN', 'опубликовано', 'город', 'телефон']

    pdf = PDF(
        orientation="L",
        unit="mm",
        format="A4"
              )
    pdf.page_mode = "FULL_SCREEN"
    pdf.viewer_preferences = ViewerPreferences(
        hide_toolbar=True,
        hide_menubar=True,
        hide_window_u_i=True,
        fit_window=True,
        center_window=True,
        display_doc_title=True,
        non_full_screen_page_mode="USE_OUTLINES",
    )
    pdf.add_font(fname='b_logic/static/DejaVuSansCondensed.ttf')
    pdf.set_font('DejaVuSansCondensed', size=9)
    pdf.filter_full = f'{filter_full}'
    pdf.filter_short = f'{filter_short}'
    pdf.add_page()
    pdf.set_title("@AutomaticCar")
    pdf.set_author("@AutomaticCar")
    pdf.colored_table(col_names, data)
    return pdf.output(f'{name}.pdf')


if __name__ == '__main__':
    do_pdf()
