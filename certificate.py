'''Certificate Generator #1'''
import os
from io import BytesIO
from typing import Literal

from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Image, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from barcode import get_barcode_class
from barcode.writer import ImageWriter

__version__ = "0.1.0"

class CertificateGenerator:
    def __init__(self, file_path: str, student_name: str, group_name: str, direction_number: int, direction_name: str,
                 study_type: Literal["очная", "заочная"], level: str, faculty_name: str, issue_date: str, course_num: int, certificate_num: str,
                 dean_signature_path: str, secretary_signature_path: str, seal_image_path: str,
                 ministry: str, university_name: str) -> None:
        '''
        - file_path: The file path where the generated certificate PDF will be saved.
        - student_name: The name of the student for whom the certificate is issued.
        - group_name: The name of the student's academic group.
        - direction_number: The numerical code representing the educational direction.
        - direction_name: The name of the educational direction.
        - study_type: The type of study (e.g., "очная" for offline study, "заочная" for online study).
        - level: The academic level (e.g., "бакалавр", "магистр").
        - faculty_name: The name of the faculty issuing the certificate. (e.g, "Институт компьютерных технологий и искусственного интеллекта")
        - issue_date: The date when the certificate is issued (format: "DD.MM.YYYY").
        - course_num: The course number of the student.
        - certificate_num: The unique identification number of the certificate.
        - dean_signature_path: The file path to the image of the dean's signature.
        - secretary_signature_path: The file path to the image of the secretary's signature.
        - seal_image_path: The file path to the image of the seal.
        - ministry: Official name of the ministry.
        - university_name: University name issuing this certificate.
        '''
        self.file_path = file_path
        self.student_name = student_name
        self.group_name = group_name
        self.direction_number = direction_number
        self.direction_name = direction_name
        self.study_type = study_type
        self.level = level
        self.faculty_name = faculty_name
        self.issue_date = issue_date
        self.course_num = course_num
        self.certificate_num = certificate_num
        self.dean_signature_path = dean_signature_path
        self.secretary_signature_path = secretary_signature_path
        self.seal_image_path = seal_image_path
        self.ministry = ministry
        self.university_name = university_name

        self.doc = SimpleDocTemplate(self.file_path, pagesize=letter)
        self.styles = getSampleStyleSheet()
        self.normal_style = self.styles['Normal']
        pdfmetrics.registerFont(TTFont('ArialUnicode', 'ARIALUNI.TTF'))

        # custom style (to support Russian)
        self.custom_style = ParagraphStyle(
            'CustomStyle',
            parent=self.normal_style,
            fontName='ArialUnicode',
            alignment=1,  # Center-aligned
            fontSize=10
        )

    def _draw_seal(self, canvas, doc, seal_image_path):
        seal_image = Image(seal_image_path, width=100, height=100)
        seal_image.drawOn(canvas, doc.width - 75, 260)

    def _generate_barcode_image(self):
        '''Generate barcode image containing certificate number'''
        barcode_data = self.certificate_num
        code128 = get_barcode_class('code128')
        code128_img = code128(barcode_data, writer=ImageWriter())
        barcode_image_data = BytesIO()
        code128_img.write(barcode_image_data)
        return Image(barcode_image_data, width=150, height=30)

    def _add_paragraph(self, text):
        return Paragraph(text, self.custom_style)

    def _add_spacer(self, height=12):
        return Spacer(1, height)

    def _add_image_paragraph(self, text, image_path, target_width=80):
        img = Image(image_path, width=target_width, height=target_width)
        aspect_ratio = img.imageWidth / img.imageHeight

        adjusted_height = target_width / aspect_ratio

        image_text = f"<font size=10 color=black>{text} <img src='{image_path}' width='{target_width}' height='{adjusted_height}'/></font>"
        return self._add_paragraph(image_text)


    def _add_title(self):
        title_text = f"<font size=12 color=black>{self.ministry}<br/>" \
                     f"{self.university_name}<br/>{self.direction_name}</font>"
        return self._add_paragraph(title_text)

    def _add_ref_number(self):
        ref_number_text = f"<font size=12 color=black>СПРАВКА № {self.certificate_num}<br/><br/>" \
                          f"Настоящая справка подтверждает то, что</font>"
        return self._add_paragraph(ref_number_text)

    def _add_student_info(self):
        student_info_text = f"<font size=12 color=black>{self.student_name}<br/>" \
                            f"действительно является студентом (кой) {self.course_num}-курса группы {self.group_name}<br/>" \
                            f"направлении: {self.direction_number}. {self.direction_name} ({self.study_type}, {self.level})<br/>" \
                            f"{self.faculty_name}</font>"
        return self._add_paragraph(student_info_text)

    def _add_issue_date(self):
        issue_date_text = f"<font size=10 color=black>Справка выдана по месту требования.<br/><br/>{self.issue_date}</font>"
        return self._add_paragraph(issue_date_text)

    def _add_signatures(self):
        dean_signature = self._add_image_paragraph("Декан (Директор):", self.dean_signature_path)
        secretary_signature = self._add_image_paragraph("Секретарь (методист) факультета:", self.secretary_signature_path)

        return [self._add_spacer(), self._add_spacer(), dean_signature, self._add_spacer(),self._add_spacer(), secretary_signature]

    def generate_certificate(self) -> None:
        content = [self._add_title(), self._add_spacer(), self._add_ref_number(), self._add_spacer(),
                   self._add_student_info(), self._add_spacer(), self._add_issue_date(), self._add_spacer(),
                   self._generate_barcode_image(), self._add_spacer(), *self._add_signatures()]

        self.doc.build(content, onFirstPage=lambda canvas, doc: self._draw_seal(canvas, doc, self.seal_image_path))

if __name__ == "__main__":
    # Example usage
    generator = CertificateGenerator(
        file_path="certificate.pdf",
        student_name="ФИО студента",
        group_name="Группа",
        direction_number="0000000",
        direction_name="Название бакалавриата",
        study_type="очная",
        level="бакалавр",
        faculty_name="Название факультета",
        issue_date="17.01.2023",
        course_num=3,
        certificate_num="1-1111-11111111-1", # Unique number for every certificate
        dean_signature_path=os.path.join("test_images","signature.png"),
        secretary_signature_path=os.path.join("test_images","signature1.png"),
        seal_image_path=os.path.join("test_images","seal.jpg"),
        ministry="МИНИСТЕРСТВО ОБРАЗОВАНИЯ И НАУКИ СТРАНЫ",
        university_name="Университет Silk Road Innovations"

    )
    generator.generate_certificate()