import yaml
import logging
from fpdf import FPDF
import os

def load_templates(yaml_file_path):
    try:
        with open(yaml_file_path, 'r', encoding='utf-8') as file:
            return yaml.safe_load(file)
    except FileNotFoundError:
        logging.error("Файл шаблонов не найден.")
        return []
    except yaml.YAMLError as e:
        logging.error(f"Ошибка при чтении YAML файла: {e}")
        return []

def generate_pdf_from_template(template_data, user_data, output_filename):
    """Генерация PDF-файла на основе шаблона и пользовательских данных."""
    try:
        pdf_generator = PdfGenerator(font_path=r"data\ArialUni.ttf")
        return pdf_generator.generate_pdf(template_data, user_data, output_filename)
    except Exception as e:
        logging.error(f"Ошибка при генерации PDF с использованием шаблона: {e}", exc_info=True)
        return False

class PdfGenerator:
    def __init__(self, font_path):
        self.font_path = font_path

    def generate_pdf(self, template_data, user_data, output_filename):
        try:
            pdf = FPDF()
            pdf.add_page()

            try:
                pdf.add_font('ArialUni', '', self.font_path, uni=True)
                pdf.add_font('ArialUni', 'B', self.font_path, uni=True)
                pdf.add_font('ArialUni', 'I', self.font_path, uni=True)
                pdf.set_font('ArialUni', '', 12)
                logging.info("Шрифт Arial успешно добавлен.")
            except Exception as e:
                logging.error(f"Ошибка при добавлении шрифта: {e}", exc_info=True)
                return False

            section_number = 1

            for section in template_data['sections']:
                try:
                    if isinstance(section, dict):
                        # Обработка заголовка
                        if 'title' in section:
                            title = f"{section_number}. {section['title']}"
                            pdf.set_font('ArialUni', 'B', section.get('title_font_size', 14))
                            pdf.cell(0, 10, txt=title, ln=True, align='C')

                            section_number += 1

                        if 'text' in section:
                            font_size = section.get('font_size', 12)
                            font_style = section.get('font_style', '')
                            align = section.get('align', 'L')

                            valid_styles = ['', 'B', 'I']
                            if font_style not in valid_styles:
                                font_style = ''
                            
                            pdf.set_font('ArialUni', font_style, font_size)
                            text = section['text'].format(**user_data)
                            pdf.multi_cell(0, 10, txt=text, align=align)
                            pdf.ln(10)

                except Exception as e:
                    logging.error(f"Ошибка при обработке секции: {e}", exc_info=True)
                    return False

            output_dir = os.path.dirname(output_filename)
            if output_dir and not os.path.exists(output_dir):
                try:
                    os.makedirs(output_dir)
                    logging.info(f"Директория {output_dir} успешно создана.")
                except Exception as e:
                    logging.error(f"Ошибка при создании директории: {e}", exc_info=True)
                    return False

            try:
                pdf.output(output_filename)
                logging.info(f"Файл {output_filename} успешно сохранен.")
            except Exception as e:
                logging.error(f"Ошибка при сохранении файла: {e}", exc_info=True)
                return False

            return True

        except Exception as e:
            logging.error(f"Общая ошибка при генерации PDF: {e}", exc_info=True)
            return False
