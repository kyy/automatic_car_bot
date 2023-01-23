import numpy as np
import pandas as pd
from fpdf import FPDF, ViewerPreferences
import qrcode
from datetime import datetime
import csv


class PDF(FPDF):

    def imports(self):
        self.filter_full = None
        self.filter_short = None
        self.av_by_link = None

    def header(self):
        # Rendering QRC:
        img = qrcode.make(self.av_by_link)
        self.image(
            img.get_image(),
            x=273,
            y=3,
            w=19,
            link=self.av_by_link,
            title='av.by',
            alt_text='av.by',
        )
        # Rendering logo:
        self.image(
            f"b_logic/static/logo.png",
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
        self.cell(-18, 0, f'{datetime.now().date()}', align="R")
        self.ln(4)
        self.cell(259, 0, f'{datetime.now().time().strftime("%H:%M")}', align="R")
        self.ln(4)
        self.cell(13)
        self.cell(10, -8, f'{self.filter_full}', align="L")
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_text_color(60, 60, 60)
        self.set_font(size=9)
        # Printing page number:
        self.cell(0, 10, f"страница {self.page_no()}/{{nb}}", align="C")

    def colored_table(self, headings, rows, links, comments, col_widths=(7, 28, 41, 16, 80, 25, 25, 25, 32)):
        self.render_table_header(headings=headings, col_widths=col_widths)
        line_height = self.font_size * 2.5
        self.set_fill_color(240, 240, 240)                                                                              # цвет заливки строки
        self.set_text_color(0)                                                                                          # цвет текста в заливке
        fill = False                                                                                                    # заливаем строку
        j = 0
        for row in rows:
            if self.will_page_break(line_height):
                self.render_table_header(headings=headings, col_widths=col_widths)
            i = 0
            link = links[j]
            j += 1
            for datum in row:
                link_to_car = link if i == 2 else ''                                                                    # создаем ссылку во 2 столбце
                self.multi_cell(
                    w=col_widths[i],
                    h=line_height,
                    txt=datum,
                    align="L",
                    border=1,
                    new_x="RIGHT",
                    new_y="TOP",
                    max_line_height=self.font_size+1.2,
                    link=link_to_car,
                    fill=fill,
                )
                i += 1
            fill = not fill                                                                                             # убираем заливку строки
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


def do_pdf(
        data: [[str], ] = None,
        name=None,
        filter_full='<filter full>',
        filter_short='<filter code>',
        av_by_link='<link_to_av_by_filter>'
):
    data, col_names, links, comments = get_data()
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
    pdf.add_font(fname=f'b_logic/static/DejaVuSansCondensed.ttf')
    pdf.set_font('DejaVuSansCondensed', size=9)
    pdf.filter_full = str(filter_full)
    pdf.filter_short = str(filter_short)
    pdf.av_by_link = str(av_by_link)
    pdf.add_page()
    pdf.set_title("@AutomaticCar")
    pdf.set_author("@AutomaticCar")
    pdf.colored_table(col_names, data, links, comments)
    return pdf.output(f'{name}.pdf')


def get_data():
    columns = ['#', 'обмен', 'марка', 'цена', 'характеристики', 'дата', 'город', 'владелец', 'телефон']
    dataframe = pd.DataFrame(np.load('parse_av_by.npy'))
    df = dataframe.iloc[0:, 2:].to_numpy()
    links = dataframe.iloc[0:, 0].tolist()
    comments = dataframe.iloc[0:, 1].tolist()
    print(comments)
    return df, columns, links, comments


if __name__ == '__main__':
    do_pdf()
