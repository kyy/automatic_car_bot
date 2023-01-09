from fpdf import FPDF


def do_pdf(dict_, name):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font('Times', '', 12)
    pdf.set_title('Cars')
    for key in dict_:
        pdf.image(name=dict_[key], x=None, y=None, w=190, h=0, type='', link=key)
    return pdf.output(f'{name}.pdf')
