import json
from openpyxl import load_workbook
from apps.vendors.models import RfiParticipation, Vendors, Rfis


header_cols_first_scoring_round = ["E", "F", "G", "P", "Q", "R", "S", "T"]

pc_to_modules_assign = {
                            "Strategic Sourcing": ['Common S2P', 'Common Sourcing - SXM', 'Services', 'Sourcing'],
                            "Supplier Management": ['Common S2P', 'Common Sourcing - SXM', 'Services', 'SXM'],
                            "Spend Analytics": ['Common S2P', 'Services', 'Spend Analytics'],
                            "Contract Management": ['Common S2P', 'Services', 'CLM'],
                            "e-Procurement": ['Common S2P', 'Services', 'eProcurement'],
                            "Invoice-to-Pay": ['Common S2P', 'Services', 'I2P'],
                            "AP Automation": ['Common S2P', 'Services', 'I2P', 'AP'],
                            "Strategic Procurement Technologies": ['Common S2P', 'Common Sourcing - SXM', 'Services',
                                                                   'Sourcing', 'SXM', 'Spend Analytics', 'CLM'],
                            "Procure-to-Pay": ['Common S2P', 'Services', 'eProcurement', 'I2P'],
                            "Source-to-Pay": ['Common S2P', 'Common Sourcing - SXM', 'Services',
                                              'Sourcing', 'SXM', 'Spend Analytics', 'CLM', 'eProcurement', 'I2P']
                             }


paren_category_row_number = {
                            "COMMON S2P": 4,
                            "COMMON SOURCING - SXM": 222,
                            "SERVICES": 348,
                            "SOURCING": 381,
                            "SXM": 519,
                            "Spend Analytics": 568,
                            "CLM": 617,
                            "eProcurement": 688,
                            "I2P": 950,
                             }

category_to_pc_row_number = {
                            "COMMON S2P": {"Analytics": 5, "Configurability": 45, "Supplier Portal": 91, "SXM": 111},

                            "COMMON SOURCING - SXM": {"Contingent Workforce / Services Procurement": 223,
                                                      "Relationship Management": 236, "Risk Management": 256,
                                                      "Supplier Information Management": 305, "Supplier Portal": 324},

                            "SERVICES": {"S2P Services": 349, "SPT Services": 371, "Sourcing - SXM Services": 375},

                            "SOURCING": {"Opportunity": 382, "RFX / Surveys": 410, "Optimization": 465,
                                         "Performance Management": 497, "CLM Support": 509},

                            "SXM": {"Extended SIM": 520, "SXM": 544},

                            "Spend Analytics": {"Process Support": 569, "Function Support": 590},

                            "CLM": {"Contract Information Management": 618, "Contract Process Management": 645,
                                    "Analytics": 676},

                            "eProcurement": {"Catalog Management": 689, "Requisitioning": 742, "Ordering": 864, "Receiving": 919},

                            "I2P": {"Invoicing": 951, "Payment & Financing": 1033,
                                    "OPTIONAL For Specialized Personas (Additional coverage in SolutionMap)": 1083}
                            }


class InvalidFormatException(Exception):
    # do not remove !
    pass


def get_excel_file_current_pc_for_parsing(pml=None):
    modules_with_pc = (dict((option, pc_to_modules_assign[option]) for option in pml if option in pc_to_modules_assign))
    pc = [value for key, value in modules_with_pc.items()]
    # Get unique pc depending on the active modules in the round for a particular vendor
    unique_pc = set(x for element in pc for x in element)
    return unique_pc


def get_full_excel_file_response(file, context):
    # Get data from url context
    rfiid = context.get('rfiid')
    vendor_id = context.get('vendor')
    vendor = Vendors.objects.get(vendorid=vendor_id)
    round = Rfis.objects.get(rfiid=rfiid)
    participate_module = RfiParticipation.objects.filter(vendor=vendor, rfi=round, active=True)  # Get vendor active module
    participate_module_list = [element.m.module_name for element in participate_module]
    unique_pc = get_excel_file_current_pc_for_parsing(pml=participate_module_list)  # Get unique PC for future processing
    """ return full response from excel file (exclude PC not partisipate to vendor in curent round)"""
    workbook = load_workbook(filename=file)
    response = []
    pc_participate_list = []
    for element in unique_pc:
        pc_participate_list.append(pc_to_function_name.get(element))
    for pc in pc_participate_list:
        if pc:
            response.append(pc(file, workbook))
    return response


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


def check_excel_rfi_sheet_structure(file):
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
    return file_status


def subcategory_element_response_create(min_row, max_row, sheet=None,to_category_info=None, sub_category = None):
    to_sub_category_info = []
    for row in sheet.iter_rows(min_row=min_row, max_row=max_row, values_only=False):
        element_info = {}
        for cell in row:
            if cell.column_letter in header_cols_first_scoring_round:
                element_info[sheet[str(cell.column_letter + '2')].value] = cell.value
        to_sub_category_info.append(element_info)
    to_category_info.append({sub_category: to_sub_category_info})


