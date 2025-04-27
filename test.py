import pdfplumber
import re
import datetime 
import os
import json




class PDFETL:
    """
    A class to extract, transform, and load data from a PDF file.
    """

    def __init__(self, area_list, source_list, pdf_output= 'pdf.json'):
        self.area_list = area_list
        self.source_list = source_list
        self.pdf_output = pdf_output    
        self.data_folder = os.path.join(os.getcwd(), "data_folder")

    
    # this function will get the raw data from the pdf file
    # the function will take the file path of the pdf file and extract the text from it
    # the function will return the raw text


    def get_raw_data_from_pdf(self, file_path):
        base_dir = os.path.join(os.getcwd(), "data_folder")
        file_path = os.path.join(base_dir, file_path)
        if not os.path.exists(file_path):
            print(f"File not found: {file_path}")
            return None
        # Extract text from the PDF file
        all_tables_data = []

        try:
            with pdfplumber.open(file_path) as pdf:
                for page_num, page in enumerate(pdf.pages):
                    print(f"Processing page {page_num + 1}...")
                    tables = page.find_tables()
                    for table in tables:
                        table_data = table.extract()
                        if table_data:
                            all_tables_data.extend(table_data)
            return all_tables_data


        except Exception as e:
            print(f"Error extracting text from PDF: {e}")
            return None
    
    # this function will align the content of the pdf file
    # the function will take the content of the pdf file and align it into a tabular format
    # the function will return the aligned content
    def align_content(self, content):
        align_content = {}
        owner_section = content[1:5]
        inventory_section = content[5:]
        owner_info = "Owner Information:\n"
        for row in owner_section:
            owner_info += f"{row[0]}: {row[1]}\n"
        align_content['Owner Information'] = owner_info 
        # return align_content
        inventory_columns = inventory_section[0]

        row_data = inventory_section[1]
        condition_raw = inventory_section[2]
        condition_data = inventory_section[3][0]
        condition_table = "Condition:\n"
        condition_table += f"{condition_raw[0]:<10}\n"
        condition_table += "-" * 15 + "\n"

        # print(condition_data)
        texts = row_data[0]
    
        align_inventory_columns = "Inventory:\n" 
        align_inventory_columns += f"{inventory_columns[0]:<10} {inventory_columns[1]:<10} {inventory_columns[2]:<10} {inventory_columns[3]:<10} {inventory_columns[4]:<10} {inventory_columns[5]:<10} {inventory_columns[6]:<10}\n "
        align_inventory_columns += "-" * 100 + "\n"
        # print(align_inventory_columns)
        regex =r"(\d+)\s([\w\s]+)\s(\w+)\s(\w+)\s(\d{2}/\d{2}/\d{4})\s(\w+)\s(\w+)\s([$]\s[\d,.]+)"

        for text in texts.strip().split('\n'):
            match = re.search(regex, text)
            if match:
                number = match.group(1)
                area = match.group(2)
                # print(area)
                item_description = match.group(3)
                source = match.group(4)
                purchase_date= datetime.datetime.strptime(match.group(5), "%d/%m/%Y").date()
                style = match.group(6)
                serial_num = match.group(7)
                value = match.group(8)

                # processing area data 

                matched_area = None
                for a in area_list:
                    if a in area:
                        matched_area = a
                        
                        item_description = area.replace(matched_area, "").strip() + " " + item_description
                        
                        break

                else:
                    # print("No area matched, using full area as matched_area")
                    matched_area = area

                # processing item description data and source data
                for sources in ['Best', 'Home']:
                    if sources in item_description:
                        # this will split the item description and source but the source is not returned
                        # as a separate variable,
                        #  so i use the sources variable which was found and added it to the source variable
                        items = item_description.split(sources, 1)  
                        # print(f"Items: {items}")
                        item_description = items[0].strip()
                        # print(f"Items: {item_description}")
                        source = sources+ " " + source
                        # print(f"Source: {source}")
                        break

                else:
                    item_description = item_description
                    source = source



                align_inventory_columns += f"{number:<10} {matched_area:<10} {item_description:<10} {source:<10} {purchase_date.strftime('%d-%m-%Y'):<15} {style:<10} {serial_num:<10}  {value:<10}\n"
            else: 
                align_inventory_columns += "No match found for this item.\n"
                align_content['Inventory'] = align_inventory_columns

        for condition in condition_data.strip().split('\n'):
            condition_table += f"{condition}\n"
        align_content['Condition'] = condition_table

        
        
        return align_content
    

