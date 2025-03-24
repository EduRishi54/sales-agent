"""
Indian Cities Data Module

This module provides functions to access and generate data about Indian cities,
states, and business types for the EduRishi Sales Assistant application.
"""

import random
import uuid
from datetime import datetime, timedelta
import json

# Sample data for Indian states and cities
INDIAN_STATES_CITIES = {
    "Maharashtra": ["Mumbai", "Pune", "Nagpur", "Thane", "Nashik", "Aurangabad", "Solapur", "Amravati", "Kolhapur", "Sangli"],
    "Delhi": ["New Delhi", "North Delhi", "South Delhi", "East Delhi", "West Delhi", "Central Delhi", "Shahdara", "Dwarka"],
    "Karnataka": ["Bengaluru", "Mysuru", "Hubli", "Mangaluru", "Belgaum", "Gulbarga", "Davanagere", "Shimoga", "Tumkur", "Udupi"],
    "Tamil Nadu": ["Chennai", "Coimbatore", "Madurai", "Tiruchirappalli", "Salem", "Tirunelveli", "Erode", "Vellore", "Thoothukudi", "Dindigul"],
    "Uttar Pradesh": ["Lucknow", "Kanpur", "Agra", "Varanasi", "Meerut", "Prayagraj", "Ghaziabad", "Aligarh", "Bareilly", "Moradabad"],
    "Gujarat": ["Ahmedabad", "Surat", "Vadodara", "Rajkot", "Bhavnagar", "Jamnagar", "Junagadh", "Gandhinagar", "Anand", "Navsari"],
    "West Bengal": ["Kolkata", "Howrah", "Durgapur", "Asansol", "Siliguri", "Bardhaman", "Malda", "Kharagpur", "Darjeeling", "Haldia"],
    "Telangana": ["Hyderabad", "Warangal", "Nizamabad", "Karimnagar", "Khammam", "Ramagundam", "Mahbubnagar", "Nalgonda", "Adilabad", "Suryapet"],
    "Rajasthan": ["Jaipur", "Jodhpur", "Udaipur", "Kota", "Bikaner", "Ajmer", "Bhilwara", "Alwar", "Sikar", "Bharatpur"],
    "Kerala": ["Thiruvananthapuram", "Kochi", "Kozhikode", "Thrissur", "Kollam", "Palakkad", "Alappuzha", "Kannur", "Kottayam", "Malappuram"],
    "Andhra Pradesh": ["Visakhapatnam", "Vijayawada", "Guntur", "Nellore", "Kurnool", "Rajahmundry", "Tirupati", "Kakinada", "Kadapa", "Anantapur"],
    "Punjab": ["Ludhiana", "Amritsar", "Jalandhar", "Patiala", "Bathinda", "Mohali", "Pathankot", "Hoshiarpur", "Batala", "Moga"],
    "Haryana": ["Faridabad", "Gurgaon", "Panipat", "Ambala", "Yamunanagar", "Rohtak", "Hisar", "Karnal", "Sonipat", "Panchkula"],
    "Madhya Pradesh": ["Indore", "Bhopal", "Jabalpur", "Gwalior", "Ujjain", "Sagar", "Dewas", "Satna", "Ratlam", "Rewa"],
    "Bihar": ["Patna", "Gaya", "Bhagalpur", "Muzaffarpur", "Darbhanga", "Arrah", "Begusarai", "Chhapra", "Katihar", "Munger"]
}

# Business types and subcategories
BUSINESS_TYPES = {
    "Educational": [
        "Schools", "Colleges", "Universities", "Coaching Centers", "Tutoring Services", 
        "Vocational Training", "Language Institutes", "Special Education", "Preschools", "Online Education"
    ],
    "Industrial": [
        "Manufacturing", "Automotive", "Electronics", "Textiles", "Chemicals", 
        "Pharmaceuticals", "Food Processing", "Mining", "Construction", "Energy"
    ],
    "Technology": [
        "Software Development", "IT Services", "Web Development", "Mobile App Development", "Cloud Services", 
        "Cybersecurity", "Data Analytics", "Artificial Intelligence", "IoT Solutions", "Blockchain"
    ],
    "Healthcare": [
        "Hospitals", "Clinics", "Diagnostic Centers", "Pharmacies", "Medical Equipment", 
        "Telemedicine", "Mental Health", "Elderly Care", "Rehabilitation", "Alternative Medicine"
    ],
    "Retail": [
        "Supermarkets", "Department Stores", "Clothing", "Electronics Stores", "Furniture", 
        "Jewelry", "Bookstores", "Sports Equipment", "Home Improvement", "E-commerce"
    ],
    "Hospitality": [
        "Hotels", "Restaurants", "Cafes", "Catering", "Event Management", 
        "Travel Agencies", "Tour Operators", "Resorts", "Spas", "Nightclubs"
    ],
    "Financial": [
        "Banks", "Insurance", "Investment Firms", "Accounting Services", "Tax Consultants", 
        "Financial Advisors", "Credit Unions", "Microfinance", "Payment Processing", "Wealth Management"
    ]
}

