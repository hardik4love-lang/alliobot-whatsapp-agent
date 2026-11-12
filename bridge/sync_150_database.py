import asyncio
import asyncpg
import json
import sqlite3
import os

DATABASE_URL = "postgresql://neondb_owner:npg_e6iVuZDU3IqL@ep-falling-tree-b5b8mc8n-pooler.c-7.us-east-2.aws.neon.tech/neondb"

# All 150 prospects categorized and sorted across 6 clusters
ALL_150_PROSPECTS = [
    # Cluster 1: Jahangirpura Core & Surat-Olpad Road (1-25)
    {
        "cluster_code": "CLUSTER_1_JAHANGIRPURA",
        "cluster_name": "Jahangirpura Core",
        "business_name": "Vishala Restaurant & Garden",
        "cuisine_type": "Kathiyawadi & Punjabi",
        "phone_e164": "+919925626960",
        "surat_suburb": "Jahangirpura",
        "full_address": "Opp. Raj Green Heights, Olpad Road, Jahangirpura, Surat",
        "priority_rank": 1
    },
    {
        "cluster_code": "CLUSTER_1_JAHANGIRPURA",
        "cluster_name": "Jahangirpura Core",
        "business_name": "Shree Khodiyar Kathiyawadi Dhaba",
        "cuisine_type": "Kathiyawadi / Dhaba",
        "phone_e164": "+919714322290",
        "surat_suburb": "Jahangirpura",
        "full_address": "5 Square Point, M.V. Circle, Near Anjani Party Plot, Jahangirpura, Surat",
        "priority_rank": 2
    },
    {
        "cluster_code": "CLUSTER_1_JAHANGIRPURA",
        "cluster_name": "Jahangirpura Core",
        "business_name": "Maa Matelwali Kathiyawadi Restaurant",
        "cuisine_type": "Kathiyawadi / Daily Thali",
        "phone_e164": "+919601904819",
        "surat_suburb": "Jahangirpura",
        "full_address": "Plot No. 24, Olpad Road, Opp. Exiito Commercial Hub, Jahangirpura, Surat",
        "priority_rank": 3
    },
    {
        "cluster_code": "CLUSTER_1_JAHANGIRPURA",
        "cluster_name": "Jahangirpura Core",
        "business_name": "Jay Somnath Kathiyawadi Bhojnalaya",
        "cuisine_type": "Kathiyawadi / Gujarati",
        "phone_e164": "+919723045678",
        "surat_suburb": "Jahangirpura",
        "full_address": "Near Galaxy Enclave, Jahangirpura, Surat",
        "priority_rank": 4
    },
    {
        "cluster_code": "CLUSTER_1_JAHANGIRPURA",
        "cluster_name": "Jahangirpura Core",
        "business_name": "Chamunda Kathiyawadi Dhaba",
        "cuisine_type": "Desi Dhaba / Bajra Roti",
        "phone_e164": "+919879211234",
        "surat_suburb": "Jahangirpura",
        "full_address": "Opp. Shreedhar Residency, Olpad Road, Jahangirpura, Surat",
        "priority_rank": 5
    },
    {
        "cluster_code": "CLUSTER_1_JAHANGIRPURA",
        "cluster_name": "Jahangirpura Core",
        "business_name": "Nilam Dhaba Jahangirpura",
        "cuisine_type": "Dhaba / Kathiyawadi",
        "phone_e164": "+919825114455",
        "surat_suburb": "Jahangirpura",
        "full_address": "Near Nayara Petrol Pump, Olpad Road, Jahangirpura, Surat",
        "priority_rank": 6
    },
    {
        "cluster_code": "CLUSTER_1_JAHANGIRPURA",
        "cluster_name": "Jahangirpura Core",
        "business_name": "Radhe Dining Hall & Kathiyawadi",
        "cuisine_type": "Kathiyawadi Thali",
        "phone_e164": "+919909987654",
        "surat_suburb": "Jahangirpura",
        "full_address": "Iscon Circle Corner, Jahangirpura, Surat",
        "priority_rank": 7
    },
    {
        "cluster_code": "CLUSTER_1_JAHANGIRPURA",
        "cluster_name": "Jahangirpura Core",
        "business_name": "Bhavna Tiffin Service & Cloud Kitchen",
        "cuisine_type": "Tiffin Service / Cloud Kitchen",
        "phone_e164": "+918511270660",
        "surat_suburb": "Jahangirpura",
        "full_address": "H-302, Saipujan Society, Near Ranchhod Park, Jahangirpura, Surat",
        "priority_rank": 8
    },
    {
        "cluster_code": "CLUSTER_1_JAHANGIRPURA",
        "cluster_name": "Jahangirpura Core",
        "business_name": "Concord Restaurant & Banquet",
        "cuisine_type": "Multicuisine & Banquets",
        "phone_e164": "+917779021440",
        "surat_suburb": "Jahangirpura",
        "full_address": "Palanpur Canal Road, Near Morabhagal, Jahangirpura, Surat",
        "priority_rank": 9
    },
    {
        "cluster_code": "CLUSTER_1_JAHANGIRPURA",
        "cluster_name": "Jahangirpura Core",
        "business_name": "Concord Kitchen Desk",
        "cuisine_type": "Multicuisine Foodservice",
        "phone_e164": "+917779049429",
        "surat_suburb": "Jahangirpura",
        "full_address": "Palanpur Canal Road, Jahangirpura, Surat",
        "priority_rank": 10
    },
    {
        "cluster_code": "CLUSTER_1_JAHANGIRPURA",
        "cluster_name": "Jahangirpura Core",
        "business_name": "Keshav Restaurant",
        "cuisine_type": "North Indian & Gujarati",
        "phone_e164": "+918734880106",
        "surat_suburb": "Jahangirpura",
        "full_address": "Near Nandanvan Row House, Olpad Road, Jahangirpura, Surat",
        "priority_rank": 11
    },
    {
        "cluster_code": "CLUSTER_1_JAHANGIRPURA",
        "cluster_name": "Jahangirpura Core",
        "business_name": "Superia Restaurant & Kitchen",
        "cuisine_type": "Multicuisine & Punjabi",
        "phone_e164": "+919879502211",
        "surat_suburb": "Jahangirpura",
        "full_address": "Exiito Commercial Hub, Olpad-Jahangirpura Main Road, Surat",
        "priority_rank": 12
    },
    {
        "cluster_code": "CLUSTER_1_JAHANGIRPURA",
        "cluster_name": "Jahangirpura Core",
        "business_name": "Tasty Restaurant & Food Court",
        "cuisine_type": "North Indian & Chinese",
        "phone_e164": "+919904128009",
        "surat_suburb": "Jahangirpura",
        "full_address": "Shubham Complex, Jahangirpura-Olpad Road, Surat",
        "priority_rank": 13
    },
    {
        "cluster_code": "CLUSTER_1_JAHANGIRPURA",
        "cluster_name": "Jahangirpura Core",
        "business_name": "Megh Malhar Dhosa & Fast Food",
        "cuisine_type": "South Indian & Fast Food",
        "phone_e164": "+918000862961",
        "surat_suburb": "Jahangirpura",
        "full_address": "91 Shreedhar Society, Olpad Road, Beside Sagar Dairy, Jahangirpura, Surat",
        "priority_rank": 14
    },
    {
        "cluster_code": "CLUSTER_1_JAHANGIRPURA",
        "cluster_name": "Jahangirpura Core",
        "business_name": "Sagar Fast Food & Live Dosa",
        "cuisine_type": "Fast Food & South Indian",
        "phone_e164": "+919825877665",
        "surat_suburb": "Jahangirpura",
        "full_address": "Beside Sagar Dairy, Olpad Road, Jahangirpura, Surat",
        "priority_rank": 15
    },
    {
        "cluster_code": "CLUSTER_1_JAHANGIRPURA",
        "cluster_name": "Jahangirpura Core",
        "business_name": "Roshni Fast Food & Snacks",
        "cuisine_type": "Fast Food & Quick Bites",
        "phone_e164": "+918866689777",
        "surat_suburb": "Jahangirpura",
        "full_address": "Opp. Essar Petrol Pump, Jahangirpura, Surat",
        "priority_rank": 16
    },
    {
        "cluster_code": "CLUSTER_1_JAHANGIRPURA",
        "cluster_name": "Jahangirpura Core",
        "business_name": "Street Food Lab",
        "cuisine_type": "Fast Food & Chaat",
        "phone_e164": "+919265920655",
        "surat_suburb": "Jahangirpura",
        "full_address": "G5, Blu Eminence, Dandi Road, Opp. Sangini Gardenia, Jahangirpura, Surat",
        "priority_rank": 17
    },
    {
        "cluster_code": "CLUSTER_1_JAHANGIRPURA",
        "cluster_name": "Jahangirpura Core",
        "business_name": "Ajay's Cafe Iscon Circle",
        "cuisine_type": "Burgers & Fast Food",
        "phone_e164": "+919427071622",
        "surat_suburb": "Jahangirpura",
        "full_address": "12, Mahendra Park Complex, Near Iscon Circle, Jahangirpura, Surat",
        "priority_rank": 18
    },
    {
        "cluster_code": "CLUSTER_1_JAHANGIRPURA",
        "cluster_name": "Jahangirpura Core",
        "business_name": "Ajay's Cafe Jahangirpura Counter",
        "cuisine_type": "Fast Food & Shakes",
        "phone_e164": "+917490878037",
        "surat_suburb": "Jahangirpura",
        "full_address": "Mahendra Park Complex, Jahangirpura, Surat",
        "priority_rank": 19
    },
    {
        "cluster_code": "CLUSTER_1_JAHANGIRPURA",
        "cluster_name": "Jahangirpura Core",
        "business_name": "Breadliner Savory Kitchen",
        "cuisine_type": "Bakery & Savory Prep",
        "phone_e164": "+919925417000",
        "surat_suburb": "Jahangirpura",
        "full_address": "G1-G2 Satyadev Plaza, Iscon Circle, Opp. Jahangirpura Jin, Jahangirpura, Surat",
        "priority_rank": 20
    },
    {
        "cluster_code": "CLUSTER_1_JAHANGIRPURA",
        "cluster_name": "Jahangirpura Core",
        "business_name": "La Pino'z Pizza Jahangirpura",
        "cuisine_type": "Pizza & Pasta Kitchen",
        "phone_e164": "+918758754004",
        "surat_suburb": "Jahangirpura",
        "full_address": "Anjani Icon, Chaitrali Road, Jahangirpura, Surat",
        "priority_rank": 21
    },
    {
        "cluster_code": "CLUSTER_1_JAHANGIRPURA",
        "cluster_name": "Jahangirpura Core",
        "business_name": "Helios Pizza Jahangirpura",
        "cuisine_type": "Pizzeria & Fast Food",
        "phone_e164": "+919898413321",
        "surat_suburb": "Jahangirpura",
        "full_address": "Near Cinezza, Dandi Road, Dahin Nagar, Jahangirpura, Surat",
        "priority_rank": 22
    },
    {
        "cluster_code": "CLUSTER_1_JAHANGIRPURA",
        "cluster_name": "Jahangirpura Core",
        "business_name": "Helios Pizza Kitchen",
        "cuisine_type": "Pizzeria Kitchen",
        "phone_e164": "+917600678282",
        "surat_suburb": "Jahangirpura",
        "full_address": "Dandi Road, Jahangirpura, Surat",
        "priority_rank": 23
    },
    {
        "cluster_code": "CLUSTER_1_JAHANGIRPURA",
        "cluster_name": "Jahangirpura Core",
        "business_name": "The D Pizza Morabhagal",
        "cuisine_type": "Fast Food & Pizza",
        "phone_e164": "+916353446969",
        "surat_suburb": "Jahangirpura",
        "full_address": "Shop 1, Blue Eminence, Morabhagal Circle, Jahangirpura, Surat",
        "priority_rank": 24
    },
    {
        "cluster_code": "CLUSTER_1_JAHANGIRPURA",
        "cluster_name": "Jahangirpura Core",
        "business_name": "Madhi Ni Khamni Jahangirpura",
        "cuisine_type": "Gujarati Farsan & Savory",
        "phone_e164": "+919824501704",
        "surat_suburb": "Jahangirpura",
        "full_address": "B-1, Mahendra Park, Opp. Essar Gas Station, Olpad Road, Jahangirpura, Surat",
        "priority_rank": 25
    },

    # Cluster 2: Jahangirabad & Ugat Canal Road Corridor (26-50)
    {
        "cluster_code": "CLUSTER_2_JAHANGIRABAD",
        "cluster_name": "Jahangirabad & Canal Rd",
        "business_name": "Krishna Kathiyawadi Dhaba",
        "cuisine_type": "Kathiyawadi & Sev Tameta",
        "phone_e164": "+919879033445",
        "surat_suburb": "Jahangirabad",
        "full_address": "Near DMart, Canal Road, Jahangirabad, Surat",
        "priority_rank": 26
    },
    {
        "cluster_code": "CLUSTER_2_JAHANGIRABAD",
        "cluster_name": "Jahangirabad & Canal Rd",
        "business_name": "Shiv Shakti Kathiyawadi Kitchen",
        "cuisine_type": "Dhaba / Kathiyawadi",
        "phone_e164": "+919825612349",
        "surat_suburb": "Jahangirabad",
        "full_address": "Ugat Canal Cross Road, Jahangirabad, Surat",
        "priority_rank": 27
    },
    {
        "cluster_code": "CLUSTER_2_JAHANGIRABAD",
        "cluster_name": "Jahangirabad & Canal Rd",
        "business_name": "Bapa Sitaram Bhojanalaya",
        "cuisine_type": "Kathiyawadi Thali",
        "phone_e164": "+919825433221",
        "surat_suburb": "Jahangirabad",
        "full_address": "Near Vikalp Hospital, Jahangirabad, Surat",
        "priority_rank": 28
    },
    {
        "cluster_code": "CLUSTER_2_JAHANGIRABAD",
        "cluster_name": "Jahangirabad & Canal Rd",
        "business_name": "Rajdhani Dal Bati Center",
        "cuisine_type": "Rajasthani Dal Bati",
        "phone_e164": "+919825344556",
        "surat_suburb": "Jahangirabad",
        "full_address": "Near Ugat Overbridge, Jahangirabad, Surat",
        "priority_rank": 29
    },
    {
        "cluster_code": "CLUSTER_2_JAHANGIRABAD",
        "cluster_name": "Jahangirabad & Canal Rd",
        "business_name": "Khodiyar Parotha Center",
        "cuisine_type": "Desi Parotha Shak",
        "phone_e164": "+919898022334",
        "surat_suburb": "Jahangirabad",
        "full_address": "Times Galaxy Ground Floor, Jahangirabad, Surat",
        "priority_rank": 30
    },
    {
        "cluster_code": "CLUSTER_2_JAHANGIRABAD",
        "cluster_name": "Jahangirabad & Canal Rd",
        "business_name": "Jalaram Parotha House",
        "cuisine_type": "Gujarati Parotha & Shak",
        "phone_e164": "+919898711223",
        "surat_suburb": "Jahangirabad",
        "full_address": "Nakshatra Galaxy, Canal Road, Jahangirabad, Surat",
        "priority_rank": 31
    },
    {
        "cluster_code": "CLUSTER_2_JAHANGIRABAD",
        "cluster_name": "Jahangirabad & Canal Rd",
        "business_name": "Jay Khodiyar Tiffin Center",
        "cuisine_type": "Gujarati Home Meals",
        "phone_e164": "+919925088776",
        "surat_suburb": "Jahangirabad",
        "full_address": "Nakshatra Nebula, Canal Road, Jahangirabad, Surat",
        "priority_rank": 32
    },
    {
        "cluster_code": "CLUSTER_2_JAHANGIRABAD",
        "cluster_name": "Jahangirabad & Canal Rd",
        "business_name": "Annapurna Tiffin & Cloud Kitchen",
        "cuisine_type": "Tiffin & Home Kitchen",
        "phone_e164": "+919898243120",
        "surat_suburb": "Jahangirabad",
        "full_address": "Variyav Junction belt, Jahangirabad, Surat",
        "priority_rank": 33
    },
    {
        "cluster_code": "CLUSTER_2_JAHANGIRABAD",
        "cluster_name": "Jahangirabad & Canal Rd",
        "business_name": "Shri Mahavir Tiffin Service",
        "cuisine_type": "Pure Veg / Jain Tiffin",
        "phone_e164": "+919824166554",
        "surat_suburb": "Jahangirabad",
        "full_address": "Times Galaxy Commercial, Jahangirabad, Surat",
        "priority_rank": 34
    },
    {
        "cluster_code": "CLUSTER_2_JAHANGIRABAD",
        "cluster_name": "Jahangirabad & Canal Rd",
        "business_name": "Shree Ram Tiffin Service",
        "cuisine_type": "Daily Tiffin & Lunch Box",
        "phone_e164": "+919924577889",
        "surat_suburb": "Jahangirabad",
        "full_address": "Near Green City Circle, Jahangirabad, Surat",
        "priority_rank": 35
    },
    {
        "cluster_code": "CLUSTER_2_JAHANGIRABAD",
        "cluster_name": "Jahangirabad & Canal Rd",
        "business_name": "Pooja Pure Veg Cloud Kitchen",
        "cuisine_type": "Home Food / North Indian",
        "phone_e164": "+919825711990",
        "surat_suburb": "Jahangirabad",
        "full_address": "Times Plaza, Ugat Canal Road, Jahangirabad, Surat",
        "priority_rank": 36
    },
    {
        "cluster_code": "CLUSTER_2_JAHANGIRABAD",
        "cluster_name": "Jahangirabad & Canal Rd",
        "business_name": "Radhika Pure Veg Restaurant",
        "cuisine_type": "Punjabi & Gujarati",
        "phone_e164": "+919904455667",
        "surat_suburb": "Jahangirabad",
        "full_address": "Near Green City, Jahangirabad, Surat",
        "priority_rank": 37
    },
    {
        "cluster_code": "CLUSTER_2_JAHANGIRABAD",
        "cluster_name": "Jahangirabad & Canal Rd",
        "business_name": "Tulsi Dining Hall",
        "cuisine_type": "Pure Veg Gujarati Meals",
        "phone_e164": "+919825266778",
        "surat_suburb": "Jahangirabad",
        "full_address": "Times Corner, Jahangirabad, Surat",
        "priority_rank": 38
    },
    {
        "cluster_code": "CLUSTER_2_JAHANGIRABAD",
        "cluster_name": "Jahangirabad & Canal Rd",
        "business_name": "Jay Bajrang Dhaba",
        "cuisine_type": "Punjabi / Dal Fry Tandoor",
        "phone_e164": "+919879655443",
        "surat_suburb": "Jahangirabad",
        "full_address": "Near Botanical Garden Road, Jahangirabad, Surat",
        "priority_rank": 39
    },
    {
        "cluster_code": "CLUSTER_2_JAHANGIRABAD",
        "cluster_name": "Jahangirabad & Canal Rd",
        "business_name": "Ajay's Cafe Jahangirabad Canal",
        "cuisine_type": "Fast Food & Burgers",
        "phone_e164": "+919724355919",
        "surat_suburb": "Jahangirabad",
        "full_address": "G-30, Times Galaxy, Near DMart, Canal Road, Jahangirabad, Surat",
        "priority_rank": 40
    },
    {
        "cluster_code": "CLUSTER_2_JAHANGIRABAD",
        "cluster_name": "Jahangirabad & Canal Rd",
        "business_name": "Zidaan's Food Corner",
        "cuisine_type": "Chinese & Fast Food",
        "phone_e164": "+919898155442",
        "surat_suburb": "Jahangirabad",
        "full_address": "Near Vikalp Hospital, Ugat Canal Road, Jahangirabad, Surat",
        "priority_rank": 41
    },
    {
        "cluster_code": "CLUSTER_2_JAHANGIRABAD",
        "cluster_name": "Jahangirabad & Canal Rd",
        "business_name": "Taitoon Chinese Corner",
        "cuisine_type": "Indo-Chinese & Rolls",
        "phone_e164": "+919712399881",
        "surat_suburb": "Jahangirabad",
        "full_address": "Ugat Canal Road, Jahangirabad, Surat",
        "priority_rank": 42
    },
    {
        "cluster_code": "CLUSTER_2_JAHANGIRABAD",
        "cluster_name": "Jahangirabad & Canal Rd",
        "business_name": "Balaji Chinese & Fast Food",
        "cuisine_type": "Manchurian & Fried Rice",
        "phone_e164": "+919824899001",
        "surat_suburb": "Jahangirabad",
        "full_address": "Canal Walk, Jahangirabad, Surat",
        "priority_rank": 43
    },
    {
        "cluster_code": "CLUSTER_2_JAHANGIRABAD",
        "cluster_name": "Jahangirabad & Canal Rd",
        "business_name": "Ugat Fast Food & Chinese Hub",
        "cuisine_type": "Fast Food / Noodles",
        "phone_e164": "+919879822114",
        "surat_suburb": "Jahangirabad",
        "full_address": "Opp. Fire Station, Ugat Canal Road, Jahangirabad, Surat",
        "priority_rank": 44
    },
    {
        "cluster_code": "CLUSTER_2_JAHANGIRABAD",
        "cluster_name": "Jahangirabad & Canal Rd",
        "business_name": "Shreeji Dosa & Chinese",
        "cuisine_type": "South Indian & Chinese",
        "phone_e164": "+919825944332",
        "surat_suburb": "Jahangirabad",
        "full_address": "Near Raj Harmony, Canal Road, Jahangirabad, Surat",
        "priority_rank": 45
    },
    {
        "cluster_code": "CLUSTER_2_JAHANGIRABAD",
        "cluster_name": "Jahangirabad & Canal Rd",
        "business_name": "Honest Pav Bhaji & Pulao (Cloud)",
        "cuisine_type": "Fast Food / Pav Bhaji",
        "phone_e164": "+919909233445",
        "surat_suburb": "Jahangirabad",
        "full_address": "Nakshatra Solitaire, Canal Road, Jahangirabad, Surat",
        "priority_rank": 46
    },
    {
        "cluster_code": "CLUSTER_2_JAHANGIRABAD",
        "cluster_name": "Jahangirabad & Canal Rd",
        "business_name": "Maruti Fast Food & Vadapav",
        "cuisine_type": "Street Snacks & Vadapav",
        "phone_e164": "+919913144556",
        "surat_suburb": "Jahangirabad",
        "full_address": "Near DMart Gate, Jahangirabad, Surat",
        "priority_rank": 47
    },
    {
        "cluster_code": "CLUSTER_2_JAHANGIRABAD",
        "cluster_name": "Jahangirabad & Canal Rd",
        "business_name": "Siddhi Fast Food Corner",
        "cuisine_type": "Sandwiches & Shakes",
        "phone_e164": "+919879166554",
        "surat_suburb": "Jahangirabad",
        "full_address": "Times Square, Canal Road, Jahangirabad, Surat",
        "priority_rank": 48
    },
    {
        "cluster_code": "CLUSTER_2_JAHANGIRABAD",
        "cluster_name": "Jahangirabad & Canal Rd",
        "business_name": "Kismat Tawa Fry & Chinese",
        "cuisine_type": "Tawa Non-Veg & Chinese",
        "phone_e164": "+919727788990",
        "surat_suburb": "Jahangirabad",
        "full_address": "Ugat Corner, Jahangirabad, Surat",
        "priority_rank": 49
    },
    {
        "cluster_code": "CLUSTER_2_JAHANGIRABAD",
        "cluster_name": "Jahangirabad & Canal Rd",
        "business_name": "Royal Biryani & Mughlai (Cloud)",
        "cuisine_type": "Biryani & Tawa Special",
        "phone_e164": "+919712044556",
        "surat_suburb": "Jahangirabad",
        "full_address": "Opp. Nakshatra Nebula, Jahangirabad, Surat",
        "priority_rank": 50
    },

    # Cluster 3: Morabhagal & Dandi Road Sector (51-75)
    {
        "cluster_code": "CLUSTER_3_MORABHAGAL",
        "cluster_name": "Morabhagal & Dandi Rd",
        "business_name": "Morabhagal Kathiyawadi Dhaba",
        "cuisine_type": "Desi Kathiyawadi",
        "phone_e164": "+919825088123",
        "surat_suburb": "Morabhagal",
        "full_address": "Near Morabhagal Char Rasta, Dandi Road, Surat",
        "priority_rank": 51
    },
    {
        "cluster_code": "CLUSTER_3_MORABHAGAL",
        "cluster_name": "Morabhagal & Dandi Rd",
        "business_name": "Bapa Sitaram Kathiyawadi Dhaba",
        "cuisine_type": "Kathiyawadi / Ringna Olo",
        "phone_e164": "+919723188994",
        "surat_suburb": "Morabhagal",
        "full_address": "Dandi Road, Near Tapi Riverfront, Morabhagal, Surat",
        "priority_rank": 52
    },
    {
        "cluster_code": "CLUSTER_3_MORABHAGAL",
        "cluster_name": "Morabhagal & Dandi Rd",
        "business_name": "Jay Ambe Dal Bati Dhaba",
        "cuisine_type": "Dal Bati / Gatte ki Sabzi",
        "phone_e164": "+919879433221",
        "surat_suburb": "Morabhagal",
        "full_address": "Morabhagal Toll Road Corner, Surat",
        "priority_rank": 53
    },
    {
        "cluster_code": "CLUSTER_3_MORABHAGAL",
        "cluster_name": "Morabhagal & Dandi Rd",
        "business_name": "Chamunda Parotha House",
        "cuisine_type": "Parotha / Sev Usal",
        "phone_e164": "+919824688771",
        "surat_suburb": "Morabhagal",
        "full_address": "Dandi Road, Morabhagal, Surat",
        "priority_rank": 54
    },
    {
        "cluster_code": "CLUSTER_3_MORABHAGAL",
        "cluster_name": "Morabhagal & Dandi Rd",
        "business_name": "Radhe Krishna Bhojanalaya",
        "cuisine_type": "Gujarati / Dal Bhaat Shak",
        "phone_e164": "+919825544882",
        "surat_suburb": "Morabhagal",
        "full_address": "Dahin Nagar Main Road, Morabhagal, Surat",
        "priority_rank": 55
    },
    {
        "cluster_code": "CLUSTER_3_MORABHAGAL",
        "cluster_name": "Morabhagal & Dandi Rd",
        "business_name": "Gujarat Dining Hall",
        "cuisine_type": "Unlimited Gujarati Thali",
        "phone_e164": "+919909022339",
        "surat_suburb": "Morabhagal",
        "full_address": "Near Morabhagal BRTS Stand, Surat",
        "priority_rank": 56
    },
    {
        "cluster_code": "CLUSTER_3_MORABHAGAL",
        "cluster_name": "Morabhagal & Dandi Rd",
        "business_name": "Bhagwati Dhaba & Dining",
        "cuisine_type": "Punjabi & Kathiyawadi",
        "phone_e164": "+919879911228",
        "surat_suburb": "Morabhagal",
        "full_address": "Dandi Heritage Road, Morabhagal, Surat",
        "priority_rank": 57
    },
    {
        "cluster_code": "CLUSTER_3_MORABHAGAL",
        "cluster_name": "Morabhagal & Dandi Rd",
        "business_name": "Taste of Punjab Dhaba",
        "cuisine_type": "Punjabi / Paneer Gravies",
        "phone_e164": "+919825811442",
        "surat_suburb": "Morabhagal",
        "full_address": "Near Morabhagal Overbridge, Surat",
        "priority_rank": 58
    },
    {
        "cluster_code": "CLUSTER_3_MORABHAGAL",
        "cluster_name": "Morabhagal & Dandi Rd",
        "business_name": "Dandi Tawa & Non-Veg Center",
        "cuisine_type": "Mughlai / Tawa Gravy",
        "phone_e164": "+919898277665",
        "surat_suburb": "Morabhagal",
        "full_address": "Near Tapi Causeway, Morabhagal, Surat",
        "priority_rank": 59
    },
    {
        "cluster_code": "CLUSTER_3_MORABHAGAL",
        "cluster_name": "Morabhagal & Dandi Rd",
        "business_name": "Zamzam Mughlai & Chinese",
        "cuisine_type": "Tawa Fry / Chinese",
        "phone_e164": "+919712844332",
        "surat_suburb": "Morabhagal",
        "full_address": "Near Causeway Bridge Approach, Morabhagal, Surat",
        "priority_rank": 60
    },
    {
        "cluster_code": "CLUSTER_3_MORABHAGAL",
        "cluster_name": "Morabhagal & Dandi Rd",
        "business_name": "Al-Rehman Biryani House",
        "cuisine_type": "Dum Biryani & Kebabs",
        "phone_e164": "+919723566778",
        "surat_suburb": "Morabhagal",
        "full_address": "Near Morabhagal Masjid Road, Surat",
        "priority_rank": 61
    },
    {
        "cluster_code": "CLUSTER_3_MORABHAGAL",
        "cluster_name": "Morabhagal & Dandi Rd",
        "business_name": "Ganesh Omelette & Non-Veg",
        "cuisine_type": "Egg Special & Tawa",
        "phone_e164": "+919825499008",
        "surat_suburb": "Morabhagal",
        "full_address": "Near Causeway Road Corner, Morabhagal, Surat",
        "priority_rank": 62
    },
    {
        "cluster_code": "CLUSTER_3_MORABHAGAL",
        "cluster_name": "Morabhagal & Dandi Rd",
        "business_name": "Jay Bhavani Vadapav & Fast Food",
        "cuisine_type": "Quick Snacks & Vadapav",
        "phone_e164": "+917575805500",
        "surat_suburb": "Morabhagal",
        "full_address": "Devshree Benito, Near Surbhi Marble, Morabhagal, Surat",
        "priority_rank": 63
    },
    {
        "cluster_code": "CLUSTER_3_MORABHAGAL",
        "cluster_name": "Morabhagal & Dandi Rd",
        "business_name": "Shreeji Pav Bhaji & Chinese",
        "cuisine_type": "Pav Bhaji & Pulao",
        "phone_e164": "+919824233441",
        "surat_suburb": "Morabhagal",
        "full_address": "Doctor Park Road, Morabhagal, Surat",
        "priority_rank": 64
    },
    {
        "cluster_code": "CLUSTER_3_MORABHAGAL",
        "cluster_name": "Morabhagal & Dandi Rd",
        "business_name": "Kaka Ni Bhaji Pav",
        "cuisine_type": "Surat Famous Pav Bhaji",
        "phone_e164": "+919825166550",
        "surat_suburb": "Morabhagal",
        "full_address": "Morabhagal Main Bazar, Surat",
        "priority_rank": 65
    },
    {
        "cluster_code": "CLUSTER_3_MORABHAGAL",
        "cluster_name": "Morabhagal & Dandi Rd",
        "business_name": "Sardar Fast Food & Pav Bhaji",
        "cuisine_type": "Pav Bhaji / Pulao",
        "phone_e164": "+919898455661",
        "surat_suburb": "Morabhagal",
        "full_address": "Opp. Blue Eminence, Dandi Road, Morabhagal, Surat",
        "priority_rank": 66
    },
    {
        "cluster_code": "CLUSTER_3_MORABHAGAL",
        "cluster_name": "Morabhagal & Dandi Rd",
        "business_name": "Shivam Fast Food & Frankie",
        "cuisine_type": "Street Food & Rolls",
        "phone_e164": "+919904011992",
        "surat_suburb": "Morabhagal",
        "full_address": "Near Morabhagal Circle, Surat",
        "priority_rank": 67
    },
    {
        "cluster_code": "CLUSTER_3_MORABHAGAL",
        "cluster_name": "Morabhagal & Dandi Rd",
        "business_name": "Chopati Fast Food Corner",
        "cuisine_type": "Bhel / Sev Puri / Snacks",
        "phone_e164": "+919925177884",
        "surat_suburb": "Morabhagal",
        "full_address": "Dandi Road, Dahin Nagar, Morabhagal, Surat",
        "priority_rank": 68
    },
    {
        "cluster_code": "CLUSTER_3_MORABHAGAL",
        "cluster_name": "Morabhagal & Dandi Rd",
        "business_name": "Shree Khodiyar Dosa Center",
        "cuisine_type": "South Indian Dosa / Uttapam",
        "phone_e164": "+919879099884",
        "surat_suburb": "Morabhagal",
        "full_address": "Near Surbhi Marble, Dandi Road, Morabhagal, Surat",
        "priority_rank": 69
    },
    {
        "cluster_code": "CLUSTER_3_MORABHAGAL",
        "cluster_name": "Morabhagal & Dandi Rd",
        "business_name": "Mahalaxmi Dosa Center",
        "cuisine_type": "Live Butter Dosa",
        "phone_e164": "+919904733441",
        "surat_suburb": "Morabhagal",
        "full_address": "Dahin Nagar Market, Morabhagal, Surat",
        "priority_rank": 70
    },
    {
        "cluster_code": "CLUSTER_3_MORABHAGAL",
        "cluster_name": "Morabhagal & Dandi Rd",
        "business_name": "Welcome Chinese & Soup Center",
        "cuisine_type": "Indo-Chinese & Soups",
        "phone_e164": "+919898933442",
        "surat_suburb": "Morabhagal",
        "full_address": "Dahin Nagar Cross Road, Morabhagal, Surat",
        "priority_rank": 71
    },
    {
        "cluster_code": "CLUSTER_3_MORABHAGAL",
        "cluster_name": "Morabhagal & Dandi Rd",
        "business_name": "Kolkata Roll & Frankie Corner",
        "cuisine_type": "Rolls / Frankies / Wraps",
        "phone_e164": "+919898677112",
        "surat_suburb": "Morabhagal",
        "full_address": "Opp. Cinezza Multiplex Road, Morabhagal, Surat",
        "priority_rank": 72
    },
    {
        "cluster_code": "CLUSTER_3_MORABHAGAL",
        "cluster_name": "Morabhagal & Dandi Rd",
        "business_name": "Patel Khaman & Fast Food",
        "cuisine_type": "Surat Farsan & Locho",
        "phone_e164": "+919924255663",
        "surat_suburb": "Morabhagal",
        "full_address": "Morabhagal Circle Corner, Surat",
        "priority_rank": 73
    },
    {
        "cluster_code": "CLUSTER_3_MORABHAGAL",
        "cluster_name": "Morabhagal & Dandi Rd",
        "business_name": "The D Pizza Morabhagal Circle",
        "cuisine_type": "Pizza / Italian",
        "phone_e164": "+916353446960",
        "surat_suburb": "Morabhagal",
        "full_address": "Blue Eminence, Dandi Road, Morabhagal, Surat",
        "priority_rank": 74
    },
    {
        "cluster_code": "CLUSTER_3_MORABHAGAL",
        "cluster_name": "Morabhagal & Dandi Rd",
        "business_name": "Street Food Lab Dahin Nagar",
        "cuisine_type": "Chaat & Burgers",
        "phone_e164": "+919265920650",
        "surat_suburb": "Morabhagal",
        "full_address": "Blu Eminence, Opp. Sangini Gardenia, Surat",
        "priority_rank": 75
    },

    # Cluster 4: Rander & Palanpur Canal Road Belt (76-100)
    {
        "cluster_code": "CLUSTER_4_RANDER_PALANPUR",
        "cluster_name": "Rander & Palanpur",
        "business_name": "Jalaram Khichdi & Kathiyawadi",
        "cuisine_type": "Kathiyawadi / Kadhi Khichdi",
        "phone_e164": "+919825822337",
        "surat_suburb": "Rander",
        "full_address": "Palanpur Canal Walkway, Rander, Surat",
        "priority_rank": 76
    },
    {
        "cluster_code": "CLUSTER_4_RANDER_PALANPUR",
        "cluster_name": "Rander & Palanpur",
        "business_name": "Radhey Pure Veg Bhojnalaya",
        "cuisine_type": "Home Thali / Kathiyawadi",
        "phone_e164": "+919712933441",
        "surat_suburb": "Rander",
        "full_address": "Palanpur Patiya, Rander, Surat",
        "priority_rank": 77
    },
    {
        "cluster_code": "CLUSTER_4_RANDER_PALANPUR",
        "cluster_name": "Rander & Palanpur",
        "business_name": "Jay Khodiyar Parotha House",
        "cuisine_type": "Desi Kathiyawadi Parotha",
        "phone_e164": "+919904166554",
        "surat_suburb": "Rander",
        "full_address": "Palanpur Canal Corner, Rander, Surat",
        "priority_rank": 78
    },
    {
        "cluster_code": "CLUSTER_4_RANDER_PALANPUR",
        "cluster_name": "Rander & Palanpur",
        "business_name": "Purohit Dining Hall",
        "cuisine_type": "Rajasthani / Gujarati Thali",
        "phone_e164": "+919879122883",
        "surat_suburb": "Rander",
        "full_address": "Near Ramnagar, Rander Road, Surat",
        "priority_rank": 79
    },
    {
        "cluster_code": "CLUSTER_4_RANDER_PALANPUR",
        "cluster_name": "Rander & Palanpur",
        "business_name": "Surat Tiffin & Catering Hub",
        "cuisine_type": "Large Kitchen / Tiffin",
        "phone_e164": "+919898844119",
        "surat_suburb": "Rander",
        "full_address": "Near Navyug College Road, Rander, Surat",
        "priority_rank": 80
    },
    {
        "cluster_code": "CLUSTER_4_RANDER_PALANPUR",
        "cluster_name": "Rander & Palanpur",
        "business_name": "Bapa Sitaram Tiffin Service",
        "cuisine_type": "Daily Tiffin for Offices",
        "phone_e164": "+919898566772",
        "surat_suburb": "Rander",
        "full_address": "Palanpur Canal Commercial, Rander, Surat",
        "priority_rank": 81
    },
    {
        "cluster_code": "CLUSTER_4_RANDER_PALANPUR",
        "cluster_name": "Rander & Palanpur",
        "business_name": "Tasty Restaurant & Banquet",
        "cuisine_type": "Punjabi / Chinese / Banquet",
        "phone_e164": "+912612918009",
        "surat_suburb": "Rander",
        "full_address": "Shubham Complex, Palanpur-Rander Road, Surat",
        "priority_rank": 82
    },
    {
        "cluster_code": "CLUSTER_4_RANDER_PALANPUR",
        "cluster_name": "Rander & Palanpur",
        "business_name": "Hotel Sona Dining & Rooms",
        "cuisine_type": "Multi-cuisine / Punjabi",
        "phone_e164": "+919825133445",
        "surat_suburb": "Rander",
        "full_address": "Near Palanpur Patiya, Opp. Dena Bank, Rander, Surat",
        "priority_rank": 83
    },
    {
        "cluster_code": "CLUSTER_4_RANDER_PALANPUR",
        "cluster_name": "Rander & Palanpur",
        "business_name": "Concord Palanpur Branch",
        "cuisine_type": "Multi-cuisine / North Indian",
        "phone_e164": "+917779021441",
        "surat_suburb": "Rander",
        "full_address": "Palanpur Canal Road, Rander, Surat",
        "priority_rank": 84
    },
    {
        "cluster_code": "CLUSTER_4_RANDER_PALANPUR",
        "cluster_name": "Rander & Palanpur",
        "business_name": "Liza's Multi Cuisine Restaurant",
        "cuisine_type": "Tandoor / Chinese / North Indian",
        "phone_e164": "+919825677881",
        "surat_suburb": "Rander",
        "full_address": "Near Palanpur Canal Circle, Rander, Surat",
        "priority_rank": 85
    },
    {
        "cluster_code": "CLUSTER_4_RANDER_PALANPUR",
        "cluster_name": "Rander & Palanpur",
        "business_name": "Keshav Punjabi & Gujarati",
        "cuisine_type": "Daily Meals / Paneer Special",
        "phone_e164": "+918734880107",
        "surat_suburb": "Rander",
        "full_address": "Palanpur Patiya Main Road, Rander, Surat",
        "priority_rank": 86
    },
    {
        "cluster_code": "CLUSTER_4_RANDER_PALANPUR",
        "cluster_name": "Rander & Palanpur",
        "business_name": "New Green Garden Restaurant",
        "cuisine_type": "Punjabi & Tandoor",
        "phone_e164": "+919898177225",
        "surat_suburb": "Rander",
        "full_address": "Canal Road, Palanpur, Rander, Surat",
        "priority_rank": 87
    },
    {
        "cluster_code": "CLUSTER_4_RANDER_PALANPUR",
        "cluster_name": "Rander & Palanpur",
        "business_name": "Zamzam Amdavadi Tawa Fry",
        "cuisine_type": "Mughlai Tawa / Spiced Rice",
        "phone_e164": "+919898322119",
        "surat_suburb": "Rander",
        "full_address": "Rander Road, Near Navyug College, Surat",
        "priority_rank": 88
    },
    {
        "cluster_code": "CLUSTER_4_RANDER_PALANPUR",
        "cluster_name": "Rander & Palanpur",
        "business_name": "Mughal Darbar Restaurant",
        "cuisine_type": "Mughlai / Chicken Handi",
        "phone_e164": "+919723811993",
        "surat_suburb": "Rander",
        "full_address": "Gorat Road, Rander, Surat",
        "priority_rank": 89
    },
    {
        "cluster_code": "CLUSTER_4_RANDER_PALANPUR",
        "cluster_name": "Rander & Palanpur",
        "business_name": "Al-Madina Biryani & Darbar",
        "cuisine_type": "Dum Biryani & Mutton Korma",
        "phone_e164": "+919824955662",
        "surat_suburb": "Rander",
        "full_address": "Rander Gorat Road, Surat",
        "priority_rank": 90
    },
    {
        "cluster_code": "CLUSTER_4_RANDER_PALANPUR",
        "cluster_name": "Rander & Palanpur",
        "business_name": "Bismillah Biryani Corner",
        "cuisine_type": "Chicken Dum Biryani",
        "phone_e164": "+919825988117",
        "surat_suburb": "Rander",
        "full_address": "Gorat, Rander, Surat",
        "priority_rank": 91
    },
    {
        "cluster_code": "CLUSTER_4_RANDER_PALANPUR",
        "cluster_name": "Rander & Palanpur",
        "business_name": "Dilpasand Tawa Center",
        "cuisine_type": "Non-Veg Tawa Dishes",
        "phone_e164": "+919824744339",
        "surat_suburb": "Rander",
        "full_address": "Near Rander Causeway, Surat",
        "priority_rank": 92
    },
    {
        "cluster_code": "CLUSTER_4_RANDER_PALANPUR",
        "cluster_name": "Rander & Palanpur",
        "business_name": "A-One Egg & Non-Veg Tawa",
        "cuisine_type": "Surat Special Egg Dishes",
        "phone_e164": "+919712566774",
        "surat_suburb": "Rander",
        "full_address": "Near Rander Town Police Station, Surat",
        "priority_rank": 93
    },
    {
        "cluster_code": "CLUSTER_4_RANDER_PALANPUR",
        "cluster_name": "Rander & Palanpur",
        "business_name": "Shreeji Chhole Bhature & Snacks",
        "cuisine_type": "North Indian Snacks",
        "phone_e164": "+919879744331",
        "surat_suburb": "Rander",
        "full_address": "Palanpur Canal Road, Rander, Surat",
        "priority_rank": 94
    },
    {
        "cluster_code": "CLUSTER_4_RANDER_PALANPUR",
        "cluster_name": "Rander & Palanpur",
        "business_name": "Kailash Parbat Sweets & Fast Food",
        "cuisine_type": "Chaat & North Indian",
        "phone_e164": "+919909588991",
        "surat_suburb": "Rander",
        "full_address": "Near Palanpur Patiya Circle, Rander, Surat",
        "priority_rank": 95
    },
    {
        "cluster_code": "CLUSTER_4_RANDER_PALANPUR",
        "cluster_name": "Rander & Palanpur",
        "business_name": "Sai Fast Food & Sandwich",
        "cuisine_type": "Grilled Sandwiches & Pizza",
        "phone_e164": "+919924833221",
        "surat_suburb": "Rander",
        "full_address": "Palanpur Canal Junction, Rander, Surat",
        "priority_rank": 96
    },
    {
        "cluster_code": "CLUSTER_4_RANDER_PALANPUR",
        "cluster_name": "Rander & Palanpur",
        "business_name": "Rander Street Bites & Rolls",
        "cuisine_type": "Frankies & Kebab Rolls",
        "phone_e164": "+919825077114",
        "surat_suburb": "Rander",
        "full_address": "Near Rander Eidgah, Surat",
        "priority_rank": 97
    },
    {
        "cluster_code": "CLUSTER_4_RANDER_PALANPUR",
        "cluster_name": "Rander & Palanpur",
        "business_name": "Al-Falah Chinese & Tawa",
        "cuisine_type": "Indo-Chinese & Tawa Fry",
        "phone_e164": "+919824399882",
        "surat_suburb": "Rander",
        "full_address": "Near Rander Bus Stop, Surat",
        "priority_rank": 98
    },
    {
        "cluster_code": "CLUSTER_4_RANDER_PALANPUR",
        "cluster_name": "Rander & Palanpur",
        "business_name": "Surbhi Fast Food & Dosa",
        "cuisine_type": "Mysore Masala Dosa / Idli",
        "phone_e164": "+919879255660",
        "surat_suburb": "Rander",
        "full_address": "Near Navyug Science College, Rander, Surat",
        "priority_rank": 99
    },
    {
        "cluster_code": "CLUSTER_4_RANDER_PALANPUR",
        "cluster_name": "Rander & Palanpur",
        "business_name": "Honest Food Zone (Palanpur)",
        "cuisine_type": "Bhaji Pav & Pulav",
        "phone_e164": "+919909911448",
        "surat_suburb": "Rander",
        "full_address": "Palanpur Canal Road, Rander, Surat",
        "priority_rank": 100
    },

    # Cluster 5: Dabholi & Causeway Bridge Belt (101-125)
    {
        "cluster_code": "CLUSTER_5_DABHOLI_CAUSEWAY",
        "cluster_name": "Dabholi & Causeway",
        "business_name": "Ganesh Kathiyawadi Dhaba",
        "cuisine_type": "Kathiyawadi / Desi Dhaba",
        "phone_e164": "+919725911065",
        "surat_suburb": "Dabholi",
        "full_address": "Causeway Link Road, Dabholi-Jahangirpura, Surat",
        "priority_rank": 101
    },
    {
        "cluster_code": "CLUSTER_5_DABHOLI_CAUSEWAY",
        "cluster_name": "Dabholi & Causeway",
        "business_name": "Bhal Ni Dalbati Dhaba",
        "cuisine_type": "Dal Bati Churma / Dhaba",
        "phone_e164": "+919825112903",
        "surat_suburb": "Dabholi",
        "full_address": "Near BRTS Station, Dabholi Road, Surat",
        "priority_rank": 102
    },
    {
        "cluster_code": "CLUSTER_5_DABHOLI_CAUSEWAY",
        "cluster_name": "Dabholi & Causeway",
        "business_name": "Shree Khodiyar Dhaba Dabholi",
        "cuisine_type": "Kathiyawadi / Sev Usal",
        "phone_e164": "+919879522114",
        "surat_suburb": "Dabholi",
        "full_address": "Dabholi Char Rasta, Near Causeway, Surat",
        "priority_rank": 103
    },
    {
        "cluster_code": "CLUSTER_5_DABHOLI_CAUSEWAY",
        "cluster_name": "Dabholi & Causeway",
        "business_name": "Chamunda Kathiyawadi Dhaba",
        "cuisine_type": "Kathiyawadi / Rotla & Lasan",
        "phone_e164": "+919898244331",
        "surat_suburb": "Dabholi",
        "full_address": "Causeway Link Road, Singanpore, Surat",
        "priority_rank": 104
    },
    {
        "cluster_code": "CLUSTER_5_DABHOLI_CAUSEWAY",
        "cluster_name": "Dabholi & Causeway",
        "business_name": "Radhe Kathiyawadi Dhaba",
        "cuisine_type": "Kathiyawadi / Ringna Bharta",
        "phone_e164": "+919925966771",
        "surat_suburb": "Dabholi",
        "full_address": "Singanpore Causeway Road, Surat",
        "priority_rank": 105
    },
    {
        "cluster_code": "CLUSTER_5_DABHOLI_CAUSEWAY",
        "cluster_name": "Dabholi & Causeway",
        "business_name": "Jay Ambe Kathiyawadi Kitchen",
        "cuisine_type": "Dhaba / Sev Dungri",
        "phone_e164": "+919825766994",
        "surat_suburb": "Dabholi",
        "full_address": "Near Tapi Weir Causeway, Dabholi, Surat",
        "priority_rank": 106
    },
    {
        "cluster_code": "CLUSTER_5_DABHOLI_CAUSEWAY",
        "cluster_name": "Dabholi & Causeway",
        "business_name": "Desi Dhaba Kathiyawadi Hub",
        "cuisine_type": "Chhas / Rotla / Lasaniya Bataka",
        "phone_e164": "+919904822117",
        "surat_suburb": "Dabholi",
        "full_address": "Causeway Riverfront Road, Dabholi, Surat",
        "priority_rank": 107
    },
    {
        "cluster_code": "CLUSTER_5_DABHOLI_CAUSEWAY",
        "cluster_name": "Dabholi & Causeway",
        "business_name": "Nilkanth Dining Hall",
        "cuisine_type": "Kathiyawadi / Rotla Ghee",
        "phone_e164": "+919712877663",
        "surat_suburb": "Dabholi",
        "full_address": "Causeway Road, Dabholi, Surat",
        "priority_rank": 108
    },
    {
        "cluster_code": "CLUSTER_5_DABHOLI_CAUSEWAY",
        "cluster_name": "Dabholi & Causeway",
        "business_name": "Jay Jalaram Dal Bati Center",
        "cuisine_type": "Dal Bati / Gatte ki Sabzi",
        "phone_e164": "+919904277885",
        "surat_suburb": "Dabholi",
        "full_address": "Near Dabholi BRTS, Surat",
        "priority_rank": 109
    },
    {
        "cluster_code": "CLUSTER_5_DABHOLI_CAUSEWAY",
        "cluster_name": "Dabholi & Causeway",
        "business_name": "Patel Parotha & Shak Center",
        "cuisine_type": "Desi Gujarati Parotha",
        "phone_e164": "+919712188992",
        "surat_suburb": "Dabholi",
        "full_address": "Near Causeway Bridge Pillar 4, Dabholi, Surat",
        "priority_rank": 110
    },
    {
        "cluster_code": "CLUSTER_5_DABHOLI_CAUSEWAY",
        "cluster_name": "Dabholi & Causeway",
        "business_name": "Krishna Dining Hall",
        "cuisine_type": "Gujarati Unlimited Thali",
        "phone_e164": "+919825855669",
        "surat_suburb": "Dabholi",
        "full_address": "Dabholi Main Road, Surat",
        "priority_rank": 111
    },
    {
        "cluster_code": "CLUSTER_5_DABHOLI_CAUSEWAY",
        "cluster_name": "Dabholi & Causeway",
        "business_name": "Bapa Sitaram Bhojanalaya",
        "cuisine_type": "Daily Thali / Kathiyawadi",
        "phone_e164": "+919723411883",
        "surat_suburb": "Dabholi",
        "full_address": "Near Dabholi Lake Garden, Surat",
        "priority_rank": 112
    },
    {
        "cluster_code": "CLUSTER_5_DABHOLI_CAUSEWAY",
        "cluster_name": "Dabholi & Causeway",
        "business_name": "Khodiyar Tiffin & Mess",
        "cuisine_type": "Daily Tiffin for Workers",
        "phone_e164": "+919825588331",
        "surat_suburb": "Dabholi",
        "full_address": "Dabholi Village, Surat",
        "priority_rank": 113
    },
    {
        "cluster_code": "CLUSTER_5_DABHOLI_CAUSEWAY",
        "cluster_name": "Dabholi & Causeway",
        "business_name": "Tulsi Restaurant & Caterers",
        "cuisine_type": "Gujarati / Punjabi",
        "phone_e164": "+919898099118",
        "surat_suburb": "Dabholi",
        "full_address": "Near Dabholi BRTS Terminal, Surat",
        "priority_rank": 114
    },
    {
        "cluster_code": "CLUSTER_5_DABHOLI_CAUSEWAY",
        "cluster_name": "Dabholi & Causeway",
        "business_name": "Shree Hari Villa Garden Restaurant",
        "cuisine_type": "Punjabi & Garden Dining",
        "phone_e164": "+919879944558",
        "surat_suburb": "Dabholi",
        "full_address": "Ved-Dabholi Link Road, Surat",
        "priority_rank": 115
    },
    {
        "cluster_code": "CLUSTER_5_DABHOLI_CAUSEWAY",
        "cluster_name": "Dabholi & Causeway",
        "business_name": "Sanju Dhaba & Tawa Kitchen",
        "cuisine_type": "Dhaba / Seafood & Tawa",
        "phone_e164": "+919712958432",
        "surat_suburb": "Dabholi",
        "full_address": "Tekra Faliya, Near Jahangirpura Bridge, Surat",
        "priority_rank": 116
    },
    {
        "cluster_code": "CLUSTER_5_DABHOLI_CAUSEWAY",
        "cluster_name": "Dabholi & Causeway",
        "business_name": "New Royal Tawa Fry",
        "cuisine_type": "Egg & Tawa Special",
        "phone_e164": "+919879188775",
        "surat_suburb": "Dabholi",
        "full_address": "Singanpore Link Road, Surat",
        "priority_rank": 117
    },
    {
        "cluster_code": "CLUSTER_5_DABHOLI_CAUSEWAY",
        "cluster_name": "Dabholi & Causeway",
        "business_name": "Flavour Funshion The Fast Food",
        "cuisine_type": "Street Food & Chinese",
        "phone_e164": "+919825433118",
        "surat_suburb": "Dabholi",
        "full_address": "Beside Torrent Power, Dabholi Bridge, Surat",
        "priority_rank": 118
    },
    {
        "cluster_code": "CLUSTER_5_DABHOLI_CAUSEWAY",
        "cluster_name": "Dabholi & Causeway",
        "business_name": "Dabholi Fast Food & Pav Bhaji",
        "cuisine_type": "Pav Bhaji / Pulao",
        "phone_e164": "+919824611223",
        "surat_suburb": "Dabholi",
        "full_address": "Dabholi Gam Char Rasta, Surat",
        "priority_rank": 119
    },
    {
        "cluster_code": "CLUSTER_5_DABHOLI_CAUSEWAY",
        "cluster_name": "Dabholi & Causeway",
        "business_name": "Sardar Pav Bhaji & Pulao",
        "cuisine_type": "Amul Butter Pav Bhaji",
        "phone_e164": "+919924511229",
        "surat_suburb": "Dabholi",
        "full_address": "Opp. BRTS Station, Dabholi, Surat",
        "priority_rank": 120
    },
    {
        "cluster_code": "CLUSTER_5_DABHOLI_CAUSEWAY",
        "cluster_name": "Dabholi & Causeway",
        "business_name": "Shreeji Live Dosa Center",
        "cuisine_type": "Gotala Dosa / Cheese Dosa",
        "phone_e164": "+919824144552",
        "surat_suburb": "Dabholi",
        "full_address": "Dabholi Circle Corner, Surat",
        "priority_rank": 121
    },
    {
        "cluster_code": "CLUSTER_5_DABHOLI_CAUSEWAY",
        "cluster_name": "Dabholi & Causeway",
        "business_name": "Maruti Dosa & Fast Food",
        "cuisine_type": "South Indian Live Dosa",
        "phone_e164": "+919898755449",
        "surat_suburb": "Dabholi",
        "full_address": "Causeway Approach Road, Dabholi, Surat",
        "priority_rank": 122
    },
    {
        "cluster_code": "CLUSTER_5_DABHOLI_CAUSEWAY",
        "cluster_name": "Dabholi & Causeway",
        "business_name": "Balaji Chinese & Soup Stall",
        "cuisine_type": "Manchurian / Noodles",
        "phone_e164": "+919825322117",
        "surat_suburb": "Dabholi",
        "full_address": "Near Dabholi Police Chowki, Surat",
        "priority_rank": 123
    },
    {
        "cluster_code": "CLUSTER_5_DABHOLI_CAUSEWAY",
        "cluster_name": "Dabholi & Causeway",
        "business_name": "Welcome Fast Food & Chinese",
        "cuisine_type": "Chinese Fried Rice / Choupsey",
        "phone_e164": "+919879344552",
        "surat_suburb": "Dabholi",
        "full_address": "Singanpore Causeway Corner, Surat",
        "priority_rank": 124
    },
    {
        "cluster_code": "CLUSTER_5_DABHOLI_CAUSEWAY",
        "cluster_name": "Dabholi & Causeway",
        "business_name": "Surat Live Dhokla & Khaman",
        "cuisine_type": "Fresh Steamed Farsan",
        "phone_e164": "+919909433226",
        "surat_suburb": "Dabholi",
        "full_address": "Dabholi Gam Main Road, Surat",
        "priority_rank": 125
    },

    # Cluster 6: Variyav & Highway Dhaba Belt (126-150)
    {
        "cluster_code": "CLUSTER_6_VARIYAV_HIGHWAY",
        "cluster_name": "Variyav & Highway",
        "business_name": "Variyav Highway Garden Restaurant",
        "cuisine_type": "Highway Dhaba / Punjabi",
        "phone_e164": "+919825177665",
        "surat_suburb": "Variyav",
        "full_address": "Variyav Circle, Surat-Olpad Highway, Surat",
        "priority_rank": 126
    },
    {
        "cluster_code": "CLUSTER_6_VARIYAV_HIGHWAY",
        "cluster_name": "Variyav & Highway",
        "business_name": "Jay Ranchhod Kathiyawadi Dhaba",
        "cuisine_type": "Authentic Kathiyawadi",
        "phone_e164": "+919879044332",
        "surat_suburb": "Variyav",
        "full_address": "Near Variyav Bridge, Olpad Highway, Surat",
        "priority_rank": 127
    },
    {
        "cluster_code": "CLUSTER_6_VARIYAV_HIGHWAY",
        "cluster_name": "Variyav & Highway",
        "business_name": "Chamunda Highway Hotel & Dining",
        "cuisine_type": "Desi Dhaba / Bajra Roti",
        "phone_e164": "+919723988771",
        "surat_suburb": "Variyav",
        "full_address": "Variyav Jakatnaka, Highway, Surat",
        "priority_rank": 128
    },
    {
        "cluster_code": "CLUSTER_6_VARIYAV_HIGHWAY",
        "cluster_name": "Variyav & Highway",
        "business_name": "Shree Khodiyar Garden Restaurant",
        "cuisine_type": "Kathiyawadi & Gujarati",
        "phone_e164": "+919825633228",
        "surat_suburb": "Variyav",
        "full_address": "Surat-Olpad Road, Variyav, Surat",
        "priority_rank": 129
    },
    {
        "cluster_code": "CLUSTER_6_VARIYAV_HIGHWAY",
        "cluster_name": "Variyav & Highway",
        "business_name": "Krishna Kathiyawadi Dhaba Variyav",
        "cuisine_type": "Kathiyawadi / Sev Tameta",
        "phone_e164": "+919904155662",
        "surat_suburb": "Variyav",
        "full_address": "Near Variyav Gam Bus Stop, Surat",
        "priority_rank": 130
    },
    {
        "cluster_code": "CLUSTER_6_VARIYAV_HIGHWAY",
        "cluster_name": "Variyav & Highway",
        "business_name": "Bapa Sitaram Kathiyawadi Variyav",
        "cuisine_type": "Ringna Olo / Rotla",
        "phone_e164": "+919879811993",
        "surat_suburb": "Variyav",
        "full_address": "Near Variyav Patiya, Surat",
        "priority_rank": 131
    },
    {
        "cluster_code": "CLUSTER_6_VARIYAV_HIGHWAY",
        "cluster_name": "Variyav & Highway",
        "business_name": "Amroli-Variyav Dhaba & Kitchen",
        "cuisine_type": "Kathiyawadi / Dhaba",
        "phone_e164": "+919925244558",
        "surat_suburb": "Variyav",
        "full_address": "Variyav-Amroli Bridge Road, Surat",
        "priority_rank": 132
    },
    {
        "cluster_code": "CLUSTER_6_VARIYAV_HIGHWAY",
        "cluster_name": "Variyav & Highway",
        "business_name": "Jay Meldi Kathiyawadi Dhaba",
        "cuisine_type": "Desi Dhaba / Lasan Chatni",
        "phone_e164": "+919898633227",
        "surat_suburb": "Variyav",
        "full_address": "Variyav Gam Road, Surat",
        "priority_rank": 133
    },
    {
        "cluster_code": "CLUSTER_6_VARIYAV_HIGHWAY",
        "cluster_name": "Variyav & Highway",
        "business_name": "Patel Kathiyawadi Bhojnalaya",
        "cuisine_type": "Gujarati Rasoi / Thali",
        "phone_e164": "+919825911448",
        "surat_suburb": "Variyav",
        "full_address": "Variyav Char Rasta, Surat",
        "priority_rank": 134
    },
    {
        "cluster_code": "CLUSTER_6_VARIYAV_HIGHWAY",
        "cluster_name": "Variyav & Highway",
        "business_name": "Shree Ram Kathiyawadi Dhaba",
        "cuisine_type": "Desi Rotla & Shak",
        "phone_e164": "+919924688991",
        "surat_suburb": "Variyav",
        "full_address": "Variyav Highway Corner, Surat",
        "priority_rank": 135
    },
    {
        "cluster_code": "CLUSTER_6_VARIYAV_HIGHWAY",
        "cluster_name": "Variyav & Highway",
        "business_name": "Sai Baba Kathiyawadi Dhaba",
        "cuisine_type": "Kathiyawadi / Sev Dungri",
        "phone_e164": "+919904311228",
        "surat_suburb": "Variyav",
        "full_address": "Variyav River Approach Road, Surat",
        "priority_rank": 136
    },
    {
        "cluster_code": "CLUSTER_6_VARIYAV_HIGHWAY",
        "cluster_name": "Variyav & Highway",
        "business_name": "Jalaram Parotha House Variyav",
        "cuisine_type": "Parotha Shak / Chaas",
        "phone_e164": "+919723144556",
        "surat_suburb": "Variyav",
        "full_address": "Near Variyav BRTS, Surat",
        "priority_rank": 137
    },
    {
        "cluster_code": "CLUSTER_6_VARIYAV_HIGHWAY",
        "cluster_name": "Variyav & Highway",
        "business_name": "Maruti Nandan Dining Hall",
        "cuisine_type": "Pure Veg Unlimited Thali",
        "phone_e164": "+919909722114",
        "surat_suburb": "Variyav",
        "full_address": "Variyav Market, Surat",
        "priority_rank": 138
    },
    {
        "cluster_code": "CLUSTER_6_VARIYAV_HIGHWAY",
        "cluster_name": "Variyav & Highway",
        "business_name": "Ganesh Dining Hall Variyav",
        "cuisine_type": "Gujarati Thali & Farsan",
        "phone_e164": "+919824066775",
        "surat_suburb": "Variyav",
        "full_address": "Near Variyav Gram Panchayat, Surat",
        "priority_rank": 139
    },
    {
        "cluster_code": "CLUSTER_6_VARIYAV_HIGHWAY",
        "cluster_name": "Variyav & Highway",
        "business_name": "Annapurna Highway Kitchen",
        "cuisine_type": "Daily Tiffin & Highway Meals",
        "phone_e164": "+919712733449",
        "surat_suburb": "Variyav",
        "full_address": "Variyav Junction, Surat",
        "priority_rank": 140
    },
    {
        "cluster_code": "CLUSTER_6_VARIYAV_HIGHWAY",
        "cluster_name": "Variyav & Highway",
        "business_name": "Tapi Riverview Garden Dhaba",
        "cuisine_type": "Family Garden / Punjabi",
        "phone_e164": "+919898211449",
        "surat_suburb": "Variyav",
        "full_address": "Variyav Tapi Riverfront, Surat",
        "priority_rank": 141
    },
    {
        "cluster_code": "CLUSTER_6_VARIYAV_HIGHWAY",
        "cluster_name": "Variyav & Highway",
        "business_name": "Green View Garden Dhaba",
        "cuisine_type": "Family Garden Restaurant",
        "phone_e164": "+919879466772",
        "surat_suburb": "Variyav",
        "full_address": "Olpad Highway, Variyav, Surat",
        "priority_rank": 142
    },
    {
        "cluster_code": "CLUSTER_6_VARIYAV_HIGHWAY",
        "cluster_name": "Variyav & Highway",
        "business_name": "Highway King Punjabi Dhaba",
        "cuisine_type": "Punjabi / Dal Makhani Tandoor",
        "phone_e164": "+919824877114",
        "surat_suburb": "Variyav",
        "full_address": "Variyav Highway Cross Road, Surat",
        "priority_rank": 143
    },
    {
        "cluster_code": "CLUSTER_6_VARIYAV_HIGHWAY",
        "cluster_name": "Variyav & Highway",
        "business_name": "Radhe Krishna Highway Restaurant",
        "cuisine_type": "North Indian & Kathiyawadi",
        "phone_e164": "+919825399881",
        "surat_suburb": "Variyav",
        "full_address": "Olpad Highway, Variyav, Surat",
        "priority_rank": 144
    },
    {
        "cluster_code": "CLUSTER_6_VARIYAV_HIGHWAY",
        "cluster_name": "Variyav & Highway",
        "business_name": "Shiv Shakti Punjabi Dhaba",
        "cuisine_type": "Tandoori Roti & Paneer Handi",
        "phone_e164": "+919824355661",
        "surat_suburb": "Variyav",
        "full_address": "Near Tapi Bridge, Variyav, Surat",
        "priority_rank": 145
    },
    {
        "cluster_code": "CLUSTER_6_VARIYAV_HIGHWAY",
        "cluster_name": "Variyav & Highway",
        "business_name": "Tulsi Highway Restaurant",
        "cuisine_type": "Multicuisine / Punjabi",
        "phone_e164": "+919898077883",
        "surat_suburb": "Variyav",
        "full_address": "Surat-Olpad State Highway, Surat",
        "priority_rank": 146
    },
    {
        "cluster_code": "CLUSTER_6_VARIYAV_HIGHWAY",
        "cluster_name": "Variyav & Highway",
        "business_name": "Chhatrapati Highway Dhaba",
        "cuisine_type": "Punjabi / Tandoor Special",
        "phone_e164": "+919879699002",
        "surat_suburb": "Variyav",
        "full_address": "Olpad Road, Variyav, Surat",
        "priority_rank": 147
    },
    {
        "cluster_code": "CLUSTER_6_VARIYAV_HIGHWAY",
        "cluster_name": "Variyav & Highway",
        "business_name": "Kismat Highway Hotel",
        "cuisine_type": "Tawa Non-Veg & Biryani",
        "phone_e164": "+919712088995",
        "surat_suburb": "Variyav",
        "full_address": "Variyav Junction, Highway, Surat",
        "priority_rank": 148
    },
    {
        "cluster_code": "CLUSTER_6_VARIYAV_HIGHWAY",
        "cluster_name": "Variyav & Highway",
        "business_name": "Royal Highway Tawa Center",
        "cuisine_type": "Egg & Chicken Tawa",
        "phone_e164": "+919898488113",
        "surat_suburb": "Variyav",
        "full_address": "Variyav Outskirts, Highway, Surat",
        "priority_rank": 149
    },
    {
        "cluster_code": "CLUSTER_6_VARIYAV_HIGHWAY",
        "cluster_name": "Variyav & Highway",
        "business_name": "New Star Chinese & Fast Food",
        "cuisine_type": "Indo-Chinese & Fast Food",
        "phone_e164": "+919825422339",
        "surat_suburb": "Variyav",
        "full_address": "Variyav Bazar, Surat",
        "priority_rank": 150
    }
]

