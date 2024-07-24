import pandas as pd
import easyocr
import streamlit as st
from PIL import Image
import os
import cv2
import matplotlib.pyplot as plt
import re
import mysql.connector
import pytesseract




icon = Image.open("C:/Users/LENOVO/Desktop/bizcard/uploaded_cards/1.jpg")
st.set_page_config(page_title= "BizCardX: Extracting Business Card Data with OCR | By Jafar Hussain",
                   page_icon= icon,
                   layout= "wide",
                   initial_sidebar_state= "expanded",
                   menu_items={'About': """# This OCR app is created by *Jafar Hussain*!"""})
st.markdown("<h1 style='text-align: center; color: white;'>BizCardX: Extracting Business Card Data with OCR</h1>", unsafe_allow_html=True)

def setting_bg():
    st.markdown(f""" <style>.stApp {{
                        background: url("https://cutewallpaper.org/21/web-background-images/webplunder-background-image-technology-online-website-.jpg");
                        background-size: cover}}
                     </style>""",unsafe_allow_html=True) 
setting_bg()

# Home page creation
def home_page() :
    st.title("Home Page")

    col1,col2 = st.columns(2)

    with col1 :

        st.markdown("Technologies Used : Python, PostgreSQL, Easy OCR, Pandas and Streamlit")

    with col2 :
        image_path = "C:/Users/LENOVO/Desktop/bizcard/Home.jpg"
        st.image(image_path, use_column_width=True)

def modify_page():
    col1, col2, col3 = st.columns([3, 3, 2])
    col2.markdown("## Alter or Delete the data here")
    column1, column2 = st.columns(2, gap="large")

    with column1:
        cursor.execute("SELECT card_holder FROM card_data")
        result = cursor.fetchall()
        business_cards = {}

        # Check if result is empty
        if not result:
            st.warning("No card holders found.")
        else:
            for row in result:
                business_cards[row[0]] = row[0]

            selected_card = st.selectbox("Select a card holder name to update", list(business_cards.keys()))

            st.markdown("#### Update or modify any data below")
            cursor.execute(
                "select company_name,card_holder,designation,mobile_number,email,website,area,city,state,pin_code from card_data WHERE card_holder=%s",
                (selected_card,))
            result = cursor.fetchone()

            # Check if result is not None before accessing its elements
            if result is not None:
                # DISPLAYING ALL THE INFORMATIONS
                company_name = st.text_input("Company_Name", result[0] if result[0] is not None else "")
                card_holder = st.text_input("Card_Holder", result[1] if result[1] is not None else "")
                designation = st.text_input("Designation", result[2] if result[2] is not None else "")
                mobile_number = st.text_input("Mobile_Number", result[3] if result[3] is not None else "")
                email = st.text_input("Email", result[4] if result[4] is not None else "")
                website = st.text_input("Website", result[5] if result[5] is not None else "")
                area = st.text_input("Area", result[6] if result[6] is not None else "")
                city = st.text_input("City", result[7] if result[7] is not None else "")
                state = st.text_input("State", result[8] if result[8] is not None else "")
                pin_code = st.text_input("Pin_Code", result[9] if result[9] is not None else "")

                if st.button("Commit changes to DB"):
                    # Update the information for the selected business card in the database
                    cursor.execute(
                        """UPDATE card_data SET company_name=%s,card_holder=%s,designation=%s,mobile_number=%s,email=%s,website=%s,area=%s,city=%s,state=%s,pin_code=%s
                            WHERE card_holder=%s""",
                        (company_name, card_holder, designation, mobile_number, email, website, area, city, state,
                         pin_code, selected_card))
                    conn.commit()
                    st.success("Information updated in database successfully.")
            else:
                st.warning("No data found for the selected card holder.")

    with column2:
        cursor.execute("SELECT card_holder FROM card_data")
        result = cursor.fetchall()
        business_cards = {}

        # Check if result is empty
        if not result:
            st.warning("No card holders found.")
        else:
            for row in result:
                business_cards[row[0]] = row[0]

            selected_card = st.selectbox("Select a card holder name to Delete", list(business_cards.keys()))
            st.write(f"### You have selected :green[**{selected_card}'s**] card to delete")
            st.write("#### Proceed to delete this card?")

            if st.button("Yes Delete Business Card"):
                cursor.execute(f"DELETE FROM card_data WHERE card_holder='{selected_card}'")
                conn.commit()
                st.success("Business card information deleted from database.")

    if st.button("View updated data"):
        cursor.execute(
            "select company_name,card_holder,designation,mobile_number,email,website,area,city,state,pin_code from card_data")
        updated_df = pd.DataFrame(cursor.fetchall(),
                                  columns=["Company_Name", "Card_Holder", "Designation", "Mobile_Number", "Email",
                                           "Website", "Area", "City", "State", "Pin_Code"])
        st.write(updated_df)