# Sample company name templates
COMPANY_NAME_TEMPLATES = {
    "Educational": [
        "{city} International School", 
        "{city} Public School", 
        "{name} Academy", 
        "St. {name}'s School", 
        "Modern {city} School", 
        "{name} College", 
        "{city} University", 
        "{name} Institute of Technology", 
        "{city} Educational Society", 
        "Global Education {city}"
    ],
    "Industrial": [
        "{name} Industries", 
        "{city} Manufacturing Co.", 
        "{name} Engineering Works", 
        "{city} Industrial Solutions", 
        "{name} Fabrication", 
        "{city} Steel", 
        "{name} Automotive", 
        "{city} Chemicals", 
        "{name} Textiles", 
        "Modern {city} Industries"
    ],
    "Technology": [
        "{name} Technologies", 
        "{city} Software Solutions", 
        "{name} IT Services", 
        "{city} Digital", 
        "{name} Tech", 
        "{city} Innovations", 
        "{name} Systems", 
        "{city} Infosystems", 
        "{name} Computing", 
        "Next Gen {city} Tech"
    ],
    "Healthcare": [
        "{city} General Hospital", 
        "{name} Medical Center", 
        "{city} Healthcare", 
        "{name} Clinic", 
        "{city} Diagnostics", 
        "{name} Wellness", 
        "{city} Pharmacy", 
        "{name} Health Services", 
        "{city} Medical Equipment", 
        "Care {name} Hospital"
    ],
    "Retail": [
        "{name} Retail", 
        "{city} Supermarket", 
        "{name} Stores", 
        "{city} Shopping Center", 
        "{name} Mart", 
        "{city} Fashion", 
        "{name} Electronics", 
        "{city} Furniture", 
        "{name} Jewelers", 
        "Modern {city} Retail"
    ],
    "Hospitality": [
        "Hotel {name}", 
        "{city} Resort", 
        "{name} Restaurant", 
        "{city} Catering", 
        "{name} Cafe", 
        "{city} Travels", 
        "{name} Events", 
        "{city} Tourism", 
        "{name} Hospitality", 
        "Grand {city} Hotel"
    ],
    "Financial": [
        "{name} Finance", 
        "{city} Bank", 
        "{name} Insurance", 
        "{city} Investments", 
        "{name} Financial Services", 
        "{city} Accounting", 
        "{name} Tax Consultants", 
        "{city} Wealth Management", 
        "{name} Capital", 
        "Secure {city} Finance"
    ]
}

# Sample person names
FIRST_NAMES = [
    "Aarav", "Vivaan", "Aditya", "Vihaan", "Arjun", "Reyansh", "Ayaan", "Atharva", "Krishna", "Ishaan",
    "Shaurya", "Advait", "Dhruv", "Kabir", "Ritvik", "Aarush", "Kayaan", "Darsh", "Veer", "Samar",
    "Aanya", "Aadhya", "Aarna", "Ananya", "Diya", "Myra", "Sara", "Iraa", "Ahana", "Anvi",
    "Prisha", "Riya", "Aarohi", "Anaya", "Akshara", "Shanaya", "Kyra", "Samara", "Tara", "Kiara"
]

LAST_NAMES = [
    "Sharma", "Verma", "Patel", "Gupta", "Singh", "Kumar", "Jain", "Shah", "Mehta", "Agarwal",
    "Reddy", "Nair", "Menon", "Iyer", "Rao", "Malhotra", "Chopra", "Joshi", "Bose", "Chatterjee",
    "Banerjee", "Mukherjee", "Das", "Sen", "Dutta", "Desai", "Patil", "Kaur", "Kapoor", "Khanna",
    "Saxena", "Bhatia", "Chauhan", "Chaudhary", "Mehra", "Sinha", "Trivedi", "Pandey", "Mishra", "Tiwari"
]