def common_s2p_category_response_create(file, workbook):
    """
    Create response from COMMON_S2P parsing
    :param file:
    :return:
    """

    sheet = workbook["RFI"]
    if check_excel_rfi_sheet_structure(file):  # Check that excel file structure equal to source template
        pc_response = {}  # crete response with all element information for each subcat for each category in PC
        pc_response.update({"Parent Category": sheet["E4"].value})
        category_list = []  # list of all category in PC with subcat info and element data

        # ANALYTICS CATEGORY

        category_name = sheet["E5"].value
        info_to_subcat_to_cat = {}
        to_category_info = []  # list of all subcat wit element info

        # Subcategory Data Schema
        sub_category = sheet["E6"].value
        subcategory_element_response_create(min_row=7, max_row=12, sheet=sheet, to_category_info=to_category_info,
                                            sub_category=sub_category)
        # Subcategory Data Management
        sub_category = sheet["E15"].value
        subcategory_element_response_create(min_row=16, max_row=20, sheet=sheet, to_category_info=to_category_info,
                                            sub_category=sub_category)
        # Subcategory Metric Management
        sub_category = sheet["E23"].value
        subcategory_element_response_create(min_row=24, max_row=28, sheet=sheet, to_category_info=to_category_info,
                                            sub_category=sub_category)

        # Subcategory Reporting
        sub_category = sheet["E31"].value
        subcategory_element_response_create(min_row=32, max_row=42, sheet=sheet, to_category_info=to_category_info,
                                            sub_category=sub_category)

        info_to_subcat_to_cat.update({category_name: to_category_info})  # Aggregate info for each Subcat at CAREGORY
        category_list.append(info_to_subcat_to_cat)

        # CONFIGURABILITY CATEGORY
        category_name = sheet["E45"].value
        info_to_subcat_to_cat = {}
        to_category_info = []

        # Subcategory Globalization
        sub_category = sheet["E46"].value
        subcategory_element_response_create(min_row=47, max_row=53, sheet=sheet, to_category_info=to_category_info,
                                            sub_category=sub_category)
        # Subcategory Organizational Modeling
        sub_category = sheet["E56"].value
        subcategory_element_response_create(min_row=57, max_row=62, sheet=sheet, to_category_info=to_category_info,
                                            sub_category=sub_category)

        # Subcategory Personalization
        sub_category = sheet["E65"].value
        subcategory_element_response_create(min_row=66, max_row=70, sheet=sheet, to_category_info=to_category_info,
                                            sub_category=sub_category)

        # Subcategory Project Management
        sub_category = sheet["E73"].value
        subcategory_element_response_create(min_row=74, max_row=78, sheet=sheet, to_category_info=to_category_info,
                                            sub_category=sub_category)
        # Subcategory Workflow
        sub_category = sheet["E81"].value
        subcategory_element_response_create(min_row=82, max_row=88, sheet=sheet, to_category_info=to_category_info,
                                            sub_category=sub_category)

        info_to_subcat_to_cat.update({category_name: to_category_info})  # Aggregate info for each Subcat at CAREGORY
        category_list.append(info_to_subcat_to_cat)

        # SUPPLIER PORTAL CATEGORY
        category_name = sheet["E91"].value
        info_to_subcat_to_cat = {}
        to_category_info = []

        # Subcategory Account Management
        sub_category = sheet["E92"].value
        subcategory_element_response_create(min_row=93, max_row=97, sheet=sheet, to_category_info=to_category_info,
                                            sub_category=sub_category)
        # Subcategory Document Management
        sub_category = sheet["E100"].value
        subcategory_element_response_create(min_row=101, max_row=102, sheet=sheet, to_category_info=to_category_info,
                                            sub_category=sub_category)
        # Subcategory Information Management
        sub_category = sheet["E105"].value
        subcategory_element_response_create(min_row=106, max_row=108, sheet=sheet, to_category_info=to_category_info,
                                            sub_category=sub_category)

        info_to_subcat_to_cat.update({category_name: to_category_info})  # Aggregate info for each Subcat at CAREGORY
        category_list.append(info_to_subcat_to_cat)

        # SXM CATEGORY
        category_name = sheet["E111"].value
        info_to_subcat_to_cat = {}
        to_category_info = []

        # Subcategory Supplier Information Management
        sub_category = sheet["E112"].value
        subcategory_element_response_create(min_row=113, max_row=119, sheet=sheet, to_category_info=to_category_info,
                                            sub_category=sub_category)
        # Subcategory Supply Intelligence
        sub_category = sheet["E122"].value
        subcategory_element_response_create(min_row=123, max_row=125, sheet=sheet, to_category_info=to_category_info,
                                            sub_category=sub_category)

        info_to_subcat_to_cat.update({category_name: to_category_info})  # Aggregate info for each Subcat at CAREGORY
        category_list.append(info_to_subcat_to_cat)

        # TECHNOLOGY CATEGORY
        category_name = sheet["E128"].value
        info_to_subcat_to_cat = {}
        to_category_info = []

        # Subcategory Automation
        sub_category = sheet["E129"].value
        subcategory_element_response_create(min_row=130, max_row=136, sheet=sheet, to_category_info=to_category_info,
                                            sub_category=sub_category)
        # Subcategory Core Platform
        sub_category = sheet["E139"].value
        subcategory_element_response_create(min_row=140, max_row=156, sheet=sheet, to_category_info=to_category_info,
                                            sub_category=sub_category)
        # Subcategory Data Management
        sub_category = sheet["E159"].value
        subcategory_element_response_create(min_row=160, max_row=174, sheet=sheet, to_category_info=to_category_info,
                                            sub_category=sub_category)
        # Subcategory Document Management
        sub_category = sheet["E177"].value
        subcategory_element_response_create(min_row=178, max_row=182, sheet=sheet, to_category_info=to_category_info,
                                            sub_category=sub_category)
        # Subcategory Emerging Technology
        sub_category = sheet["E185"].value
        subcategory_element_response_create(min_row=186, max_row=193, sheet=sheet, to_category_info=to_category_info,
                                            sub_category=sub_category)
        # Subcategory Standards and Integrations
        sub_category = sheet["E196"].value
        subcategory_element_response_create(min_row=197, max_row=209, sheet=sheet, to_category_info=to_category_info,
                                            sub_category=sub_category)
        # Subcategory UX Layer
        sub_category = sheet["E212"].value
        subcategory_element_response_create(min_row=213, max_row=219, sheet=sheet, to_category_info=to_category_info,
                                            sub_category=sub_category)

        info_to_subcat_to_cat.update({category_name: to_category_info})  # Aggregate info for each Subcat at CAREGORY
        category_list.append(info_to_subcat_to_cat)

        pc_response.update({"Category": category_list})
        return pc_response


def common_sourcing_sxm_response_create(file, workbook):
    """
    Create response from COMMON SOURCING SXM parsing
    :param file:
    :return:
    """
    sheet = workbook["RFI"]
    if check_excel_rfi_sheet_structure(file):  # Check that excel file structure equal to source template
        pc_response = {}  # crete response with all element information for each subcat for each category in PC
        pc_response.update({"Parent Category": sheet["E222"].value})
        category_list = []  # list of all category in PC with subcat info and element data

        # CONTINGENT WORKFORCE / SERVICES PROCUREMENT CATEGORY

        category_name = sheet["E223"].value
        info_to_subcat_to_cat = {}
        to_category_info = []  # list of all subcat wit element info

        # Subcategory Contingent Workforce Management
        sub_category = sheet["E224"].value
        subcategory_element_response_create(min_row=225, max_row=227, sheet=sheet, to_category_info=to_category_info,
                                            sub_category=sub_category)

        info_to_subcat_to_cat.update({category_name: to_category_info})  # Aggregate info for each Subcat at CAREGORY
        category_list.append(info_to_subcat_to_cat)

        # PERFOMANCE MANAGEMENT CATEGORY

        category_name = sheet["E230"].value
        info_to_subcat_to_cat = {}
        to_category_info = []  # list of all subcat wit element info

        # Subcategory Supplier Performance Management
        sub_category = sheet["E231"].value
        subcategory_element_response_create(min_row=232, max_row=233, sheet=sheet, to_category_info=to_category_info,
                                            sub_category=sub_category)

        info_to_subcat_to_cat.update({category_name: to_category_info})  # Aggregate info for each Subcat at CAREGORY
        category_list.append(info_to_subcat_to_cat)

        # RELATIONSHIP MANAGEMENT CATEGORY

        category_name = sheet["E236"].value
        info_to_subcat_to_cat = {}
        to_category_info = []  # list of all subcat wit element info

        # Subcategory Issue Management
        sub_category = sheet["E237"].value
        subcategory_element_response_create(min_row=238, max_row=242, sheet=sheet, to_category_info=to_category_info,
                                            sub_category=sub_category)

        # Subcategory Plan Management
        sub_category = sheet["E245"].value
        subcategory_element_response_create(min_row=246, max_row=253, sheet=sheet, to_category_info=to_category_info,
                                            sub_category=sub_category)

        info_to_subcat_to_cat.update({category_name: to_category_info})  # Aggregate info for each Subcat at CAREGORY
        category_list.append(info_to_subcat_to_cat)

        # RISK MANAGEMENT CATEGORY

        category_name = sheet["E256"].value
        info_to_subcat_to_cat = {}
        to_category_info = []  # list of all subcat wit element info

        # Subcategory Assessment
        sub_category = sheet["E257"].value
        subcategory_element_response_create(min_row=258, max_row=260, sheet=sheet, to_category_info=to_category_info,
                                            sub_category=sub_category)

        # Subcategory Mitigation Planning
        sub_category = sheet["E263"].value
        subcategory_element_response_create(min_row=264, max_row=267, sheet=sheet, to_category_info=to_category_info,
                                            sub_category=sub_category)

        # Subcategory Model Definition
        sub_category = sheet["E270"].value
        subcategory_element_response_create(min_row=271, max_row=274, sheet=sheet, to_category_info=to_category_info,
                                            sub_category=sub_category)
        # Subcategory Monitoring & Identification
        sub_category = sheet["E277"].value
        subcategory_element_response_create(min_row=278, max_row=287, sheet=sheet, to_category_info=to_category_info,
                                            sub_category=sub_category)
        # Subcategory Regulatory Compliance
        sub_category = sheet["E290"].value
        subcategory_element_response_create(min_row=291, max_row=298, sheet=sheet, to_category_info=to_category_info,
                                            sub_category=sub_category)
        # Subcategory Supplier Risk Management
        sub_category = sheet["E301"].value
        subcategory_element_response_create(min_row=302, max_row=302, sheet=sheet, to_category_info=to_category_info,
                                            sub_category=sub_category)

        info_to_subcat_to_cat.update({category_name: to_category_info})  # Aggregate info for each Subcat at CAREGORY
        category_list.append(info_to_subcat_to_cat)

        # SUPPLIER INFORMATION MANAGEMENT CATEGORY

        category_name = sheet["E305"].value
        info_to_subcat_to_cat = {}
        to_category_info = []  # list of all subcat wit element info

        # Subcategory Discovery
        sub_category = sheet["E306"].value
        subcategory_element_response_create(min_row=307, max_row=311, sheet=sheet, to_category_info=to_category_info,
                                            sub_category=sub_category)
        # Subcategory Onboarding Support
        sub_category = sheet["E314"].value
        subcategory_element_response_create(min_row=315, max_row=316, sheet=sheet, to_category_info=to_category_info,
                                            sub_category=sub_category)
        # Subcategory Supply Base Profiling
        sub_category = sheet["E319"].value
        subcategory_element_response_create(min_row=320, max_row=321, sheet=sheet, to_category_info=to_category_info,
                                            sub_category=sub_category)

        info_to_subcat_to_cat.update({category_name: to_category_info})  # Aggregate info for each Subcat at CAREGORY
        category_list.append(info_to_subcat_to_cat)

        # SUPPLIER PORTAL CATEGORY

        category_name = sheet["E324"].value
        info_to_subcat_to_cat = {}
        to_category_info = []  # list of all subcat wit element info

        # Subcategory Collaboration
        sub_category = sheet["E325"].value
        subcategory_element_response_create(min_row=326, max_row=326, sheet=sheet, to_category_info=to_category_info,
                                            sub_category=sub_category)
        # Subcategory Information Management
        sub_category = sheet["E329"].value
        subcategory_element_response_create(min_row=330, max_row=331, sheet=sheet, to_category_info=to_category_info,
                                            sub_category=sub_category)
        # Subcategory Performance Management
        sub_category = sheet["E334"].value
        subcategory_element_response_create(min_row=335, max_row=335, sheet=sheet, to_category_info=to_category_info,
                                            sub_category=sub_category)
        # Subcategory Relationship Management
        sub_category = sheet["E338"].value
        subcategory_element_response_create(min_row=339, max_row=341, sheet=sheet, to_category_info=to_category_info,
                                            sub_category=sub_category)
        # Subcategory Supplier Portal
        sub_category = sheet["E344"].value
        subcategory_element_response_create(min_row=345, max_row=345, sheet=sheet, to_category_info=to_category_info,
                                            sub_category=sub_category)

        info_to_subcat_to_cat.update({category_name: to_category_info})  # Aggregate info for each Subcat at CAREGORY
        category_list.append(info_to_subcat_to_cat)

        pc_response.update({"Category": category_list})
        return pc_response


