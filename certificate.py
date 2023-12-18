'''Certificate Generator #1'''
import os
from io import BytesIO
from typing import Literal, List, Dict

import qrcode
from barcode import get_barcode_class
from barcode.writer import ImageWriter
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Image, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

__version__ = "0.1.2"

# custom font (to support Russian)
module_directory = os.path.dirname(os.path.abspath(__file__))
font_path = os.path.join(module_directory, 'ARIALUNI.TTF')

pdfmetrics.registerFont(TTFont('ArialUnicode', font_path))
styles = getSampleStyleSheet()
normal_style = styles['Normal']
custom_style = ParagraphStyle(
    'CustomStyle',
    parent=normal_style,
    fontName='ArialUnicode',
    alignment=1,  # Center-aligned
    fontSize=10
)
    

def add_spacer(height=12):
    return Spacer(1, height)

def add_paragraph(text):
    return Paragraph(text, custom_style)

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

    def _add_image_paragraph(self, text, image_path, target_width=80):
        img = Image(image_path, width=target_width, height=target_width)
        aspect_ratio = img.imageWidth / img.imageHeight

        adjusted_height = target_width / aspect_ratio

        image_text = f"<font size=10 color=black>{text} <img src='{image_path}' width='{target_width}' height='{adjusted_height}'/></font>"
        return add_paragraph(image_text)


    def _add_title(self):
        title_text = f"<font size=12 color=black>{self.ministry}<br/>" \
                     f"{self.university_name}<br/>{self.direction_name}</font>"
        return add_paragraph(title_text)

    def _add_ref_number(self):
        ref_number_text = f"<font size=12 color=black>СПРАВКА № {self.certificate_num}<br/><br/>" \
                          f"Настоящая справка подтверждает то, что</font>"
        return add_paragraph(ref_number_text)

    def _add_student_info(self):
        student_info_text = f"<font size=12 color=black>{self.student_name}<br/>" \
                            f"действительно является студентом (кой) {self.course_num}-курса группы {self.group_name}<br/>" \
                            f"направлении: {self.direction_number}. {self.direction_name} ({self.study_type}, {self.level})<br/>" \
                            f"{self.faculty_name}</font>"
        return add_paragraph(student_info_text)

    def _add_issue_date(self):
        issue_date_text = f"<font size=10 color=black>Справка выдана по месту требования.<br/><br/>{self.issue_date}</font>"
        return add_paragraph(issue_date_text)

    def _add_signatures(self):
        dean_signature = self._add_image_paragraph("Декан (Директор):", self.dean_signature_path)
        secretary_signature = self._add_image_paragraph("Секретарь (методист) факультета:", self.secretary_signature_path)

        return [add_spacer(), add_spacer(), dean_signature, add_spacer(),add_spacer(), secretary_signature]

    def generate_certificate(self) -> None:
        content = [self._add_title(), add_spacer(), self._add_ref_number(), add_spacer(),
                   self._add_student_info(), add_spacer(), self._add_issue_date(), add_spacer(),
                   self._generate_barcode_image(), add_spacer(), *self._add_signatures()]

        self.doc.build(content, onFirstPage=lambda canvas, doc: self._draw_seal(canvas, doc, self.seal_image_path))

