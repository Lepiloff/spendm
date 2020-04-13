import json
from openpyxl import load_workbook


class InvalidFormatException(Exception):
    pass


def check_exel_rfi_template_structure(structure):
    p_category_coordinate = ["COMMON S2P",
                            "COMMON SOURCING - SXM",
                            "SERVICES",
                            "SOURCING",
                            "SXM",
                            "Spend Analytics",
                            "CLM",
                            "eProcurement",
                            "I2P",
                          ]
    if structure == p_category_coordinate:
        return True
    else:
        return False

def parse_excel_rfi_sheet(file):
    workbook = load_workbook(filename=file)
    sheet = workbook["RFI"]
    curent_paren_category_coordinate = []
    try:
        curent_paren_category_coordinate.append(sheet['E4'].value)  # COMMON S2P
        curent_paren_category_coordinate.append(sheet['E222'].value)  # COMMON SOURCING - SXM
        curent_paren_category_coordinate.append(sheet['E348'].value)  # SERVICES
        curent_paren_category_coordinate.append(sheet['E381'].value)  # SOURCING
        curent_paren_category_coordinate.append(sheet['E519'].value)  # SXM
        curent_paren_category_coordinate.append(sheet['E568'].value)  # Spend Analytics
        curent_paren_category_coordinate.append(sheet['E617'].value)  # CLM
        curent_paren_category_coordinate.append(sheet['E688'].value)  # eProcurement
        curent_paren_category_coordinate.append(sheet['E950'].value)  # I2P
        if check_exel_rfi_template_structure(structure=curent_paren_category_coordinate):
            file_status = True
        else:
            file_status = False
    except:
        raise InvalidFormatException("Error during excel file parsing. Unknown module cell")
    if file_status:
        for row in sheet.rows:
            for cell in row:
                if cell.value == "COMMON S2P":
                    sheet['E7'] = 4
                    workbook.save("sample.xlsx")
                    print('Yep found in {}'.format(cell.coordinate))
    return json.dumps(curent_paren_category_coordinate)