def services_response_create(file, workbook):
    """
    Create response from SERVICES parsing
    :param file:
    :return:
    """
    sheet = workbook["RFI"]
    if check_excel_rfi_sheet_structure(file):  # Check that excel file structure equal to source template
        pc_response = {}  # crete response with all element information for each subcat for each category in PC
        pc_response.update({"Parent Category": sheet["E348"].value})
        category_list = []  # list of all category in PC with subcat info and element data

        # S2P SERVICES CATEGORY

        category_name = sheet["E349"].value
        info_to_subcat_to_cat = {}
        to_category_info = []  # list of all subcat wit element info

        # Subcategory General
        sub_category = "General"
        subcategory_element_response_create(min_row=350, max_row=368, sheet=sheet, to_category_info=to_category_info,
                                            sub_category=sub_category)

        # SPT SERVICES CATEGORY

        category_name = sheet["E371"].value
        info_to_subcat_to_cat = {}
        to_category_info = []  # list of all subcat wit element info

        # Subcategory General
        sub_category = "General"
        subcategory_element_response_create(min_row=372, max_row=372, sheet=sheet, to_category_info=to_category_info,
                                            sub_category=sub_category)

        info_to_subcat_to_cat.update({category_name: to_category_info})  # Aggregate info for each Subcat at CAREGORY
        category_list.append(info_to_subcat_to_cat)

        # SOURCING - SXM SERVICES CATEGORY

        category_name = sheet["E375"].value
        info_to_subcat_to_cat = {}
        to_category_info = []  # list of all subcat wit element info

        # Subcategory General
        sub_category = "General"
        subcategory_element_response_create(min_row=376, max_row=378, sheet=sheet, to_category_info=to_category_info,
                                            sub_category=sub_category)

        info_to_subcat_to_cat.update({category_name: to_category_info})  # Aggregate info for each Subcat at CAREGORY
        category_list.append(info_to_subcat_to_cat)

        pc_response.update({"Category": category_list})
        return pc_response


def sourcing_response_create(file, workbook):
    """
    Create response from SOURCING parsing
    :param file:
    :return:
    """
    sheet = workbook["RFI"]
    if check_excel_rfi_sheet_structure(file):  # Check that excel file structure equal to source template
        pc_response = {}  # crete response with all element information for each subcat for each category in PC
        pc_response.update({"Parent Category": sheet["E381"].value})
        category_list = []  # list of all category in PC with subcat info and element data

        # OPPORTUNITY CATEGORY

        category_name = sheet["E382"].value
        info_to_subcat_to_cat = {}
        to_category_info = []  # list of all subcat wit element info

        # Subcategory Category Analysis
        sub_category = sheet["E383"].value
        subcategory_element_response_create(min_row=384, max_row=397, sheet=sheet, to_category_info=to_category_info,
                                            sub_category=sub_category)
        # Subcategory Should-Cost Modelling
        sub_category = sheet["E400"].value
        subcategory_element_response_create(min_row=401, max_row=407, sheet=sheet, to_category_info=to_category_info,
                                            sub_category=sub_category)

        info_to_subcat_to_cat.update({category_name: to_category_info})  # Aggregate info for each Subcat at CAREGORY
        category_list.append(info_to_subcat_to_cat)

        # RFX / SURVEYS CATEGORY

        category_name = sheet["E410"].value
        info_to_subcat_to_cat = {}
        to_category_info = []  # list of all subcat with element info

        # Subcategory Construction
        sub_category = sheet["E411"].value
        subcategory_element_response_create(min_row=412, max_row=432, sheet=sheet, to_category_info=to_category_info,
                                            sub_category=sub_category)
        # Subcategory Evaluation mechanisms
        sub_category = sheet["E435"].value
        subcategory_element_response_create(min_row=436, max_row=439, sheet=sheet, to_category_info=to_category_info,
                                            sub_category=sub_category)
        # Subcategory RFX Management Capabilities
        sub_category = sheet["E442"].value
        subcategory_element_response_create(min_row=443, max_row=448, sheet=sheet, to_category_info=to_category_info,
                                            sub_category=sub_category)
        # Subcategory Auction
        sub_category = sheet["E451"].value
        subcategory_element_response_create(min_row=452, max_row=462, sheet=sheet, to_category_info=to_category_info,
                                            sub_category=sub_category)

        info_to_subcat_to_cat.update({category_name: to_category_info})  # Aggregate info for each Subcat at CAREGORY
        category_list.append(info_to_subcat_to_cat)

        # OPTIMIZATION CATEGORY

        category_name = sheet["E465"].value
        info_to_subcat_to_cat = {}
        to_category_info = []  # list of all subcat with element info

        # Subcategory Foundations
        sub_category = sheet["E466"].value
        subcategory_element_response_create(min_row=467, max_row=475, sheet=sheet, to_category_info=to_category_info,
                                            sub_category=sub_category)
        # Subcategory Sophisticated Constraint Analysis
        sub_category = sheet["E478"].value
        subcategory_element_response_create(min_row=479, max_row=486, sheet=sheet, to_category_info=to_category_info,
                                            sub_category=sub_category)
        # Subcategory Freight Analytics
        sub_category = sheet["E489"].value
        subcategory_element_response_create(min_row=490, max_row=494, sheet=sheet, to_category_info=to_category_info,
                                            sub_category=sub_category)

        info_to_subcat_to_cat.update({category_name: to_category_info})  # Aggregate info for each Subcat at CAREGORY
        category_list.append(info_to_subcat_to_cat)

        # PERFOMANCE MANAGEMENT CATEGORY

        category_name = sheet["E497"].value
        info_to_subcat_to_cat = {}
        to_category_info = []  # list of all subcat with element info

        # Subcategory Core Capabilities
        sub_category = sheet["E498"].value
        subcategory_element_response_create(min_row=499, max_row=506, sheet=sheet, to_category_info=to_category_info,
                                            sub_category=sub_category)

        info_to_subcat_to_cat.update({category_name: to_category_info})  # Aggregate info for each Subcat at CAREGORY
        category_list.append(info_to_subcat_to_cat)

        # CLM SUPPORT CATEGORY

        category_name = sheet["E509"].value
        info_to_subcat_to_cat = {}
        to_category_info = []  # list of all subcat with element info

        # Subcategory Core Capabilities
        sub_category = sheet["E510"].value
        subcategory_element_response_create(min_row=511, max_row=516, sheet=sheet, to_category_info=to_category_info,
                                            sub_category=sub_category)

        info_to_subcat_to_cat.update({category_name: to_category_info})  # Aggregate info for each Subcat at CAREGORY
        category_list.append(info_to_subcat_to_cat)

        pc_response.update({"Category": category_list})
        return pc_response


