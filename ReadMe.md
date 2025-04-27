# PDF ETL (Extract, Transform, Load) Pipeline
This project extracts structured data from PDF files, transforms the raw content into a clean tabular format, and saves the processed data into a JSON file. The project is test assessment for the role of Data Science Intern at Periculum. 
It is particularly useful for inventory PDFs like home inventories, property audits, or condition reports.

## Features
## Extract: 

Reads table data from PDF documents using pdfplumber.

## Transform:

Aligns and formats data (inventory items, owner information, and conditions).

Handles areas and sources based on pre-defined lists.

Cleans and restructures extracted text into usable formats.

## Load: 

Outputs the final structured data into a JSON file for easy further use.

## Project Structure

project/
│
├── data_folder/
│
├── pdf_etl.py            
│
└── README.md


## How It Works
Extract:
Extracts raw tables from the PDF file using pdfplumber.

Transform:

Parses the Owner Information, Inventory List, and Condition Report.

Recognizes Area (e.g., "Kitchen", "Living Room") and Source (e.g., "Home Depot", "Best Buy") fields.

Corrects misaligned item descriptions and sources when necessary.

Formats the purchase dates into ISO format.

Load:
Saves the structured data into a JSON file inside the data_folder/.



## How to Run
- Place your PDF file (e.g., home_inventory.pdf) inside the data_folder/.

- Install the required dependencies:
    - pip install pdfplumber

    - python pdf_etl.py

- After running, the extracted and cleaned data will be saved into a file called pdf.json inside data_folder/.

## Configuration
You can adjust the recognized areas and sources easily by editing the lists


## Requirements
- Python 3.7+
- Libraries:
- pdfplumber
- re
- datetime
- os
- json


## Notes
- The data_folder/ must exist in the project directory; otherwise, the script will raise a path error.
- If the PDF structure changes significantly (e.g., missing headers, new columns), the parsing logic may need slight modifications.
- The script expects a specific layout: Owner information, Inventory table, and Condition list. Unexpected formats might not parse correctly.
