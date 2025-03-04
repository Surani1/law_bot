import yaml
import logging
import os
from fpdf import FPDF
from collections import defaultdict
from app.config import ARIAL_UNICODE, ARIAL_UNICODE_BOLD, ARIAL_UNICODE_BOLD_ITALIC, ARIAL_UNICODE_ITALIC

def load_templates(yaml_file_path):
    try:
        with open(yaml_file_path, 'r', encoding='utf-8') as file:
            return yaml.safe_load(file)
    except FileNotFoundError:
        logging.error("Файл шаблонов не найден.")
    except yaml.YAMLError as e:
        logging.error(f"Ошибка при чтении YAML файла: {e}")
    return None

def generate_pdf_from_template(template_data, user_data, output_filename):
    try:
        pdf_generator = PdfGenerator(
            font_regular= ARIAL_UNICODE,
            font_bold= ARIAL_UNICODE_BOLD,
            font_italic=ARIAL_UNICODE_ITALIC,
            font_bold_italic=ARIAL_UNICODE_BOLD_ITALIC
        )
        return pdf_generator.generate_pdf(template_data, user_data, output_filename)
    except Exception as e:
        logging.error(f"Ошибка при генерации PDF: {e}", exc_info=True)
        return False

class PdfGenerator:
    def __init__(self, font_regular, font_bold, font_italic, font_bold_italic):
        self.fonts = {
            "Regular": font_regular,
            "Bold": font_bold,
            "Italic": font_italic,
            "BoldItalic": font_bold_italic
        }
        self.font_alias = {"": "Regular", "B": "Bold", "I": "Italic", "BI": "BoldItalic"}

    def add_fonts(self, pdf):
        """Добавление всех шрифтов в PDF"""
        for style, path in self.fonts.items():
            if os.path.exists(path):
                try:
                    pdf.add_font(f"ArialUni-{style}", '', path, uni=True)
                except Exception as e:
                    logging.error(f"Ошибка при загрузке шрифта {style}: {e}", exc_info=True)
                    return False
            else:
                logging.error(f"Шрифт {path} не найден. Остановка генерации PDF.")
                return False
        return True

    def set_text_style(self, pdf, style=""):
        """Выбор правильного шрифта в зависимости от стиля"""
        font_name = f"ArialUni-{self.font_alias.get(style, 'Regular')}"
        pdf.set_font(font_name, '', 11)

    def add_two_column_text(self, pdf, left_text, right_text, width_ratio=0.45):
        """Выводит два текста в одной строке: один слева, другой справа."""
        page_width = pdf.w - 2 * pdf.l_margin
        col_width = page_width * width_ratio
        max_height = 6  # Базовая высота строки

        # Определяем высоту каждого блока текста
        left_height = pdf.get_string_width(left_text) / col_width * max_height
        right_height = pdf.get_string_width(right_text) / col_width * max_height
        cell_height = max(left_height, right_height, max_height)

        self.set_text_style(pdf, '')
        y_position = pdf.get_y()
        pdf.set_x(pdf.l_margin)
        pdf.multi_cell(col_width, cell_height, left_text, border=0, align='L')
        pdf.set_xy(pdf.l_margin + page_width - col_width, y_position)
        pdf.multi_cell(col_width, cell_height, right_text, border=0, align='R')
        pdf.ln(cell_height)

    def generate_pdf(self, template_data, user_data, output_filename):
        if not isinstance(template_data, dict) or 'sections' not in template_data:
            logging.error("Некорректный формат шаблона.")
            return False
        
        user_data = defaultdict(str, user_data)
        pdf = FPDF()
        pdf.add_page()

        if not self.add_fonts(pdf):
            return False

        pdf.set_auto_page_break(auto=True, margin=15)
        section_number = 1

        for section in template_data['sections']:
            if not isinstance(section, dict):
                continue
            try:
                if 'title' in section:
                    self.set_text_style(pdf, 'B')
                    pdf.cell(0, 8, txt=f"{section_number}. {section['title']}", ln=True, align='C')
                    pdf.ln(3)
                    section_number += 1
                if 'text' in section:
                    self.set_text_style(pdf, section.get('font_style', ''))
                    text = section['text'].format_map(user_data)
                    if "{date}" in section['text'] and "{city}" in section['text']:
                        self.add_two_column_text(pdf, user_data.get("date", "____.__.__"), user_data.get("city", "Город"))
                    else:
                        pdf.multi_cell(0, 4.5, txt=text, align='L')
                        pdf.ln(3)
            except Exception as e:
                logging.error(f"Ошибка при обработке секции: {e}", exc_info=True)
                return False
        
        output_dir = os.path.dirname(output_filename)
        if output_dir and not os.path.exists(output_dir):
            try:
                os.makedirs(output_dir, exist_ok=True)
            except Exception as e:
                logging.error(f"Ошибка при создании директории: {e}", exc_info=True)
                return False
        
        try:
            with open(output_filename, 'wb') as f:
                pass  # Проверка возможности записи
        except Exception as e:
            logging.error(f"Нет прав на запись в файл {output_filename}: {e}")
            return False
        
        try:
            pdf.output(output_filename)
            logging.info(f"Файл {output_filename} успешно сохранен.")
            return True
        except Exception as e:
            logging.error(f"Ошибка при сохранении файла: {e}", exc_info=True)
            return False