def sxm_response_create(file, workbook):
    """
    Create response from SXM parsing
    :param file:
    :return:
    """
    sheet = workbook["RFI"]
    if check_excel_rfi_sheet_structure(file):  # Check that excel file structure equal to source template
        pc_response = {}  # crete response with all element information for each subcat for each category in PC
        pc_response.update({"Parent Category": sheet["E519"].value})
        category_list = []  # list of all category in PC with subcat info and element data

        # EXTENDED SIM CATEGORY

        category_name = sheet["E520"].value
        info_to_subcat_to_cat = {}
        to_category_info = []  # list of all subcat wit element info

        # Subcategory General
        sub_category = "General"
        subcategory_element_response_create(min_row=521, max_row=541, sheet=sheet, to_category_info=to_category_info,
                                            sub_category=sub_category)

        info_to_subcat_to_cat.update({category_name: to_category_info})  # Aggregate info for each Subcat at CATEGORY
        category_list.append(info_to_subcat_to_cat)

        # SXM CATEGORY

        category_name = sheet["E544"].value
        info_to_subcat_to_cat = {}
        to_category_info = []  # list of all subcat wit element info

        # Subcategory Development & Innovation Management
        sub_category = sheet["E545"].value
        subcategory_element_response_create(min_row=546, max_row=550, sheet=sheet, to_category_info=to_category_info,
                                            sub_category=sub_category)
        # Subcategory NPD / NPI
        sub_category = sheet["E553"].value
        subcategory_element_response_create(min_row=554, max_row=558, sheet=sheet, to_category_info=to_category_info,
                                            sub_category=sub_category)
        # Subcategory Out-of-the-Box Reporting
        sub_category = sheet["E561"].value
        subcategory_element_response_create(min_row=562, max_row=565, sheet=sheet, to_category_info=to_category_info,
                                            sub_category=sub_category)

        info_to_subcat_to_cat.update({category_name: to_category_info})  # Aggregate info for each Subcat at CATEGORY
        category_list.append(info_to_subcat_to_cat)

        pc_response.update({"Category": category_list})
        return pc_response


def spend_analytics_response_create(file, workbook):
    """
    Create response from Spend Analytics parsing
    :param file:
    :return:
    """
    sheet = workbook["RFI"]
    if check_excel_rfi_sheet_structure(file):  # Check that excel file structure equal to source template
        pc_response = {}  # crete response with all element information for each subcat for each category in PC
        pc_response.update({"Parent Category": sheet["E568"].value})
        category_list = []  # list of all category in PC with subcat info and element data

        # PROCESS SUPPORT CATEGORY

        category_name = sheet["E569"].value
        info_to_subcat_to_cat = {}
        to_category_info = []  # list of all subcat wit element info

        # Subcategory General
        sub_category = "General"
        subcategory_element_response_create(min_row=570, max_row=587, sheet=sheet, to_category_info=to_category_info,
                                            sub_category=sub_category)

        info_to_subcat_to_cat.update({category_name: to_category_info})  # Aggregate info for each Subcat at CATEGORY
        category_list.append(info_to_subcat_to_cat)

        # FUNCTION SUPPORT CATEGORY

        category_name = sheet["E590"].value
        info_to_subcat_to_cat = {}
        to_category_info = []  # list of all subcat wit element info

        # Subcategory Raw Capability
        sub_category = sheet["E591"].value
        subcategory_element_response_create(min_row=593, max_row=600, sheet=sheet, to_category_info=to_category_info,
                                            sub_category=sub_category)

        # Subcategory Out of the Box
        sub_category = sheet["E603"].value
        subcategory_element_response_create(min_row=604, max_row=614, sheet=sheet, to_category_info=to_category_info,
                                            sub_category=sub_category)

        info_to_subcat_to_cat.update({category_name: to_category_info})  # Aggregate info for each Subcat at CATEGORY
        category_list.append(info_to_subcat_to_cat)

        pc_response.update({"Category": category_list})
        return pc_response