# Sample professions
PROFESSIONS = {
    "Educational": [
        "Principal", "Vice Principal", "School Director", "Administrator", "Department Head", 
        "Academic Coordinator", "School Owner", "Trustee", "Education Consultant", "School Relationship Manager"
    ],
    "Industrial": [
        "CEO", "Managing Director", "Plant Manager", "Operations Head", "Production Manager", 
        "Quality Control Manager", "Procurement Manager", "Industrial Engineer", "Maintenance Manager", "R&D Head"
    ],
    "Technology": [
        "CTO", "IT Director", "Software Architect", "Development Manager", "Project Manager", 
        "IT Manager", "System Administrator", "Network Manager", "Security Officer", "Technical Lead"
    ],
    "Healthcare": [
        "Medical Director", "Chief Medical Officer", "Hospital Administrator", "Clinic Manager", "Head Doctor", 
        "Chief of Staff", "Pharmacy Manager", "Lab Director", "Radiology Manager", "Healthcare Consultant"
    ],
    "Retail": [
        "Store Manager", "Retail Director", "Merchandising Manager", "Operations Manager", "Sales Manager", 
        "Category Manager", "Inventory Manager", "Retail Consultant", "Branch Manager", "Department Manager"
    ],
    "Hospitality": [
        "Hotel Manager", "Restaurant Owner", "F&B Manager", "Executive Chef", "Hospitality Director", 
        "Events Manager", "Travel Agency Owner", "Tourism Consultant", "Guest Relations Manager", "Operations Director"
    ],
    "Financial": [
        "Branch Manager", "Financial Advisor", "Insurance Agent", "Investment Consultant", "Accounting Manager", 
        "Tax Consultant", "Wealth Manager", "Financial Planner", "Banking Officer", "Credit Manager"
    ]
}

# Sample product interests based on business type
PRODUCT_INTERESTS = {
    "Educational": ["ELAP", "MDL", "PBL", "ICT", "AI Workshop", "AI tutor", "Simulation", "E2MP", "LMS", "AI software"],
    "Industrial": ["AI software", "E2MP", "Entrepreneurship_Workshop", "Tech Franchise"],
    "Technology": ["AI software", "E2MP software", "LMS", "Tech Franchise", "Entrepreneurship_Workshop"],
    "Healthcare": ["AI software", "E2MP", "Entrepreneurship_Workshop", "Simulation"],
    "Retail": ["AI software", "E2MP", "Entrepreneurship_Workshop", "Digital Marketing Masterclass"],
    "Hospitality": ["AI software", "E2MP", "Entrepreneurship_Workshop", "Digital Marketing Masterclass"],
    "Financial": ["AI software", "E2MP", "Entrepreneurship_Workshop", "Digital Marketing Masterclass"]
}

# Sample lead sources
LEAD_SOURCES = [
    "Website", "Referral", "Cold Call", "Event", "Email Campaign", "Social Media", 
    "Google Ads", "LinkedIn", "Trade Show", "Partner Referral", "Direct Mail", "Webinar"
]

# Sample lead statuses
LEAD_STATUSES = ["New", "Contacted", "Qualified", "Proposal Sent", "Negotiation", "Won", "Lost"]

# Helper functions
def get_all_cities():
    """Get a list of all cities with their states."""
    cities = []
    for state, city_list in INDIAN_STATES_CITIES.items():
        for city in city_list:
            cities.append({"city": city, "state": state})
    return cities

def get_all_business_types():
    """Get a dictionary of all business types and their subcategories."""
    return BUSINESS_TYPES

def get_cities_by_state(state):
    """Get a list of cities for a given state."""
    return INDIAN_STATES_CITIES.get(state, [])

def get_states():
    """Get a list of all states."""
    return list(INDIAN_STATES_CITIES.keys())

def generate_phone_number():
    """Generate a random Indian phone number."""
    return f"+91 {random.randint(7, 9)}{random.randint(100, 999)} {random.randint(100, 999)} {random.randint(100, 999)}"

def generate_email(name, company):
    """Generate an email address based on name and company."""
    name_part = name.lower().replace(" ", ".")
    company_part = company.lower().replace(" ", "").replace("'", "")
    domains = ["gmail.com", "yahoo.com", "outlook.com", "hotmail.com", "company.com"]
    
    # 50% chance to use company domain
    if random.random() > 0.5:
        return f"{name_part}@{company_part}.com"
    else:
        return f"{name_part}@{random.choice(domains)}"

def generate_company_name(business_type, city):
    """Generate a company name based on business type and city."""
    if business_type not in COMPANY_NAME_TEMPLATES:
        business_type = random.choice(list(COMPANY_NAME_TEMPLATES.keys()))
    
    template = random.choice(COMPANY_NAME_TEMPLATES[business_type])
    name_options = ["Royal", "Global", "National", "Premier", "Elite", "Supreme", "Universal", "Imperial", "Prestige", "Excellence"]
    
    return template.format(city=city, name=random.choice(name_options))

def generate_budget(business_type):
    """Generate a budget based on business type."""
    base_budgets = {
        "Educational": (50000, 500000),
        "Industrial": (100000, 1000000),
        "Technology": (75000, 750000),
        "Healthcare": (100000, 1000000),
        "Retail": (50000, 500000),
        "Hospitality": (75000, 750000),
        "Financial": (100000, 1000000)
    }
    
    min_budget, max_budget = base_budgets.get(business_type, (50000, 500000))
    return random.randint(min_budget, max_budget)

