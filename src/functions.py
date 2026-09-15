import yaml

def read_yaml_config(config_path: str) -> dict:
    '''
    Хелпер функция для безопасного чтения yaml-конфига.

    Args:
        config_path (str): Путь до конфига с расширением .yaml
    
    Returns:
        dict: Конфиг в формате словаря.
    '''

    with open(config_path, 'r', encoding = 'utf-8') as data:

        result = yaml.safe_load(data)

        return result