def clm_response_create(file, workbook):
    """
    Create response from CLM parsing
    :param file:
    :return:
    """
    sheet = workbook["RFI"]
    if check_excel_rfi_sheet_structure(file):  # Check that excel file structure equal to source template
        pc_response = {}  # crete response with all element information for each subcat for each category in PC
        pc_response.update({"Parent Category": sheet["E568"].value})
        category_list = []  # list of all category in PC with subcat info and element data

        # CONTACT INFORMATION MANAGEMENT CATEGORY

        category_name = sheet["E618"].value
        info_to_subcat_to_cat = {}
        to_category_info = []  # list of all subcat wit element info

        # Subcategory Core Contract modeling
        sub_category = sheet["E619"].value
        subcategory_element_response_create(min_row=620, max_row=630, sheet=sheet, to_category_info=to_category_info,
                                            sub_category=sub_category)

        # Subcategory Extended Contract Modeling and Analytics
        sub_category = sheet["E633"].value
        subcategory_element_response_create(min_row=634, max_row=642, sheet=sheet, to_category_info=to_category_info,
                                            sub_category=sub_category)

        info_to_subcat_to_cat.update({category_name: to_category_info})  # Aggregate info for each Subcat at CAREGORY
        category_list.append(info_to_subcat_to_cat)

        # CONTACT PROCESS MANAGEMENT CATEGORY

        category_name = sheet["E645"].value
        info_to_subcat_to_cat = {}
        to_category_info = []  # list of all subcat wit element info

        # Subcategory Contract Expiry & Renewal Management
        sub_category = sheet["E646"].value
        subcategory_element_response_create(min_row=647, max_row=649, sheet=sheet, to_category_info=to_category_info,
                                            sub_category=sub_category)

        # Subcategory Contract Creation and Authoring
        sub_category = sheet["E652"].value
        subcategory_element_response_create(min_row=653, max_row=659, sheet=sheet, to_category_info=to_category_info,
                                            sub_category=sub_category)

        # Subcategory Contract Collaboration
        sub_category = sheet["E662"].value
        subcategory_element_response_create(min_row=663, max_row=667, sheet=sheet, to_category_info=to_category_info,
                                            sub_category=sub_category)

        # Subcategory Contract Performance Management
        sub_category = sheet["E670"].value
        subcategory_element_response_create(min_row=671, max_row=673, sheet=sheet, to_category_info=to_category_info,
                                            sub_category=sub_category)

        info_to_subcat_to_cat.update({category_name: to_category_info})  # Aggregate info for each Subcat at CAREGORY
        category_list.append(info_to_subcat_to_cat)

        # ANALYTICS CATEGORY

        category_name = sheet["E676"].value
        info_to_subcat_to_cat = {}
        to_category_info = []  # list of all subcat wit element info

        # Subcategory Performance Management Analytics
        sub_category = sheet["E677"].value
        subcategory_element_response_create(min_row=678, max_row=679, sheet=sheet, to_category_info=to_category_info,
                                            sub_category=sub_category)

        # Subcategory Knowledge Management and Expertise
        sub_category = sheet["E682"].value
        subcategory_element_response_create(min_row=683, max_row=685, sheet=sheet, to_category_info=to_category_info,
                                            sub_category=sub_category)

        info_to_subcat_to_cat.update({category_name: to_category_info})  # Aggregate info for each Subcat at CAREGORY
        category_list.append(info_to_subcat_to_cat)

        pc_response.update({"Category": category_list})
        return pc_response


def eprocurement_response_create(file, workbook):
    """
    Create response from eProcurement parsing
    :param file:
    :return:
    """
    sheet = workbook["RFI"]
    if check_excel_rfi_sheet_structure(file):  # Check that excel file structure equal to source template
        pc_response = {}  # crete response with all element information for each subcat for each category in PC
        pc_response.update({"Parent Category": sheet["E688"].value})
        category_list = []  # list of all category in PC with subcat info and element data

        # CATALOG MANAGEMENT CATEGORY

        category_name = sheet["E689"].value
        info_to_subcat_to_cat = {}
        to_category_info = []  # list of all subcat wit element info

        # Subcategory Catalog Creation / Onboarding
        sub_category = sheet["E690"].value
        subcategory_element_response_create(min_row=691, max_row=700, sheet=sheet, to_category_info=to_category_info,
                                            sub_category=sub_category)

        # Subcategory Catalog Objects
        sub_category = sheet["E703"].value
        subcategory_element_response_create(min_row=704, max_row=706, sheet=sheet, to_category_info=to_category_info,
                                            sub_category=sub_category)

        # Subcategory Catalog Data Quality Control
        sub_category = sheet["E709"].value
        subcategory_element_response_create(min_row=710, max_row=715, sheet=sheet, to_category_info=to_category_info,
                                            sub_category=sub_category)

        # Subcategory Catalog Approvals  / Validations
        sub_category = sheet["E718"].value
        subcategory_element_response_create(min_row=719, max_row=719, sheet=sheet, to_category_info=to_category_info,
                                            sub_category=sub_category)

        # Subcategory Catalog Maintenance
        sub_category = sheet["E722"].value
        subcategory_element_response_create(min_row=723, max_row=723, sheet=sheet, to_category_info=to_category_info,
                                            sub_category=sub_category)

        # Subcategory Catalog Mobility
        sub_category = sheet["E726"].value
        subcategory_element_response_create(min_row=727, max_row=727, sheet=sheet, to_category_info=to_category_info,
                                            sub_category=sub_category)

        # Subcategory Catalog Analytics
        sub_category = sheet["E730"].value
        subcategory_element_response_create(min_row=731, max_row=731, sheet=sheet, to_category_info=to_category_info,
                                            sub_category=sub_category)

        # Subcategory Internet Shopping / Distributed Content
        sub_category = sheet["E734"].value
        subcategory_element_response_create(min_row=735, max_row=735, sheet=sheet, to_category_info=to_category_info,
                                            sub_category=sub_category)

        # Subcategory Catalog Roadmap
        sub_category = sheet["E738"].value
        subcategory_element_response_create(min_row=739, max_row=739, sheet=sheet, to_category_info=to_category_info,
                                            sub_category=sub_category)


        info_to_subcat_to_cat.update({category_name: to_category_info})  # Aggregate info for each Subcat at CAREGORY
        category_list.append(info_to_subcat_to_cat)




        pc_response.update({"Category": category_list})
        return pc_response




pc_to_function_name = {
                            "Common S2P": common_s2p_category_response_create,
                            "Common Sourcing - SXM": common_sourcing_sxm_response_create,
                            "Services": services_response_create,
                            "Sourcing": sourcing_response_create,
                            "SXM": sxm_response_create,
                            "Spend Analytics": spend_analytics_response_create,
                            "CLM": clm_response_create,
                            "eProcurement": eprocurement_response_create,
                            "I2P": None,
                             }
