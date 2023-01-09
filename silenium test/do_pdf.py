from fpdf import FPDF


def do_pdf(dict_, name):
    pdf = FPDF()
    pdf.add_page()
    for key in dict_:
        pdf.image(f'{dict_[key]}', x=None, y=None, w=190, h=0, type='', link=f'{key}')
    return pdf.output(f"{name}.pdf")