class CertificateGenerator2:
    def __init__(self, file_path: str, student_name: str, date_of_birth: int, course_num: int, group_name: str, faculty_name: str,
                 study_form: Literal["очная", "контракт"], period_start: int, period_end: int, normative_duration: int,
                 to_the_authority: str, certificate_num: str, executor_name: str, execution_date: str, qr_code_data: str, project_authority_name: str, project_authority_role, project_authority_sign_path: str,
                 ministry: str, university_name: str, seal_image_path: str, semesters: List[Dict[str, str]]) -> None:
        '''
        - file_path: The file path where the generated certificate PDF will be saved.
        - student_name: The name of the student for whom the certificate is issued.
        - date_of_birth: The birth year of the student. (format: "DD.MM.YYYY")
        - course_num: The course number of the student.
        - group_name: The name of the student's academic group.
        - faculty_name: The name of the faculty issuing the certificate.
        - study_form: The form of study (e.g., "очная", "контракт").
        - period_start: The start date of the study period (format: YYYY).
        - period_end: The end date of the study period (format: YYYY).
        - normative_duration: The normative duration of the study.
        - to_the_authority: The authority requesting the certificate. For whom this certificate is.
        - certificate_num: The unique identification number of the certificate.
        - executor_name: The name of the executor.
        - executor_date: The date of the execution of the document, by executor (format: DD.MM.YYYY).
        - qr_code_data: What should be shown inside QR code.
        - project_authority_name: Name of the project authority.
        - project_authority_role: Role of the authority.
        - project_authority_sign_path: The file path to the image of the project authority's signature.
        - ministry: Official name of the ministry.
        - university_name: University name issuing this certificate.
        - seal_image_path: File path to the seal image.
        - semesters: List of dictionaries representing each semester with parameters "name", "start", and "end". e.g: [{"name": "осенний семестр", "start": "01.09.2022", "end": "31.12.2022"}, ...],
        '''
        self.file_path = file_path
        self.student_name = student_name
        self.date_of_birth = date_of_birth
        self.course_num = course_num
        self.group_name = group_name
        self.faculty_name = faculty_name
        self.study_form = study_form
        self.period_start = period_start
        self.period_end = period_end
        self.normative_duration = normative_duration
        self.to_the_authority = to_the_authority
        self.certificate_num = certificate_num
        self.executor_name = executor_name
        self.execution_date = execution_date
        self.qr_code_data = qr_code_data
        self.project_authority_name = project_authority_name
        self.project_authority_role = project_authority_role
        self.project_authority_sign_path = project_authority_sign_path
        self.ministry = ministry
        self.university_name = university_name
        self.seal_image_path = seal_image_path
        self.semesters = semesters


        self.doc = SimpleDocTemplate(self.file_path, pagesize=letter)

    def _draw_seal(self, canvas, doc, seal_image_path):
        seal_image = Image(seal_image_path, width=100, height=100)
        seal_image.drawOn(canvas, doc.width - 75, 125)

    def _generate_qr_code_image(self):
        '''Generate QR code image'''
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(self.qr_code_data)
        qr.make(fit=True)

        qr_code_img = qr.make_image(fill_color="black", back_color="white")

        qr_code_image_data = BytesIO()
        qr_code_img.save(qr_code_image_data)
        return Image(qr_code_image_data, width=100, height=100)

    def _add_image_paragraph(self, text, image_path, target_width=80):
        img = Image(image_path, width=target_width, height=target_width)
        aspect_ratio = img.imageWidth / img.imageHeight

        adjusted_height = target_width / aspect_ratio

        image_text = f"<font size=10 color=black>{text} <img src='{image_path}' width='{target_width}' height='{adjusted_height}'/></font>"
        return add_paragraph(image_text)

    def _add_title(self):
        title_text = f"<font size=12 color=black>{self.ministry}<br/>" \
                     f"{self.university_name}<br/>{self.faculty_name}</font>"
        return add_paragraph(title_text)

    def _add_reference(self):
        reference_text = f"<font size=12 color=black>СПРАВКА<br/><br/>" \
                          f"Дана студенту {self.student_name}. {self.date_of_birth} года рождения, в том, что он(а) действительно является студентом {self.course_num}-курса, группы {self.group_name}," \
                          f" {self.faculty_name} ({self.study_form})</font>"
        return add_paragraph(reference_text)

    def _add_study_period(self):
        declination = "года" if self.normative_duration > 1 and self.normative_duration < 5 else "год" if self.normative_duration == 1 else "лет"
        study_period_text = f"<font size=12 color=black>Форма обучения: {self.study_form}<br/>" \
                            f"Период обучения: с {self.period_start} по {self.period_end}<br/>" \
                            f"Нормативный срок освоения: {self.normative_duration} {declination} </font>"
        return add_paragraph(study_period_text)

    def _add_to_the_authority(self):
        to_the_authority_text = f"<font size=12 color=black>Справка выдана в {self.to_the_authority}</font>"
        return add_paragraph(to_the_authority_text)

    def _add_current_year_periods(self):
        periods_text = "<font size=12 color=black>Сроки обучения в текущем учебном году:</font>"
        for period in self.semesters:
            periods_text += f"<br/>- {period['name']} с {period['start']} по {period['end']}"
        return add_paragraph(periods_text)

    def _add_unique_number(self):
        unique_number_text = f"<font size=12 color=black>Уникальный номер документа: {self.certificate_num}</font>"
        return add_paragraph(unique_number_text)

    def _add_executor_and_date(self):
        executor_and_date = f"<font size=12>Исполнитель: {self.executor_name}, {self.execution_date}</font>"
        return add_paragraph(executor_and_date)

    def _add_signatures(self):
        project_authority_signature = self._add_image_paragraph(f"{self.project_authority_role}, {self.project_authority_name}:", self.project_authority_sign_path)

        return [add_spacer(), project_authority_signature]

    def generate_certificate(self) -> None:
        content = [self._add_title(), add_spacer(), self._add_reference(), add_spacer(),
                   self._add_study_period(), add_spacer(), self._add_to_the_authority(), add_spacer(),
                   self._add_current_year_periods(), add_spacer(), self._add_unique_number(), add_spacer(), self._add_executor_and_date(), add_spacer(),
                   self._generate_qr_code_image(), add_spacer(), add_spacer(), *self._add_signatures()]

        self.doc.build(content, onFirstPage=lambda canvas, doc: self._draw_seal(canvas, doc, self.seal_image_path))

if __name__ == "__main__":
#--------------------------------------------------------------------

    # Certificate1 | Example usage
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

#--------------------------------------------------------------------

    # Certificate2 | Example usage
    semesters_data = [
        {"name": "осенний семестр", "start": "01.09.2022", "end": "31.12.2022"},
        {"name": "весенний семестр", "start": "01.02.2023", "end": "31.05.2023"},
        {"name": "каникулярный семестр", "start": "01.06.2023", "end": "31.08.2023"}
    ]

    generator2 = CertificateGenerator2(
        file_path="certificate2.pdf",
        student_name="Имя Фамилия Отчество",
        date_of_birth="15.02.2004",
        course_num=3,
        group_name="Группа",
        faculty_name="Название факультета",
        study_form="очная",
        period_start=2021,
        period_end=2025,
        normative_duration=4,
        to_the_authority="посольство Германии",
        certificate_num="10-23-17-204", # Unique number for every certificate
        executor_name="ФИО исполнителя",
        execution_date="14.11.2023", # NOTE: Not sure whether it's execution date, keeping it as is for now.

        qr_code_data="something",
        # TODO: QR code should show some information automatically
        # without having to enter it as a parameter, replace it later
        # when info is gathered from the university.

        project_authority_name="ФИО",
        project_authority_role="Проектор по УР",
        project_authority_sign_path=os.path.join("test_images", "signature1.png"),
        ministry="МИНИСТЕРСТВО ОБРАЗОВАНИЯ И НАУКИ СТРАНЫ",
        university_name="Университет Silk Road Innovations",
        seal_image_path=os.path.join("test_images", "seal.jpg"),
        semesters=semesters_data
    )
    generator2.generate_certificate()

#--------------------------------------------------------------------