import yaml
import logging
import os
from fpdf import FPDF
from collections import defaultdict

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
    try:
        pdf_generator = PdfGenerator(font_path=r"data\ArialUni.ttf")
        return pdf_generator.generate_pdf(template_data, user_data, output_filename)
    except Exception as e:
        logging.error(f"Ошибка при генерации PDF: {e}", exc_info=True)
        return False

class PdfGenerator:
    def __init__(self, font_path):
        self.font_path = font_path
        self.font_name = "ArialUni"

    def generate_pdf(self, template_data, user_data, output_filename):
        if not isinstance(template_data, dict) or 'sections' not in template_data:
            logging.error("Некорректный формат шаблона.")
            return False
        
        user_data = defaultdict(str, user_data)  # Предотвращаем KeyError при форматировании
        pdf = FPDF()
        pdf.add_page()
        
        if os.path.exists(self.font_path):
            try:
                pdf.add_font(self.font_name, '', self.font_path, uni=True)
                pdf.add_font(self.font_name, 'B', self.font_path, uni=True)
                pdf.add_font(self.font_name, 'I', self.font_path, uni=True)
                logging.info("Шрифт Arial успешно добавлен.")
            except Exception as e:
                logging.error(f"Ошибка при добавлении шрифта: {e}", exc_info=True)
                return False
        else:
            logging.warning(f"Шрифт {self.font_path} не найден, используется стандартный Arial.")
            self.font_name = "Arial"

        section_number = 1
        
        for section in template_data['sections']:
            if not isinstance(section, dict):
                continue
            try:
                if 'title' in section:
                    title = f"{section_number}. {section['title']}"
                    pdf.set_font(self.font_name, 'B', section.get('title_font_size', 14))
                    pdf.cell(0, 10, txt=title, ln=True, align='C')
                    pdf.ln(5)
                    section_number += 1
                
                if 'text' in section:
                    font_size = section.get('font_size', 12)
                    font_style = section.get('font_style', '')
                    align = section.get('align', 'L')
                    
                    valid_styles = ['', 'B', 'I', 'U', 'BI']
                    font_style = font_style if font_style in valid_styles else ''
                    
                    pdf.set_font(self.font_name, font_style, font_size)
                    text = section['text'].format_map(user_data)
                    pdf.multi_cell(0, 10, txt=text, align=align)
                    pdf.ln(10)
            except Exception as e:
                logging.error(f"Ошибка при обработке секции: {e}", exc_info=True)
                return False
        
        output_dir = os.path.dirname(output_filename)
        if output_dir and not os.path.exists(output_dir):
            try:
                os.makedirs(output_dir, exist_ok=True)
                logging.info(f"Директория {output_dir} создана.")
            except Exception as e:
                logging.error(f"Ошибка при создании директории: {e}", exc_info=True)
                return False
        
        if not os.access(output_dir, os.W_OK):
            logging.error(f"Нет прав на запись в директорию {output_dir}")
            return False
        
        try:
            pdf.output(output_filename)
            logging.info(f"Файл {output_filename} успешно сохранен.")
            return True
        except Exception as e:
            logging.error(f"Ошибка при сохранении файла: {e}", exc_info=True)
            return False