import psycopg2
import streamlit as st

# Connect to PostgreSQL
conn = psycopg2.connect(
    host="localhost",
    user="postgres",
    password="080902",
    database="bizcard",
    port="5432",
)

# Create a cursor object
cursor = conn.cursor()

# Define the SQL query to create the table with SERIAL for auto-incrementing id
create_table_query = """
CREATE TABLE IF NOT EXISTS card_data (
    id SERIAL PRIMARY KEY,
    company_name VARCHAR(255),
    card_holder VARCHAR(255),
    designation VARCHAR(255),
    mobile_number VARCHAR(20),
    email VARCHAR(255),
    website VARCHAR(255),
    area VARCHAR(255),
    city VARCHAR(255),
    state VARCHAR(255),
    pin_code VARCHAR(10),
    image BYTEA
);
"""

# Execute the SQL query
cursor.execute(create_table_query)

# Commit the changes
conn.commit()

# Close the cursor and connection
cursor.close()
conn.close()
conn = psycopg2.connect(
    host="localhost",
    user="postgres",
    password="080902",
    database="bizcard",
    port="5432",
)

conn.autocommit = False
cursor = conn.cursor()

# Set Tesseract and other configurations
os.environ['TESSDATA_PREFIX'] = r'C:/Program Files/Tesseract-OCR'
pytesseract.pytesseract.tesseract_cmd = r'C:/Program Files/Tesseract-OCR/tesseract.exe'

# Create a directory for uploaded cards
save_directory = "uploaded_cards"
if not os.path.exists(save_directory):
    os.makedirs(save_directory)

def img_to_binary(file):
    if file is not None:
        with open(file, 'rb') as file:
            binaryData = file.read()
        return binaryData
    else:
        return None

def extract_text_from_image(image_path):
    img = Image.open(image_path)
    custom_config = r'--oem 3 --psm 6 --tessdata-dir "C:/Program Files/Tesseract-OCR/tessdata"'
    text = pytesseract.image_to_string(img, config=custom_config)
    return text