# this function will extract the data from the aligned content and return it in a dictionary format
# the function will take the aligned content and extract the data from it

# extract data into dictionary 
    def extract_data(self, test):
        extracted_data = {}
        for section, content in test.items():
            if section == 'Owner Information':
                owner_info = {}
                lines = content.split('\n')[1:]
                for line in lines:
                    if ':' in line:
                        key, value = line.split(':', 1)
                        owner_info[key.strip()] = value.strip()
                extracted_data['Owner Information'] = owner_info

            elif section == 'Inventory':
                inventory_list = []
                lines = content.split('\n')[2:]  # Skip the header lines
                # regular expression to match the area and source values in the inventory
                area_regex = r"(?P<area>" + "|".join(area_list) + ")"
                source_regex = r"(?P<source>" + "|".join(source_list) + ")"

                # regex to match the inventory data
                # the regex will match the number, area, item description, source, purchase date, style, serial number and value
                # the regex will also match the area and source values if they are present

                regex = rf"""
                    (?P<number>\d+)\s+
                    (?:{area_regex}\s+)?
                    (?P<item_description>(?:[\w\s'-]+?))\s+
                    (?:{source_regex}\s+)?
                    (?P<date>\d{{2}}-\d{{2}}-\d{{4}})\s+
                    (?P<style>\w+)\s+
                    (?P<serial_number>\w+)\s+
                    (?P<value>[$]\s[\d,.]+)
                """

                # for loop to iterate through the lines of the inventory data
                # the regex will match the number, area, item description, source, purchase date, style, serial number and value
                for line in lines:

                    match = re.search(regex, line.strip(), re.VERBOSE)
                    # print(match)

                    if match:
                        number = match.group('number')
                        # Default to empty string if not found
                        area = match.group('area') or ''  
                        item_description = match.group('item_description').strip()
                        source = match.group('source') or ''
                        date_str = match.group('date')
                        style = match.group('style')
                        serial_number = match.group('serial_number')
                        value = match.group('value')        
                
                        # Convert the date string to ISO format
                        try:
                            date_string = datetime.datetime.strptime(date_str, "%d-%m-%Y").date()
                            purchase_date_iso = date_string.isoformat()
                        except ValueError:
                            print(f"Invalid date format: {date_str}")
                        # continue
                    # Create a dictionary for each inventory item
                        inventory_item = {
                            'Number': number,
                            'Area': area,
                            'Item Description': item_description,
                            'Source': source,
                            'Purchase Date': purchase_date_iso,
                            'Style': style,
                            'Serial Number': serial_number,
                            'Value': value
                        }
                        inventory_list.append(inventory_item)
                extracted_data['data'] = inventory_list
            elif section == 'Condition':
                condition_list = []
                lines = content.split('\n')[3:] # Skip the header lines
                for line in lines:
                    if line.strip():  # Ignore empty lines
                        condition_list.append(line.strip())
                
            # merge the condition list into the data dictionary
                if 'data' in extracted_data:
                    for index, item in enumerate(extracted_data['data']):
                        if index < len(condition_list):
                            item['Condition'] = condition_list[index]
                        else:
                            item['Condition'] = 'N/A'

        return extracted_data
    
    # this function will save the extracted data to a json file
    def save_to_json(self, data, output_file):
        output_path = os.path.join(self.data_folder, output_file)
        with open(output_path, 'w') as json_file:
            json.dump(data, json_file, indent=4)
        print(f"Data saved to {output_path}")


   
    # the function will take the file path of the pdf file and run the etl process

    def run(self, file_path):
        raw_data = self.get_raw_data_from_pdf(file_path)
        if raw_data is None:
            print("No data extracted from the PDF.")
            return
        aligned_content = self.align_content(raw_data)
        if aligned_content is None:
            print("Failed to process the PDF content.")
            return
        extracted_data = self.extract_data(aligned_content)
        if extracted_data is None:
            print("Failed to extract data from the PDF content.")
            return
        self.save_to_json(extracted_data, self.pdf_output) 


    
if __name__ == "__main__":
    area_list = ["Kitchen", "Living Room", "Dining Room", "Bedroom", "Bathroom", "Garage", "Office"]
    source_list = ["Home Depot", "Best Buy", 'Target', 'Walmart', 'Amazon', 'Wayfair']
    pdf_file = "home_inventory.pdf"
    pdf_etl = PDFETL(area_list, source_list)
    extracted_data = pdf_etl.run(pdf_file)
    if extracted_data:
        print("Data extraction and transformation completed successfully.")
    else:
        print("Data extraction and transformation failed.")
   
