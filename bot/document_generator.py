import yaml
import logging

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
