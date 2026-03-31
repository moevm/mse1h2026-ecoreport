from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer,
    PageBreak, ListFlowable, ListItem
)
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.pagesizes import A4
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from io import BytesIO
from jinja2 import Template
import os


class ReportGenerator:
    def __init__(self):
        self.BASE_DIR = os.path.dirname(os.path.abspath(__file__))

        # шрифт
        font_path = os.path.join(self.BASE_DIR, "Times New Roman", "timesnewromanpsmt.ttf")
        pdfmetrics.registerFont(TTFont("TimesNewRoman", font_path))

        # отступы
        self.LEFT_MARGIN = self.mm_to_pt(30)
        self.RIGHT_MARGIN = self.mm_to_pt(15)
        self.TOP_MARGIN = self.mm_to_pt(20)
        self.BOTTOM_MARGIN = self.mm_to_pt(20)
        self.FIRST_LINE_INDENT = self.mm_to_pt(12.5)


    def mm_to_pt(self, mm):
        return mm * 2.83464567


    # header/footer
    def header_footer_title(self, canvas, doc, full_name, short_name):
        canvas.saveState()
        width, height = A4

        style = ParagraphStyle(
            name="header",
            fontName="TimesNewRoman",
            fontSize=14,
            alignment=TA_CENTER,
            leading=16
        )

        top = Paragraph(full_name, style)
        w, h = top.wrap(doc.width, self.mm_to_pt(30))
        top.drawOn(canvas, doc.leftMargin, height - self.mm_to_pt(15) - h / 2)

        bottom = Paragraph(f"ПРЕДПРИЯТИЕ {short_name}", style)
        w, h = bottom.wrap(doc.width, self.mm_to_pt(30))
        bottom.drawOn(canvas, doc.leftMargin, self.mm_to_pt(15))

        canvas.restoreState()

    def header_footer_main(self, canvas, doc):
        canvas.saveState()
        if canvas.getPageNumber() > 1:
            canvas.setFont("TimesNewRoman", 12)
            width = doc.pagesize[0]
            canvas.drawCentredString(width / 2, self.mm_to_pt(10), str(canvas.getPageNumber()))
        canvas.restoreState()

    # list builder
    def create_list(self, items, normal_style):
        list_items = []

        for item in items:
            p = Paragraph(item, ParagraphStyle(
                name='list_item',
                parent=normal_style,
                firstLineIndent=0,
                leftIndent=10
            ))
            list_items.append(ListItem(p))

        return ListFlowable(
            list_items,
            bulletType='bullet',
            bulletFontName='TimesNewRoman',
            bulletFontSize=12,
            leftIndent=self.FIRST_LINE_INDENT + 12.5,
        )


    # section reader
    def read_section(self, file_path, title_style, normal_style, data_dict):
        elements = []

        if not os.path.exists(file_path):
            elements.append(Paragraph("Текст раздела отсутствует.", normal_style))
            return elements

        with open(file_path, "r", encoding="utf-8") as f:
            template = Template(f.read())

        rendered = template.render(**data_dict)

        buffer_list = []
        in_list = False

        for line in rendered.splitlines():
            line = line.strip()

            if not line:
                if buffer_list and in_list:
                    elements.append(self.create_list(buffer_list, normal_style))
                    buffer_list, in_list = [], False
                continue

            if line.startswith("TITLE:"):
                elements.append(Paragraph(line.replace("TITLE:", "").strip(), title_style))

            elif line.startswith("PARA:"):
                style = ParagraphStyle(
                    name='para',
                    parent=normal_style,
                    firstLineIndent=self.FIRST_LINE_INDENT
                )
                elements.append(Paragraph(line.replace("PARA:", "").strip(), style))

            elif line.startswith("LIST:"):
                in_list = True
                buffer_list = []

            elif in_list:
                buffer_list.append(line.lstrip('•-*').strip())

            else:
                style = ParagraphStyle(
                    name='para',
                    parent=normal_style,
                    firstLineIndent=self.FIRST_LINE_INDENT
                )
                elements.append(Paragraph(line, style))

        if buffer_list and in_list:
            elements.append(self.create_list(buffer_list, normal_style))

        return elements

    def generate(self, user_data) -> bytes:
        buffer = BytesIO()

        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            leftMargin=self.LEFT_MARGIN,
            rightMargin=self.RIGHT_MARGIN,
            topMargin=self.TOP_MARGIN,
            bottomMargin=self.BOTTOM_MARGIN
        )

        title_style = ParagraphStyle(
            name="title",
            fontName="TimesNewRoman",
            fontSize=14,
            leading=21,
            alignment=TA_CENTER
        )

        normal_style = ParagraphStyle(
            name="normal",
            fontName="TimesNewRoman",
            fontSize=12,
            leading=18,
            firstLineIndent=self.FIRST_LINE_INDENT,
            alignment=TA_JUSTIFY
        )

        elements = []

        # титульник
        elements.append(Spacer(1, self.mm_to_pt(90)))
        elements.append(Paragraph("ОТЧЕТ ПО ЭКОЛОГИЧЕСКОЙ БЕЗОПАСНОСТИ", title_style))
        elements.append(PageBreak())

        # разделы
        content_file = os.path.join(self.BASE_DIR, "report_module", "content.txt")

        if os.path.exists(content_file):
            with open(content_file, "r", encoding="utf-8") as f:
                sections = [line.strip() for line in f if line.strip()]

            for i, section in enumerate(sections, 1):
                section_file = os.path.join(self.BASE_DIR, "report_module", f"section_{i}.txt")
                elements.extend(
                    self.read_section(section_file, title_style, normal_style, user_data)
                )
                elements.append(PageBreak())

        doc.build(
            elements,
            onFirstPage=lambda c, d: self.header_footer_title(
                c, d,
                user_data["FULL_OBJECT_NAME"],
                user_data["SHORT_OBJECT_NAME"]
            ),
            onLaterPages=self.header_footer_main
        )

        buffer.seek(0)
        return buffer.getvalue()