# [
#     {
#         "Parent Category": "COMMON S2P",
#         "Category": [
#             {
#                 "Analytics": [
#                     {
#                         "Data Schema": [
#                             {
#                                 "Element Name": "Breadth",
#                                 "Description": "How broad is the out-of-the-box data schema that underlies the analytics platform and what types of analytics does it support?",
#                                 "Scoring Scale": "0 - not currently supported / not applicable \n1. Limited to spend/transactional/supplier data and a basic mirroring of the data model (to summarize/report data out of) from the applications \n2. An analytical shema that goes beyond reporting off of the workflow-centric data in order to provide deeper quantitative insights on numeric data.  Specific analytic data models are developed to allow deeper performance modeling, causal factor analysis, drill downs through master data taxonomies, etc.\n3. An extended analytics schema that can also support textual data (and processing with reg-ex expressions, etc.) and use of data modeling beyond traditional relational database structures\n4. Capabilities beyond the above and well beyond peers",
#                                 "Self-Score": 5,
#                                 "Self-Description": "Test Self Description !!!!!!!!!!!!!!",
#                                 "Attachments/Supporting Docs and Location/Link": "tui",
#                                 "SM score": 4,
#                                 "Analyst notes": "tytyt"
#                             },
#                             {
#                                 "Element Name": "Extensibility",
#                                 "Description": "How extensible is the data schema that underlies the platform?",
#                                 "Scoring Scale": "0 - not currently supported / not applicable \n1. Limited to a small set of fields in a pre-defined schema format (e.g., fixed data cubes for dice-and-slice)\n2. Unlimited fields in all standard data formats can be added to the existing tables/objects in the schema AND additional tables/'joins' can be created on the fly (permissions allowing)\n3. The schema can also support blobs, multimedia files, real time feeds and more modern data types - and the ability to analyze them (e.g., via NoSQL or equivalent database approaches)\n4. Additional capabilities beyond above and beyond peers",
#                                 "Self-Score": null,
#                                 "Self-Description": null,
#                                 "Attachments/Supporting Docs and Location/Link": null,
#                                 "SM score": null,
#                                 "Analyst notes": null
#                             },
#                             {
#                                 "Element Name": "Multi-Schema Support",
#                                 "Description": "Can the platform support multiple data schemas, namely for tagging and taxonomies?",
#                                 "Scoring Scale": "0 - not currently supported / not applicable \n1. Only a single schema, but tagging is supported \n2. Multiple schemas can be supported simultaneously, but one taxonomy per schema\n3. Multiple taxonomies and tagging structures can be mapped to each schema, and each schema can be cross mapped against multiple taxonomies\n4. Capabilities beyond the above and beyond peers",
#                                 "Self-Score": null,
#                                 "Self-Description": null,
#                                 "Attachments/Supporting Docs and Location/Link": null,
#                                 "SM score": null,
#                                 "Analyst notes": null
#                             },
#                             {
#                                 "Element Name": "Federated Schema Support Capability",
#                                 "Description": "What support is there for data schema federation and the integration of data sets across schemas?  (This capability uses data abstraction to allow mapping of disparate DBs into single virtual composite federated DB to use for analytics.)",
#                                 "Scoring Scale": "0 - not currently supported / not applicable \n1. Can import multiple data sets against multiple schemas, but they are not connected\n2. Can import multiple data sets and link them across common fields\n3. Can import unlimited data sets, cross-link them across common fields, and cross-link to external data sets and feeds \n4. Capabilities beyond the above and beyond peers",
#                                 "Self-Score": null,
#                                 "Self-Description": null,
#                                 "Attachments/Supporting Docs and Location/Link": null,
#                                 "SM score": null,
#                                 "Analyst notes": null
#                             },
#                             {
#                                 "Element Name": "Multi-Taxonomy Support",
#                                 "Description": "Can the platform support multiple data organization taxonomies for analysis and reporting mapped to the underlying data schemas?",
#                                 "Scoring Scale": "0 - not currently supported / not applicable \n1. One taxonomy per schema\n2. Multiple canned taxonomies can be modeled against a schema\n3. Multiple user Taxonomies can be user defined and cross-linked across data schemas\n4. Capabilities beyond above and beyond peers",
#                                 "Self-Score": null,
#                                 "Self-Description": null,
#                                 "Attachments/Supporting Docs and Location/Link": null,
#                                 "SM score": null,
#                                 "Analyst notes": null
#                             },
#                             {
#                                 "Element Name": "Graph Model Support",
#                                 "Description": "Does the platform support graph modeling?",
#                                 "Scoring Scale": "0 - not currently supported / not applicable \n1. our system has a relational schema that also supports relational attributes by way of relationship tables on entity ideas and descriptive fields\n2. our system (also) has an object database that allows related objects to be traversed using standard (textbook) graph traversal algorithms\n3.our system (also) uses a true NoSQL Graph Database that allows for graph-based operations to be easily expressed and utilized in queries, views, and automation\n4. capabilities beyond above and beyond peers",
#                                 "Self-Score": null,
#                                 "Self-Description": null,
#                                 "Attachments/Supporting Docs and Location/Link": null,
#                                 "SM score": null,
#                                 "Analyst notes": null
#                             }
#                         ]
#                     },
#                     {
#                         "Data Management": [
#                             {
#                                 "Element Name": "MDM Capability",
#                                 "Description": "Does the platform support master data management?",
#                                 "Scoring Scale": "0 - not currently supported / not applicable \n1. can ETL master data to the centralized (virtual) data store used by the analytics platform\n2. can cleanse, standardize, match, index, enrich, and harmonize S2P data ETL'd to the centralized master data store to the analytics data model being applied\n3. can also serve as the MDM master for enterprise applications and push back harmonized data to the ERP, S2P, and other platforms as required\n4. capabilities beyond above and beyond peers such as advanced harmonization through best practice views/models, application of AI, etc.",
#                                 "Self-Score": null,
#                                 "Self-Description": null,
#                                 "Attachments/Supporting Docs and Location/Link": null,
#                                 "SM score": null,
#                                 "Analyst notes": null
#                             },
#                             {
#                                 "Element Name": "Data Archival and Auditability",
#                                 "Description": "Does the platform support data archival, with full audit trails?",
#                                 "Scoring Scale": "0 - not currently supported / not applicable \n1. Data can be archived on demand and loaded on demand, who archived or made the last change is recorded\n2. Data can be archived automatically according to certain rules; full secure and unalterable audit trails of all changes are maintained so the user can always find out who changed what,when; and the archive can be easily searched and reported on \n3. the platform contains the ability to automatically identify unused data, archive it, and, if necessary, automatically reload it as needed and full, unauditable audit trails as well as system action logs are always, automatically, maintained\n4. Capabilities beyond above and beyond peers",
#                                 "Self-Score": null,
#                                 "Self-Description": null,
#                                 "Attachments/Supporting Docs and Location/Link": null,
#                                 "SM score": null,
#                                 "Analyst notes": null
#                             },
#                             {
#                                 "Element Name": "API",
#                                 "Description": "What is the extent of the  API with respect to data management?",
#                                 "Scoring Scale": "0 - not currently supported / not applicable \n1. Basic API that can be used to push or pull data in limited CSV/XML formats\n2. Complete API that can be used to push or pull data in a wide variety of formats to and from a plethora of enterprise ERP and S2P systems\n3. Extensive, open, API that can even be used to connect to real-time feeds and non-ERP / S2P enterprise systems, weather in-house or cloud-based \n4. Capabilities beyond above and beyond peers",
#                                 "Self-Score": null,
#                                 "Self-Description": null,
#                                 "Attachments/Supporting Docs and Location/Link": null,
#                                 "SM score": null,
#                                 "Analyst notes": null
#                             },
#                             {
#                                 "Element Name": "3rd Party BI Support",
#                                 "Description": "Can third party BI tools be integrated into the platform for data management and analytics?  If so, how extensive is the support?",
#                                 "Scoring Scale": "0 - not currently supported / not applicable \n1. Data can be exported in a supported format for import into a 3rd party BI tool\n2. Direct connect support for multiple 3rd party BI tools that can use the analytics source directly\n3. Support for simultaneous analysis within the platform and a 3rd party BI tool -- changes in one are immediately reflected in the other and vice versa\n4. Capabilities beyond the above and beyond peers",
#                                 "Self-Score": null,
#                                 "Self-Description": null,
#                                 "Attachments/Supporting Docs and Location/Link": null,
#                                 "SM score": null,
#                                 "Analyst notes": null
#                             },
#                             {
#                                 "Element Name": "Classification / Clustering and Normalization",
#                                 "Description": "Does the platform support classification/clustering (\"familying\") and normalization of entities including, but not limited to suppliers, products, etc.?",
#                                 "Scoring Scale": "0 - not currently supported / not applicable \n1. Suppliers can be familied into a single supplier entity, but that's about it\n2. Multiple, specific, entities can be grouped and families into hierarchies, and familying does not cause original entities to be lost\n3. Any entity can be grouped and families into hierarchies, families can be changed on the fly, and roll ups / drill downs / formulas can all take advantage \n4. Capabilities beyond above and beyond peers",
#                                 "Self-Score": null,
#                                 "Self-Description": null,
#                                 "Attachments/Supporting Docs and Location/Link": null,
#                                 "SM score": null,
#                                 "Analyst notes": null
#                             }
#                         ]
#                     }
#                 ]
#             },
#             {
#                 "Configurability": [
#                     {
#                         "Globalization": [
#                             {
#                                 "Element Name": "Multi-Currency",
#                                 "Description": "How extensive is the built-in support for multi-currency?",
#                                 "Scoring Scale": "0 - not currently supported / not applicable \n1. a single currency conversion table; \n2. integrated currency feed (to FOREX-type data sources) which updates daily; \n3. rules-based conversion based on currency and payment type as well as granular permissioning of multi-currency selection \n4. Includes capabilities beyond which is previously addressed and beyond peers, including the complex orchestration of SCF 3rd parties for optimized recommendations about currency selection",
#                                 "Self-Score": null,
#                                 "Self-Description": null,
#                                 "Attachments/Supporting Docs and Location/Link": null,
#                                 "SM score": null,
#                                 "Analyst notes": null
#                             },
#                             {
#                                 "Element Name": "Multi-Lingual",
#                                 "Description": "How extensive are the multi-lingual support capabilities?",
#                                 "Scoring Scale": "0 - not currently supported / not applicable \n1. flat file menu mappings for a small set of languages; \n2. dynamic mappings of menu options and help text based on standard translations and regional linguistic variances and support for over a dozen languages; \n3. override features that allow a buyer to override mappings on documents / menu options being shared with a supplier and over twenty languages supported; \n4. Includes capability beyond which is previously addressed and beyond peers",
#                                 "Self-Score": null,
#                                 "Self-Description": null,
#                                 "Attachments/Supporting Docs and Location/Link": null,
#                                 "SM score": null,
#                                 "Analyst notes": null
#                             },
#                             {
#                                 "Element Name": "e-Document Regulatory Support",
#                                 "Description": "To what extent is there e-Document regulatory support out of the box?",
#                                 "Scoring Scale": "0 - not currently supported / not applicable \n1. Supports the manual creation of e-Documents that can meet regulatory needs\n2. Automatic e-document creation consistent with multiple regulations \n3. … and governmental requirements from countries around the globe\n4.  Additional support beyond the above and beyond peers",
#                                 "Self-Score": null,
#                                 "Self-Description": null,
#                                 "Attachments/Supporting Docs and Location/Link": null,
#                                 "SM score": null,
#                                 "Analyst notes": null
#                             },
#                             {
#                                 "Element Name": "e-Payment Support",
#                                 "Description": "To what extent does the platform support e-Payments?",
#                                 "Scoring Scale": "0 - not currently supported / not applicable \n1. Can push approved payments to an e-Payment system\n2. P-card, ACH, and Wire support for local and some global payments\n3. Support for third party invoice factoring, lending, and non-bank payment platforms\n4. Support beyond the above and beyond peers\n",
#                                 "Self-Score": null,
#                                 "Self-Description": null,
#                                 "Attachments/Supporting Docs and Location/Link": null,
#                                 "SM score": null,
#                                 "Analyst notes": null
#                             },
#                             {
#                                 "Element Name": "GDPR / Privacy Standards",
#                                 "Description": "How extensive is the built-in support for GDPR and similar global privacy standards?",
#                                 "Scoring Scale": "0 - not currently supported / not applicable \n1. Personal Data can be encrypted\n2. Built in support for anonymizing / purging of all personal information as needed to comply with GDPR\n3. Built-in support for multiple privacy regulations around the globe\n4. Setting new standards in privacy support and capabilities beyond peers",
#                                 "Self-Score": null,
#                                 "Self-Description": null,
#                                 "Attachments/Supporting Docs and Location/Link": null,
#                                 "SM score": null,
#                                 "Analyst notes": null
#                             },
#                             {
#                                 "Element Name": "Other Globalization Support",
#                                 "Description": "What other types of globalization support is baked into the platform?",
#                                 "Scoring Scale": "Scored against peers.  Make the case!",
#                                 "Self-Score": null,
#                                 "Self-Description": null,
#                                 "Attachments/Supporting Docs and Location/Link": null,
#                                 "SM score": null,
#                                 "Analyst notes": null
#                             },
#                             {
#                                 "Element Name": "Roadmap",
#                                 "Description": "What is your globalization roadmap that will advance your  solution in the next 6 months (if applicable)?  Give directional input if you can't share exact details",
#                                 "Scoring Scale": "Scored against peers.  Make the case!",
#                                 "Self-Score": null,
#                                 "Self-Description": null,
#                                 "Attachments/Supporting Docs and Location/Link": null,
#                                 "SM score": null,
#                                 "Analyst notes": null
#                             }
#                         ]
#                     },
#                     {
#                         "Organizational Modeling": [
#                             {
#                                 "Element Name": "Organizational Hierarchy",
#                                 "Description": "Does the platform support the modelling of the organizational hierarchy?",
#                                 "Scoring Scale": "0 - not currently supported / not applicable \n1. Can model organizational hierarchies to support all of the following business entities / units, functions, budgetary approvals, ledgers/sub-ledgers, user roles, and custom user groups.\n2. Can also model geographic hierarchies (down to site / location level) and positional hierarchies (e.g,. job levels/grades with associated job codes and descriptions)\n3. Can manage matrixed/hybrid structures and consider multiple hierarchies in the context of the workflows and user rights controlled by those hierarchies.\n4. Even more complex organizational modelling beyond peers",
#                                 "Self-Score": null,
#                                 "Self-Description": null,
#                                 "Attachments/Supporting Docs and Location/Link": null,
#                                 "SM score": null,
#                                 "Analyst notes": null
#                             },
#                             {
#                                 "Element Name": "Account Structures ",
#                                 "Description": "How sophisticated  is the support for the definition and maintenance of account structures?",
#                                 "Scoring Scale": "0 - not currently supported / not applicable \n1. Basic account code support … \n2. Account code structures and associated business rules that automatically match purchases to account codes (including sub-ledgers)\n3. Support for multiple/differing accounting, taxation, and reporting structures/rules applied within different fiscal entities, regions, countries, etc.\n4. Advanced account management functionality beyond peers ",
#                                 "Self-Score": null,
#                                 "Self-Description": null,
#                                 "Attachments/Supporting Docs and Location/Link": null,
#                                 "SM score": null,
#                                 "Analyst notes": null
#                             },
#                             {
#                                 "Element Name": "Budget Support",
#                                 "Description": "How extensive is the budgetary support in the platform?",
#                                 "Scoring Scale": "0 - not currently supported / not applicable \n1=Budgets are modeled based on org hierarchy and G/L for the current period, but client manages budgets in separate budgeting app (e.g., ERP).  Application models spending and/against budgets\n2=Budget figures can be maintained natively (e.g., money can be moved around) and are actively integrated with other parts of solution and referenced within the workflow (e.g, alerts when exceeding/overconsuming) \n3=Support for \"spend planning\"/forecasting (and dynamic target setting/monitoring) tied to TCO elements and consumption drivers.  Use of predictive monitoring/alerts.  4=Advanced analytics, AI, or other major differentiators",
#                                 "Self-Score": null,
#                                 "Self-Description": null,
#                                 "Attachments/Supporting Docs and Location/Link": null,
#                                 "SM score": null,
#                                 "Analyst notes": null
#                             },
#                             {
#                                 "Element Name": "Team Modelling & Management",
#                                 "Description": "How sophisticated is the team modeling and management capability?",
#                                 "Scoring Scale": "0 - not currently supported / not applicable \n1. Team members can be defined within user groups / \"teams\" (AND have users assigned different standard/definable roles as well)\n2. Team members can be assigned to projects, put on tasks, associated with milestones, and have their progress tracked as a team (or team member).  Basic work queues can be established for these user groups before a team member takes a task from the queue.\n3. Multi-view visual team-management allows team members to be managed across projects and projects to be managed across teams.  Advanced work queue management with rule-based team member assignments.\n4. Even more advanced capability that goes beyond peers ... ",
#                                 "Self-Score": null,
#                                 "Self-Description": null,
#                                 "Attachments/Supporting Docs and Location/Link": null,
#                                 "SM score": null,
#                                 "Analyst notes": null
#                             },
#                             {
#                                 "Element Name": "Talent Management",
#                                 "Description": "Does the platform support talent management processes to engage and support employees",
#                                 "Scoring Scale": "*This question does not include on-line training which is asked elsewhere\n1. Support for not just \"roles\" and \"user groups\", but also job descriptions, job codes, job levels, salaries (optional), and other basic HR-related employee information.\n2. Employee performance appraisals and basic training/development, including goals/objectives setting,  self-assessments, performance appraisals, tracking of required/actual training hours & certifications, etc.\n3. Strong talent management process support including skills/competencies modeling, granular assessments (including 3rd party assessments), learning/development planning (which drives training requirements/curricula), succession planning.\n4. Advanced capabilities beyond peers (e.g., integrating procurement talent management and contingent workforce planning into enterprise talent management processes)",
#                                 "Self-Score": null,
#                                 "Self-Description": null,
#                                 "Attachments/Supporting Docs and Location/Link": null,
#                                 "SM score": null,
#                                 "Analyst notes": null
#                             },
#                             {
#                                 "Element Name": "Asset Management",
#                                 "Description": "Does the platform have built in capability for asset management?",
#                                 "Scoring Scale": "0 - not currently supported / not applicable \n1. Asset reference field to note assets (e.g., IT/Lab/Mfg equipment; software asset tracking) being purchased/managed; \n2. \"Asset master\" to be able to track assets (e.g., software license tracking); \n3. Asset BOMs; Asset TCO elements for CapEx; maintenance/service pricing and history; software TCO/license modeling and tracking; \n4. Advanced asset management (predictive, AI, etc.)",
#                                 "Self-Score": null,
#                                 "Self-Description": null,
#                                 "Attachments/Supporting Docs and Location/Link": null,
#                                 "SM score": null,
#                                 "Analyst notes": null
#                             }
#                         ]
#                     }
#                 ]
#             }
#         ]
#     },
#     {
#         "Parent Category": "COMMON SOURCING - SXM",
#         "Category": [
#             {
#                 "Contingent Workforce / Services Procurement": [
#                     {
#                         "Contingent Workforce Management": [
#                             {
#                                 "Element Name": "Independent Contract Worker (ICW) Management",
#                                 "Description": "To what extent does the platform support the use/management of ICWs?",
#                                 "Scoring Scale": "0 - not currently supported / not applicable \n1. Managed like any other supplier that can self-register, but able to provide a W-9, attach certifications or proof of insurance, submit invoices (and associated time sheets or deliverables), etc. \n2. Basic independent contract worker management for sourcing/SXM (e.g., resume processing with OCR; background checks), worker classification, compliance, rudimentary contract management, 1099-MISC management, reporting, etc. \n3. Full ICW management (Freelancer Management System): direct sourcing, talent pool management (including skill/competency modeling),  onboard-off board, advanced compliance functionality VMS integration, use by MSPs, VMS integration, AOR/EOR integration, VMS integration \n4. Additional capabilities beyond above and beyond peers",
#                                 "Self-Score": null,
#                                 "Self-Description": null,
#                                 "Attachments/Supporting Docs and Location/Link": null,
#                                 "SM score": null,
#                                 "Analyst notes": null
#                             },
#                             {
#                                 "Element Name": "Temporary Staffing Management",
#                                 "Description": "To what extent does the platform support the use/management of temporary staffing?",
#                                 "Scoring Scale": "0 - not currently supported / not applicable \n1. Can generate requisitions that can be passed to VMS\n2. Can only model the staffing firm as the supplier and then process invoices from them (with time sheet / rate details) that are matched to rate cards via a 'services catalog'\n3-Can model the temporary worker as a worker and  enable candidate requisitions, candidate review/selection, candidate self-service timesheets/approvals, compliance checking and reporting, etc.)\n4=Full featured \"VMS\" capabilities including program management for internally and MSP managed programs",
#                                 "Self-Score": null,
#                                 "Self-Description": null,
#                                 "Attachments/Supporting Docs and Location/Link": null,
#                                 "SM score": null,
#                                 "Analyst notes": null
#                             },
#                             {
#                                 "Element Name": "Services/SOW Management",
#                                 "Description": "To what extent does the platform support the use/management of workers from a 3rd party service provider (e.g., a consulting firm, outsourcer, et al?",
#                                 "Scoring Scale": "0 - not currently supported / not applicable \n1- Can model and manage providers (suppliers) of services and source projects/activities from them\n2. Can model provider's workers,  have worker rates, implement SOWs under an MSA, enable worker onboarding/off boarding to/from projects/activities, apply basic compliance control (background checks, etc.), track worker activities\n3. Can collaborate with supplier to select workers; create standalone (no MSA) SOWs or services contracts; manage SOW-contract lifecycle; manage project/engagements, milestones, deliverables; provide worker-level milestones tracking; support time and expense reporting; process change orders; enable project and worker evaluation; support worker-level itemized invoice creation\n4. Additional capabilities beyond above and beyond peers",
#                                 "Self-Score": null,
#                                 "Self-Description": null,
#                                 "Attachments/Supporting Docs and Location/Link": null,
#                                 "SM score": null,
#                                 "Analyst notes": null
#                             }
#                         ]
#                     }
#                 ]
#             },
#             {
#                 "Performance Management": [
#                     {
#                         "Supplier Performance Management": [
#                             {
#                                 "Element Name": "Preferred Supplier Status",
#                                 "Description": "Does the platform support preferred supplier status?  How extensive is the support?",
#                                 "Scoring Scale": "0 - not currently supported / not applicable \n1. account / contract managers / buyers can mark suppliers as preferred\n2. preferred suppliers can be defined at the category and product/service level, and the system can limit selection to preferred suppliers in appropriate situations based on user-defined rules\n3. the system supports automatic definition of preferred and preferential suppliers based on contracts, quality approvals, and (total) costs\n4. capabilities above and beyond peers",
#                                 "Self-Score": null,
#                                 "Self-Description": null,
#                                 "Attachments/Supporting Docs and Location/Link": null,
#                                 "SM score": null,
#                                 "Analyst notes": null
#                             },
#                             {
#                                 "Element Name": "Blocked/Blacklisted Suppliers",
#                                 "Description": "Does the platform support blocking and blacklisting of suppliers?  How extensive is the support?",
#                                 "Scoring Scale": "0 - not currently supported / not applicable \n1. the system supports the manual definition of blocked and blacklisted suppliers\n2. the system supports the definition of blocked suppliers at the category and product levels, by geography \n3. the system can automatically blacklist and/or block suppliers based upon government denied party lists, financial distress (bankruptcy), lack of quality (slips below threshold), poor performance (due to consistently late deliveries, etc.) on a scorecard and other user-defined rules\n4. capabilities above and beyond peers",
#                                 "Self-Score": null,
#                                 "Self-Description": null,
#                                 "Attachments/Supporting Docs and Location/Link": null,
#                                 "SM score": null,
#                                 "Analyst notes": null
#                             }
#                         ]
#                     }
#                 ]
#             }
#         ]
#     }
# ]

[
    [
        {
            "rfi": "20R1",
            "vendor": "Actual2",
            "m": "Strategic Sourcing",
            "active": "false"
        },
        {
            "rfi": "20R1",
            "vendor": "Actual2",
            "m": "Supplier Management",
            "active": "true"
        }

    ],
    [
        {
            "rfi": "20R1",
            "vendor": "Test",
            "m": "Strategic Sourcing",
            "active": "false"
        },
        {
            "rfi": "20R1",
            "vendor": "Test",
            "m": "Supplier Management",
            "active": "true"
        }

    ]

]