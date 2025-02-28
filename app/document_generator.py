import yaml
import logging
import fpdf

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

def generate_pdf(template_text, user_data, output_filename):
    """Генерация PDF-файла на основе шаблона и пользовательских данных."""
    pdf = fpdf.FPDF()
    pdf.add_page()
    pdf.add_font('DejaVu', '', r'data\DejaVuSansCondensed.ttf', uni=True)
    pdf.set_font('DejaVu', '', 11)
    
    filled_template = template_text.format(**user_data)
    
    for line in filled_template.split('\n'):
        pdf.cell(200, 10, txt=line, ln=True, align='L')
    
    pdf.output(output_filename)