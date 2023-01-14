import os
from django.core.exceptions import ValidationError


def validate_file_extension(value):
    ext = os.path.splitext(value.name)[1]  # [0] returns path+filename
    valid_extensions = [".txt", ".csv"]
    if ext.lower() not in valid_extensions:
        raise ValidationError("Unsupported file extension.")


def validate_multi_search_files_row(row):
    try:
        if len(str(row[0])) > 32:
            # name of product can not be longer than 32
            return False
        if row[1] not in ["1", "2", "3"]:
            # there are three types of shopping (All, only allegro, without allegro)
            return False
        if row[2] not in ["Zdrowie", "Uroda"]:
            # there are two types of category
            return False
        if 10 <= int(row[3]) or int(row[3]) <= 0:
            # quantity can not be less than 1
            return False
        return True
    except (Exception,):
        return False
