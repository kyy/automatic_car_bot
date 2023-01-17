import os

import numpy as np
from fpdf import FPDF
import datetime
import csv

# prod pdf

class PDF(FPDF):

    def filters_names(self, filter_full, filter_short):
        self.filter_full = filter_full
        self.filter_short = filter_short

    def header(self):
        # Rendering logo:
        self.image("b_logic/static/logo.png", 10, 8, 8,
                   link="https://t.me/AutomaticCarBot",
                   title='@AutomaticCarBot',
                   alt_text='@AutomaticCarBot')

        # Moving cursor to the right:
        self.cell(13)
        self.set_font("DejaVuSansCondensed", "", 8)
        self.set_text_color(60, 60, 60)
        self.cell(2, 1, f"{self.filter_full}     {datetime.datetime.now()}", align="L")
        self.ln(4)
        self.cell(10, 1, f"{self.filter_short}     ", align="L")
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_text_color(60, 60, 60)
        self.set_font("DejaVuSansCondensed", "", 9)
        # Printing page number:
        self.cell(0, 10, f"страница {self.page_no()}/{{nb}}", align="C")

    def colored_table(self, headings, rows, col_widths=(8, 60, 15, 100, 22, 28, 22, 20)):
        # Colors, line width and bold font:
        self.set_font("DejaVuSansCondensed", "", 9)
        self.set_fill_color(60, 60, 60)
        self.set_text_color(240, 240, 240)
        self.set_draw_color(180, 180, 180)
        self.set_line_width(0.1)
        for col_width, heading in zip(col_widths, headings):
            self.cell(col_width, 5, heading, border=1, align="C", fill=True)
        self.ln()
        # Color and font restoration:
        self.set_fill_color(240, 240, 240)
        self.set_text_color(0)
        fill = False
        for row in rows:
            self.cell(col_widths[0], 10, row[0], border="LR", align="L", fill=fill)
            self.cell(col_widths[1], 10, row[1], border="LR", align="L", fill=fill)
            self.cell(col_widths[2], 10, row[2], border="LR", align="L", fill=fill)
            self.cell(col_widths[3], 10, row[3], border="LR", align="L", fill=fill)
            self.cell(col_widths[4], 10, row[4], border="LR", align="L", fill=fill)
            self.cell(col_widths[5], 10, row[5], border="LR", align="L", fill=fill)
            self.cell(col_widths[6], 10, row[6], border="LR", align="L", fill=fill)
            self.cell(col_widths[7], 10, row[7], border="LR", align="L", fill=fill)
            self.ln()
            fill = not fill
        self.cell(sum(col_widths), 0, "", "T")


def load_data_from_csv(csv_filepath):
    headings, rows = [], []
    with open(csv_filepath, encoding="utf8") as csv_file:
        for row in csv.reader(csv_file, delimiter=","):
            if not headings:  # extracting column names from first row:
                headings = row
            else:
                rows.append(row)
    return headings, rows



def do_pdf(data=None, name=None, filter_full=None, filter_short=None):
    col_names = ['#', 'марка', 'цена', 'характеристики', 'VIN', 'опубликовано', 'город', 'телефон']
    pdf = PDF(orientation="L", unit="mm", format="A4")
    pdf.filter_full = f'{filter_full}'
    pdf.filter_short = f'{filter_short}'
    pdf.add_font(fname='b_logic/static/DejaVuSansCondensed.ttf')
    pdf.set_font('DejaVuSansCondensed', size=9)
    pdf.add_page()
    pdf.set_title("Cars")
    pdf.set_author("Jules Verne")
    pdf.colored_table(col_names, data)
    return pdf.output(f'{name}.pdf')

# test pdf
# def do_pdf(dict_, name):
#     pdf = FPDF(orientation="L", unit="mm", format="A4")
#     pdf.add_page()
#     pdf.set_title("Title")
#     pdf.set_author("Jules Verne")
#
#     for key in dict_:
#         pdf.image(name=dict_[key], w=190, h=0, type='', link=key)
#     return pdf.output(f'{name}.pdf')

if __name__ == '__main__':
    do_pdf()
