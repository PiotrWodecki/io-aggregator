# place for every validators


def validate_file_extension(value):
    import os
    from django.core.exceptions import ValidationError

    ext = os.path.splitext(value.name)[1]  # [0] returns path+filename
    valid_extensions = [".txt", ".csv"]
    if not ext.lower() in valid_extensions:
        raise ValidationError("Unsupported file extension.")


def validate_multi_search_files_row(row):
    try:
        if len(str(row[0])) > 32:
            # name of product can not be longer than 32
            return False
        if not row[1] in ["1", "2", "3"]:
            # there are three types of shopping (All, only allegro, without allegro)
            return False
        if not row[2] in ["Zdrowie", "Uroda"]:
            # there are two types of category
            return False
        if not int(row[3]) > 0:
            # quantity can not be less than 1
            return False
        return True
    except (Exception,):
        return False