async def sync():
    conn = await asyncpg.connect(DATABASE_URL)
    print("Connected to Neon DB. Initializing future_clients_and_prospects table...")

    # 1. Create dedicated prospects_and_clients table
    await conn.execute("""
        CREATE TABLE IF NOT EXISTS future_clients_and_prospects (
            id SERIAL PRIMARY KEY,
            cluster_code VARCHAR(50) NOT NULL,
            cluster_name VARCHAR(100) NOT NULL,
            business_name VARCHAR(255) NOT NULL,
            phone_e164 VARCHAR(30) UNIQUE NOT NULL,
            cuisine_type VARCHAR(100),
            surat_suburb VARCHAR(100),
            full_address TEXT,
            stage VARCHAR(50) DEFAULT 'PROSPECT',
            priority_rank INT,
            order_unit VARCHAR(20) DEFAULT 'KG',
            min_order_kg NUMERIC(6,2) DEFAULT 1.0,
            delivery_fee_range VARCHAR(50) DEFAULT '₹20 - ₹50',
            launch_scheme_date VARCHAR(50) DEFAULT '21st',
            notes TEXT,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        );
        CREATE INDEX IF NOT EXISTS idx_fcp_cluster ON future_clients_and_prospects(cluster_code);
        CREATE INDEX IF NOT EXISTS idx_fcp_stage ON future_clients_and_prospects(stage);
        CREATE INDEX IF NOT EXISTS idx_fcp_phone ON future_clients_and_prospects(phone_e164);
        CREATE INDEX IF NOT EXISTS idx_fcp_rank ON future_clients_and_prospects(priority_rank);
    """)

    print(f"Table ready. Ingesting and sorting all {len(ALL_150_PROSPECTS)} prospects...")

    fcp_count = 0
    leads_count = 0

    for p in ALL_150_PROSPECTS:
        # Insert into dedicated future_clients_and_prospects
        await conn.execute("""
            INSERT INTO future_clients_and_prospects 
                (cluster_code, cluster_name, business_name, phone_e164, cuisine_type, surat_suburb, full_address, priority_rank, notes)
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
            ON CONFLICT (phone_e164) DO UPDATE SET
                business_name = EXCLUDED.business_name,
                cluster_code = EXCLUDED.cluster_code,
                cluster_name = EXCLUDED.cluster_name,
                cuisine_type = EXCLUDED.cuisine_type,
                surat_suburb = EXCLUDED.surat_suburb,
                full_address = EXCLUDED.full_address,
                priority_rank = EXCLUDED.priority_rank,
                updated_at = NOW();
        """, p["cluster_code"], p["cluster_name"], p["business_name"], p["phone_e164"], p["cuisine_type"], p["surat_suburb"], p["full_address"], p["priority_rank"], f"Scheme from 21st, min 1kg+, delivery fee ₹20-₹50")
        fcp_count += 1

        # Synchronize into active leads table for the bot
        await conn.execute("""
            INSERT INTO leads (business_name, phone_e164, cuisine_type, surat_suburb, full_address, source, status)
            VALUES ($1, $2, $3, $4, $5, 'NW_SURAT_150_PIPELINE', 'NEW')
            ON CONFLICT (phone_e164) DO UPDATE SET
                business_name = EXCLUDED.business_name,
                cuisine_type = EXCLUDED.cuisine_type,
                surat_suburb = EXCLUDED.surat_suburb,
                full_address = EXCLUDED.full_address,
                updated_at = NOW();
        """, p["business_name"], p["phone_e164"], p["cuisine_type"], p["surat_suburb"], p["full_address"])
        leads_count += 1

    total_fcp = await conn.fetchval("SELECT count(*) FROM future_clients_and_prospects;")
    total_leads = await conn.fetchval("SELECT count(*) FROM leads;")
    by_cluster = await conn.fetch("SELECT cluster_name, count(*) FROM future_clients_and_prospects GROUP BY cluster_name ORDER BY count DESC;")

    print("\n✅ DATABASE SYNC REPORT:")
    print(f" - Total in future_clients_and_prospects: {total_fcp}")
    print(f" - Total in active bot leads table: {total_leads}")
    for bc in by_cluster:
        print(f"   • {bc['cluster_name']}: {bc['count']} prospects")

    await conn.close()

    # Also export local SQLite database in workspace scratch directory for offline querying
    local_db_path = "C:/Users/om/.gemini/antigravity/scratch/alliobot-whatsapp-agent/database/future_clients_and_prospects.db"
    os.makedirs(os.path.dirname(local_db_path), exist_ok=True)
    sl_conn = sqlite3.connect(local_db_path)
    sl_cur = sl_conn.cursor()
    sl_cur.execute("""
        CREATE TABLE IF NOT EXISTS future_clients_and_prospects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cluster_code TEXT,
            cluster_name TEXT,
            business_name TEXT,
            phone_e164 TEXT UNIQUE,
            cuisine_type TEXT,
            surat_suburb TEXT,
            full_address TEXT,
            stage TEXT DEFAULT 'PROSPECT',
            priority_rank INTEGER,
            order_unit TEXT DEFAULT 'KG',
            min_order_kg REAL DEFAULT 1.0,
            delivery_fee_range TEXT DEFAULT '₹20 - ₹50',
            launch_scheme_date TEXT DEFAULT '21st',
            notes TEXT
        );
    """)
    for p in ALL_150_PROSPECTS:
        sl_cur.execute("""
            INSERT OR REPLACE INTO future_clients_and_prospects 
            (cluster_code, cluster_name, business_name, phone_e164, cuisine_type, surat_suburb, full_address, priority_rank, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);
        """, (p["cluster_code"], p["cluster_name"], p["business_name"], p["phone_e164"], p["cuisine_type"], p["surat_suburb"], p["full_address"], p["priority_rank"], "Scheme from 21st, min 1kg+, delivery fee ₹20-₹50"))
    sl_conn.commit()
    sl_conn.close()
    print(f"Local SQLite database mirrored at: {local_db_path}")

if __name__ == "__main__":
    asyncio.run(sync())
