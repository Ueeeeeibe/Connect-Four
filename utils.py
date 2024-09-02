def get_key_from_value(source_dict: dict, target_value):
    return [key for key, value in source_dict.items() if value == target_value][0]