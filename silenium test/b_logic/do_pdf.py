from fpdf import FPDF
import datetime
import csv


class PDF(FPDF):

    def header(self):
        # Rendering logo:
        self.image("static/logo.png", 10, 8, 15,
                   link="https://t.me/AutomaticCarBot",
                   title='@AutomaticCarBot',
                   alt_text='@AutomaticCarBot')

        # Setting font: helvetica bold 15
        self.set_font("DejaVuSansCondensed", "", 12)
        # Moving cursor to the right:
        self.cell(80)
        # Printing title:
        self.cell(30, 10, "Title", border=1, align="C")
        # Performing a line break:
        self.ln(20)

    def footer(self):
        # Position cursor at 1.5 cm from bottom:
        self.set_y(-15)
        # Setting font: helvetica italic 8
        self.set_font("DejaVuSansCondensed", "", 12)
        # Printing page number:
        self.cell(0, 10, f"Page {self.page_no()}/{{nb}}", align="C")

    def colored_table(self, headings, rows, col_widths=(40, 40, 40, 40, 40, 40, 36)):
        # Colors, line width and bold font:
        self.set_font("DejaVuSansCondensed", "", 12)
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
            self.cell(col_widths[6], 10, row[6], border="LR", align="R", fill=fill)
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


def do_pdf(dict_=None, name=666):
    col_names, data = load_data_from_csv('text.txt')
    pdf = PDF(orientation="L", unit="mm", format="A4")
    pdf.add_font(fname='static/DejaVuSansCondensed.ttf')
    pdf.set_font('DejaVuSansCondensed', size=14)
    pdf.add_page()
    pdf.set_title("Title")
    pdf.set_author("Jules Verne")
    pdf.colored_table(col_names, data)

    # for key in dict_:
    #     pdf.image(name=dict_[key], w=190, h=0, type='', link=key)
    return pdf.output(f'{name}.pdf')

if __name__ == '__main__':
    do_pdf()