def generate_leads_by_city(city, count=5, business_type=None):
    """Generate a list of leads for a specific city."""
    leads = []
    
    # Find the state for this city
    state = None
    for s, cities in INDIAN_STATES_CITIES.items():
        if city in cities:
            state = s
            break
    
    if not state:
        return []
    
    for _ in range(count):
        lead = generate_mock_lead(city=city, state=state, business_type=business_type)
        leads.append(lead)
    
    return leads

def generate_leads_by_business_type(business_type, count=5, city=None, state=None):
    """Generate a list of leads for a specific business type."""
    leads = []
    
    for _ in range(count):
        lead = generate_mock_lead(city=city, state=state, business_type=business_type)
        leads.append(lead)
    
    return leads

def generate_mock_lead(city=None, state=None, business_type=None, subcategory=None):
    """Generate a mock lead with realistic data."""
    # If city is provided but not state, find the state
    if city and not state:
        for s, cities in INDIAN_STATES_CITIES.items():
            if city in cities:
                state = s
                break
    
    # If state is provided but not city, pick a random city from that state
    if state and not city:
        if state in INDIAN_STATES_CITIES:
            city = random.choice(INDIAN_STATES_CITIES[state])
    
    # If neither is provided, pick a random state and city
    if not state and not city:
        state = random.choice(list(INDIAN_STATES_CITIES.keys()))
        city = random.choice(INDIAN_STATES_CITIES[state])
    
    # If business_type is not provided, pick a random one
    if not business_type:
        business_type = random.choice(list(BUSINESS_TYPES.keys()))
    
    # If subcategory is not provided, pick a random one from the business type
    if not subcategory and business_type in BUSINESS_TYPES:
        subcategory = random.choice(BUSINESS_TYPES[business_type])
    
    # Generate company name
    company_name = generate_company_name(business_type, city)
    
    # Generate contact person
    first_name = random.choice(FIRST_NAMES)
    last_name = random.choice(LAST_NAMES)
    contact_person = f"{first_name} {last_name}"
    
    # Generate profession based on business type
    if business_type in PROFESSIONS:
        profession = random.choice(PROFESSIONS[business_type])
    else:
        profession = random.choice(PROFESSIONS["Educational"])
    
    # Generate product interest based on business type
    if business_type in PRODUCT_INTERESTS:
        product_interested = ", ".join(random.sample(PRODUCT_INTERESTS[business_type], 
                                                    k=random.randint(1, min(3, len(PRODUCT_INTERESTS[business_type])))))
    else:
        product_interested = ", ".join(random.sample(PRODUCT_INTERESTS["Educational"], 
                                                    k=random.randint(1, 3)))
    
    # Generate other fields
    phone = generate_phone_number()
    email = generate_email(contact_person, company_name)
    budget = generate_budget(business_type)
    source = random.choice(LEAD_SOURCES)
    status = random.choice(LEAD_STATUSES)
    
    # Generate dates
    today = datetime.now()
    created_date = (today - timedelta(days=random.randint(1, 60))).strftime("%Y-%m-%d %H:%M:%S")
    
    # 70% chance to have been contacted
    if random.random() < 0.7:
        last_contacted = (today - timedelta(days=random.randint(0, 30))).strftime("%Y-%m-%d %H:%M:%S")
    else:
        last_contacted = None
    
    # Create the lead object
    lead = {
        "id": str(uuid.uuid4()),
        "name": company_name,
        "contact_person": contact_person,
        "profession": profession,
        "email": email,
        "phone": phone,
        "city": city,
        "state": state,
        "location": f"{city}, {state}",
        "business_type": business_type,
        "business_subcategory": subcategory,
        "product_interested": product_interested,
        "budget": budget,
        "source": source,
        "source_detail": f"Generated from {source}",
        "status": status,
        "created_date": created_date,
        "last_contacted": last_contacted,
        "notes": f"This lead is interested in {product_interested} for their {business_type.lower()} business.",
        "score": random.randint(1, 100),
        "tags": []
    }
    
    return lead

def fetch_leads_from_external_source(city=None, state=None, business_type=None, count=10):
    """Simulate fetching leads from an external source."""
    # In a real application, this would connect to an API or database
    # For this demo, we'll generate mock leads
    
    leads = []
    
    for _ in range(count):
        lead = generate_mock_lead(city=city, state=state, business_type=business_type)
        leads.append(lead)
    
    return leads

# Test function
if __name__ == "__main__":
    print("This module provides data about Indian cities and businesses for the EduRishi Sales Assistant.")