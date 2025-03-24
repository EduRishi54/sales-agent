# EduRishi Sales Assistant

An AI-powered sales assistant and CRM application built with Streamlit and Google's Generative AI (Gemini 1.5 Flash).

## Features

- **AI Sales Assistant**: Generate personalized sales responses based on customer data
- **CRM Dashboard**: Visualize leads, deals, and sales metrics
- **Lead & Deal Management**: Track and manage your sales pipeline
- **Task & Calendar Management**: Schedule and track meetings and tasks
- **Conversation History**: Keep track of all customer interactions
- **Sales Scripts**: Access pre-written sales scripts and templates
- **Product Catalog**: Browse and showcase EduRishi's educational products

## Installation

1. Clone this repository:
```bash
git clone https://github.com/yourusername/edurishi-sales-assistant.git
cd edurishi-sales-assistant
```

2. Create a virtual environment and activate it:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install the required packages:
```bash
pip install -r requirements.txt
```

4. Run the application:
```bash
streamlit run edurishi_sales_assistant.py
```

## Usage

1. Configure your Google Generative AI API key in the sidebar
2. Upload a CSV file with customer data
3. Use the different tabs to access various features of the application

## CSV Data Format

The application expects a CSV file with the following columns:
- Name of Customer
- Person Name
- Designation
- Email
- Phone
- City
- State
- Address
- Pincode
- Product Interested
- Budget

You can download a sample template from the application.

## Deployment

This application can be deployed on Streamlit Cloud:

1. Fork this repository to your GitHub account
2. Sign up for [Streamlit Cloud](https://streamlit.io/cloud)
3. Create a new app and select your forked repository
4. Set up your API key in the Streamlit Cloud secrets management

## Required Files

- `edurishi_sales_assistant.py`: Main application file
- `city_business_dashboard.py`: Dashboard module
- `indian_cities_data.py`: Cities data module
- `edurishi.png`: Logo file (optional)

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Built with [Streamlit](https://streamlit.io/)
- Powered by [Google Generative AI](https://ai.google.dev/)# EduRishi Sales Assistant

This Streamlit application uses Gemini 1.5 Flash to generate personalized sales responses based on customer data from CSV files and user-provided enquiry details.

## Features Added

1. **Company Logo**: Added the EduRishi company logo to the top left corner of the application using the edurishi.png file. The logo is properly aligned with the company name displayed next to it.

2. **Products Based on Schools_Enquiry.csv**:
   - **Core Programs**: ELAP, MDL, PBL, ICT, LMS
   - **AI Solutions**: AI Workshop, AI software, AI tutor, Simulation, Simulations
   - **Educational Materials**: E2MP, E2MP workshop, E2MP software
   - **Business Solutions**: Franchise Proposal, Tech Franchise, Entrepreneurship Workshop

3. **Updated Product Categories**:
   - Core Educational Programs
   - AI & Technology Solutions
   - Educational Materials & Programs
   - Business & Entrepreneurship

4. **New Product Bundles Based on Customer Interests**:
   - School Starter Package
   - Advanced Learning Suite
   - Complete School Transformation
   - LMS Integration Package
   - AI Education Bundle
   - Simulation Learning Package
   - E2MP Complete Solution
   - University Package

## How to Use

1. Place the `edurishi.png` logo file in the same directory as the application.
2. Make sure you have the `Schools_Enquiry .csv` file in the same directory.
3. Run the application:
   ```
   streamlit run edurishi_sales_assistant.py
   ```

4. Configure your API key in the sidebar or use the demo mode.
5. Select a customer from the dropdown menu.
6. Enter the customer's enquiry details.
7. Click "Generate Personalized Response" to create a tailored sales pitch.

## Product Information

The application now includes the following products based on Schools_Enquiry.csv:

### Core Educational Programs
- ELAP (Experiential Learning and Assessment Program)
- MDL (Multi-Dimensional Learning)
- PBL (Project-Based Learning)
- ICT (Information and Communication Technology)
- LMS (Learning Management System)

### AI & Technology Solutions
- AI Workshop
- AI software
- AI tutor
- Simulation
- Simulations

### Educational Materials & Programs
- Book Publisher
- E2MP (EduRishi Educational Materials Program)
- E2MP workshop
- E2MP software

### Business & Entrepreneurship
- Franchise Proposal
- Tech Franchise
- Entrepreneurship Workshop

## Customer Data

The application is configured to work with the Schools_Enquiry.csv file which contains:
- School names and contact information
- Contact person details
- Professional roles (School Relationship Manager, Admin Dept, Admin Head, CEO, VC)
- Products pitched to each customer
- Products the customer is interested in
- Budget information

## Requirements

- Python 3.7+
- Streamlit
- Pandas
- Google Generative AI (Gemini)
- Matplotlib
- NumPy
- Cryptography
- PIL (Pillow)

## Note

This application is specifically designed to work with the Schools_Enquiry.csv file format. The column mapping has been updated to match this format.