def get_data(res, image_path):
    data = {
        "company_name": [],
        "card_holder": [],
        "designation": [],
        "mobile_number": [],
        "email": [],
        "website": [],
        "area": [],
        "city": [],
        "state": [],
        "pin_code": [],
        "image": img_to_binary(image_path)
    }

    for ind, i in enumerate(res):
        if "www " in str(i).lower() or "www." in str(i).lower():
            data["website"].append(str(i))
        elif "WWW" in str(i):
            data["website"] = str(res[4]) + "." + str(res[5])

        elif "@" in str(i):
            data["email"].append(str(i))

        elif "-" in str(i):
            data["mobile_number"].append(str(i))
            if len(data["mobile_number"]) == 2:
                data["mobile_number"] = " & ".join(data["mobile_number"])

        elif ind == len(res) - 1:
            data["company_name"].append(str(i))

        elif ind == 0:
            data["card_holder"].append(str(i))

        elif ind == 1:
            data["designation"].append(str(i))

        if re.findall('^[0-9].+, [a-zA-Z]+', str(i)):
            data["area"].append(str(i).split(',')[0])
        elif re.findall('[0-9] [a-zA-Z]+', str(i)):
            data["area"].append(str(i))

        match1 = re.findall('.+St , ([a-zA-Z]+).+', str(i))
        match2 = re.findall('.+St,, ([a-zA-Z]+).+', str(i))
        match3 = re.findall('^[E].*', str(i))
        if match1:
            data["city"].append(match1[0])
        elif match2:
            data["city"].append(match2[0])
        elif match3:
            data["city"].append(match3[0])

        state_match = re.findall('[a-zA-Z]{9} +[0-9]', str(i))
        if state_match:
            data["state"].append(str(i)[:9])
        elif re.findall('^[0-9].+, ([a-zA-Z]+);', str(i)):
            data["state"].append(str(i).split()[-1])
        if len(data["state"]) == 2:
            data["state"].pop(0)

        if len(str(i)) >= 6 and str(i).isdigit():
            data["pin_code"].append(str(i))
        elif re.findall('[a-zA-Z]{9} +[0-9]', str(i)):
            data["pin_code"].append(str(i)[10:])

    return data

def create_df(data):
    for key, value in data.items():
        print(f"Length of {key}: {len(value)}")

    df = pd.DataFrame(data)
    return df

def upload_to_database(data, img_binary):
    try:
        for i, row in data.iterrows():
            print("Inserting values:", tuple(row) + (img_binary,))
            sql = """
                INSERT INTO card_data (company_name, card_holder, designation, mobile_number, email, website, area, city, state, pin_code, image)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(sql, tuple(row) + (img_binary,))
            df['mobile_number'] = df['mobile_number'].str[:20]  # Trim to 20 characters

            # Print the trimmed value
            print("Trimmed mobile_number data:", df['mobile_number'])
            conn.commit()
            print("Upload Successfully!")
    except Exception as e:
        print("Error:", e)
        conn.rollback()

# Provide the path to your test image
image_path = r"C:/Users/LENOVO/Desktop/bizcard/uploaded_cards/2.jpg"

# Perform OCR
reader = easyocr.Reader(['en'])
result = reader.readtext(image_path, detail=0, paragraph=False)

# Update the function call to pass the image_path variable
data = get_data(result, image_path)
df = create_df(data)

# Upload to Database
img_binary = img_to_binary(image_path)
upload_to_database(df, img_binary)

# Close cursor and connection
cursor.close()
conn.close()

      
# Connect to PostgreSQL
conn = psycopg2.connect(
    host="localhost",
    user="postgres",
    password="080902",
    database="bizcard",
    port="5432",
)

# Create a cursor object
conn.autocommit = False  
cursor = conn.cursor()

os.environ['TESSDATA_PREFIX'] = r'C:/Program Files/Tesseract-OCR'
pytesseract.pytesseract.tesseract_cmd = r'C:/Program Files/Tesseract-OCR/tesseract.exe'

save_directory = "uploaded_cards"
if not os.path.exists(save_directory):
    os.makedirs(save_directory)

def img_to_binary(file):
    if file is not None:
        with open(file, 'rb') as file:
            binaryData = file.read()
        return binaryData
    else:
        return None
    

def extract_text_from_image(image_path):
    img = Image.open(image_path)
    custom_config = r'--oem 3 --psm 6 --tessdata-dir "C:/Program Files/Tesseract-OCR/tessdata"'
    text = pytesseract.image_to_string(img, config=custom_config)
    return text



def get_data(res):
    data = {
        "company_name": [],
        "card_holder": [],
        "designation": [],
        "mobile_number": [],
        "email": [],
        "website": [],
        "area": [],
        "city": [],
        "state": [],
        "pin_code": [],
    }
    for ind, i in enumerate(res):
        if "www " in i.lower() or "www." in i.lower():
            data["website"].append(i)
        elif "WWW" in i:
            data["website"] = res[4] + "." + res[5]
        elif "@" in i:
            data["email"].append(i)
        elif "-" in i:
            data["mobile_number"].append(i)
            if len(data["mobile_number"]) == 2:
                data["mobile_number"] = " & ".join(data["mobile_number"])
        elif ind == len(res) - 1:
            data["company_name"].append(i)
        elif ind == 0:
            data["card_holder"].append(i)
        elif ind == 1:
            data["designation"].append(i)
        if re.findall('^[0-9].+, [a-zA-Z]+', i):
            data["area"].append(i.split(',')[0])
        elif re.findall('[0-9] [a-zA-Z]+', i):
            data["area"].append(i)
        match1 = re.findall('.+St , ([a-zA-Z]+).+', i)
        match2 = re.findall('.+St,, ([a-zA-Z]+).+', i)
        match3 = re.findall('^[E].*', i)
        if match1:
            data["city"].append(match1[0])
        elif match2:
            data["city"].append(match2[0])
        elif match3:
            data["city"].append(match3[0])
        state_match = re.findall('[a-zA-Z]{9} +[0-9]', i)
        if state_match:
            data["state"].append(i[:9])
        elif re.findall('^[0-9].+, ([a-zA-Z]+);', i):
            data["state"].append(i.split()[-1])
        if len(data["state"]) == 2:
            data["state"].pop(0)
        if len(i) >= 6 and i.isdigit():
            data["pin_code"].append(i)
        elif re.findall('[a-zA-Z]{9} +[0-9]', i):
            data["pin_code"].append(i[10:])
    return data


def create_df(data):
    df = pd.DataFrame(data)
    return df


def upload_to_database(data, img_binary):
    try:
        for i, row in data.iterrows():
            # Print the values before inserting into the database
            print("Inserting values:", tuple(row) + (img_binary,))

            sql = """
                INSERT INTO card_data (company_name, card_holder, designation, mobile_number, email, website, area, city, state, pin_code, image)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(sql, tuple(row) + (img_binary,))
            df['mobile_number'] = df['mobile_number'].str[:20]  # Trim to 20 characters
            conn.commit()

            print("Upload successful for row:", i)
    except Exception as e:
        print("Error:", e)
        conn.rollback()

