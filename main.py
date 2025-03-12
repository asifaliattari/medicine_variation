import streamlit as st
import requests
import json
from fpdf import FPDF

# Function to fetch medicines based on formula (Active Ingredient)
def get_medicines_by_formula(formula, limit=10):
    url = f"https://rxnav.nlm.nih.gov/REST/drugs.json?name={formula}"
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        medicines = []

        if "drugGroup" in data and "conceptGroup" in data["drugGroup"]:
            for group in data["drugGroup"]["conceptGroup"]:
                if "conceptProperties" in group:
                    for med in group["conceptProperties"]:
                        medicines.append({
                            "name": med["name"],  # Medicine Name
                            "rxcui": med["rxcui"],  # RxCUI Code
                            "brand": med.get("synonym", "Unknown Brand")  # Brand Name (if available)
                        })

        return medicines[:limit]  # Limit the number of results
    return []

# Function to generate a PDF prescription
def generate_pdf(medicine):
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    
    pdf.set_font("Arial", "B", 16)
    pdf.cell(200, 10, "Doctor's Prescription", ln=True, align="C")
    
    pdf.ln(10)
    pdf.set_font("Arial", "", 12)
    
    pdf.multi_cell(0, 10, f"Selected Medicine: {medicine['name']}")
    pdf.cell(200, 10, f"Brand: {medicine['brand']}", ln=True)
    pdf.cell(200, 10, f"RxCUI Code: {medicine['rxcui']}", ln=True)
    
    pdf_filename = "prescription.pdf"
    pdf.output(pdf_filename)
    return pdf_filename

# Streamlit UI
st.title("💊 Medicine Finder by Formula")

# Step 1: Doctor inputs the medicine formula
formula_input = st.text_input("Enter the Active Ingredient (Formula):")

# "Enter" button to trigger the search
search_clicked = st.button("🔍 Enter")

if search_clicked and formula_input:
    # User selects how many medicine brands to show
    limit = st.slider("How many medicine brands do you want to display?", min_value=1, max_value=20, value=5)

    # Fetch medicines when the button is clicked
    medicines = get_medicines_by_formula(formula_input, limit)

    if medicines:
        st.subheader("Step 2: Select a Medicine from Different Companies")
        selected_medicine = st.selectbox("Choose a medicine:", medicines, format_func=lambda x: f"{x['name']} - {x['brand']}")

        # Step 3: Generate Prescription Files
        if st.button("Generate Prescription PDF"):
            pdf_file = generate_pdf(selected_medicine)

            st.success("✅ Prescription PDF Generated!")

            # Download PDF
            with open(pdf_file, "rb") as file:
                st.download_button("📄 Download Prescription", file, file_name="prescription.pdf", mime="application/pdf")

        # Show JSON Response (For Debugging)
        st.subheader("📝 Medicine Data (JSON)")
        st.json(medicines)
    else:
        st.warning("⚠️ No medicines found. Try another formula.")