def upload_extract_page():
    st.title("Image Text Extraction App")
    uploaded_card = st.file_uploader("Choose an image...", type=["jpg", "png"])
    saved_img = None
    result = []

    if uploaded_card is not None:
        if st.button("Extract Text"):
            # Save the uploaded image temporarily
            with open(os.path.join(save_directory, uploaded_card.name), "wb") as f:
                f.write(uploaded_card.getbuffer())

            # Perform OCR
            reader = easyocr.Reader(['en'])
            saved_img = os.getcwd() + "\\" + "uploaded_cards" + "\\" + uploaded_card.name
            result = reader.readtext(saved_img, detail=0, paragraph=False)
            st.subheader("Extracted Text:")
            st.write("\n".join(result))

        col1, col2 = st.columns(2, gap="large")
        with col1:
            st.markdown("#     ")
            st.markdown("#     ")
            st.markdown("### You have uploaded the card")
            st.image(uploaded_card)

        with col2:
            st.markdown("#     ")
            st.markdown("#     ")
            with st.spinner("Please wait processing image..."):
                st.markdown("### Image Processed and Data Extracted")

        data = get_data(result)
        df = create_df(data)
        st.success("### Data Extracted!")
        st.write(df)

        if st.button("Upload to Database"):
            img_binary = img_to_binary(saved_img)
            upload_to_database(df, img_binary)

    # Close cursor and connection
    cursor.close()
    conn.close()


# # modify page creation

def modify_Page():
    st.title("Modify Page")

    try:
        with st.columns([3, 3, 2]) as (col1, col2, col3):
            col2.markdown("## Alter or Delete the data here")

            # Database Connection and Cursor
            with conn.cursor() as cursor:
                # Check if the 'card_data' table exists
                cursor.execute("SELECT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'card_data')")
                table_exists = cursor.fetchone()[0]

                if not table_exists:
                    st.warning("The 'card_data' table does not exist. Please create the table before using this page.")
                    return

                cursor.execute("SELECT card_holder FROM card_data")
                result = cursor.fetchall()
                business_cards = {row[0]: row[0] for row in result}

                with col1:
                    selected_card = st.selectbox("Select a card holder name to update", list(business_cards.keys()))
                    st.markdown("#### Update or modify any data below")

                    cursor.execute("""SELECT company_name, card_holder, designation, mobile_number, email, website, 
                                      area, city, state, pin_code FROM card_data WHERE card_holder=%s""", (selected_card,))
                    result = cursor.fetchone()

                    # Displaying All Information
                    company_name = st.text_input("Company_Name", result[0])
                    card_holder = st.text_input("Card_Holder", result[1])
                    designation = st.text_input("Designation", result[2])
                    mobile_number = st.text_input("Mobile_Number", result[3])
                    email = st.text_input("Email", result[4])
                    website = st.text_input("Website", result[5])
                    area = st.text_input("Area", result[6])
                    city = st.text_input("City", result[7])
                    state = st.text_input("State", result[8])
                    pin_code = st.text_input("Pin_Code", result[9])

                    if st.button("Commit changes to DB"):
                        # Update the information for the selected business card in the database
                        try:
                            cursor.execute("""UPDATE card_data SET company_name=%s, card_holder=%s, designation=%s,
                                              mobile_number=%s, email=%s, website=%s, area=%s, city=%s, state=%s,
                                              pin_code=%s WHERE card_holder=%s""",
                                           (company_name, card_holder, designation, mobile_number, email, website, area,
                                            city, state, pin_code, selected_card))
                            conn.commit()
                            st.success("Information updated in the database successfully.")
                        except psycopg2.Error as e:
                            conn.rollback()
                            st.warning(f"Error updating data: {e}")

                with col2:
                    selected_card = st.selectbox("Select a card holder name to Delete", list(business_cards.keys()))
                    st.write(f"### You have selected :green[**{selected_card}'s**] card to delete")
                    st.write("#### Proceed to delete this card?")

                    if st.button("Yes Delete Business Card"):
                        try:
                            cursor.execute("DELETE FROM card_data WHERE card_holder=%s", (selected_card,))
                            conn.commit()
                            st.success("Business card information deleted from the database.")
                        except psycopg2.Error as e:
                            conn.rollback()
                            st.warning(f"Error deleting data: {e}")

    except Exception as e:
        st.warning(f"An error occurred: {e}")

    if st.button("View updated data"):
        try:
            with conn.cursor() as cursor:
                cursor.execute("""SELECT company_name, card_holder, designation, mobile_number, email, website, 
                                  area, city, state, pin_code FROM card_data""")
                updated_df = pd.DataFrame(cursor.fetchall(),
                                          columns=["Company_Name", "Card_Holder", "Designation", "Mobile_Number", "Email",
                                                   "Website", "Area", "City", "State", "Pin_Code"])
                st.write(updated_df)
        except psycopg2.Error as e:
            st.warning(f"Error fetching updated data: {e}")


import mysql.connector
import streamlit as st

# Connect to PostgreSQL
conn = psycopg2.connect(
    host="localhost",
    user="postgres",
    password="080902",
    database="bizcard",
    port="5432",
)

# Create a cursor
cursor = conn.cursor()


# Main Page
def main():
    st.title("")
    cursor = conn.cursor()

    st.sidebar.title("Navigation")
    png = ["Home", "Upload and Extract",  "Modify Page"]
    selected_page = st.sidebar.radio("Navigation",png)

    if selected_page == "Home":
        home_page()
    elif selected_page == "Upload and Extract":
        upload_extract_page()
    elif selected_page == "Modify Page":
        modify_Page()
 
if __name__ == "__main__":
    main()    