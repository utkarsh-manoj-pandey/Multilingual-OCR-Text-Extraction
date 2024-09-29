import streamlit as st
from PIL import Image, ImageEnhance
import pytesseract
import re
import pyperclip
from langdetect import detect, LangDetectException

# Set Tesseract path (adjust this as per your system's path)
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# Set the page config with a title, icon, and wide layout
st.set_page_config(page_title="Multilingual OCR", page_icon="📄", layout='wide')

# Sidebar: User Control Panel
st.sidebar.header("Control Panel ⚙️")
text_size = st.sidebar.slider("Adjust Text Size", 12, 24, 16)
highlight_color = st.sidebar.color_picker("Highlight Color for Search Results", "#FFDD57")
feedback = st.sidebar.text_area("Feedback/Comments", placeholder="Let us know your thoughts!")
if st.sidebar.button("Submit Feedback"):
    st.sidebar.success("Thanks for your feedback!")

# Sidebar: Theme Color Picker
primary_color = st.sidebar.color_picker("Pick a primary color", "#00ADB5")

# Language selection dropdown for OCR
st.sidebar.subheader("Select OCR Language")
languages = {
    "English": "eng",
    "Hindi": "hin",
    "French": "fra",
    "Spanish": "spa",
    "German": "deu",
    "Chinese (Simplified)": "chi_sim",
    "Japanese": "jpn",
    "Korean": "kor",
}
selected_languages = st.sidebar.multiselect(
    "Choose language(s) for OCR", options=list(languages.keys()), default=["English", "Hindi"]
)

# Convert selected languages to the corresponding Tesseract language code
ocr_langs = "+".join([languages[lang] for lang in selected_languages])

# Define colors for light mode (no dark mode)
bg_color = "#FFFFFF"
text_color = "#000000"
card_bg = "#F8F9FA"
secondary_color = "#EEEEEE"
button_bg = "#007BFF"
button_hover = "#0056b3"

# Custom CSS for modern UI with dynamic colors and transitions
st.markdown(f"""
    <style>
    body {{
        background-color: {bg_color};
        color: {text_color};
        font-family: 'Helvetica', sans-serif;
        transition: background-color 0.3s, color 0.3s;
    }}

    /* Styling headers */
    .header {{
        text-align: center;
        font-size: 3em;
        color: {primary_color};
    }}
    
    /* Card container */
    .card {{
        background-color: {card_bg};
        border-radius: 15px;
        padding: 20px;
        margin: 15px 0;
        box-shadow: 0 6px 12px rgba(0, 0, 0, 0.3);
        transition: transform 0.3s ease;
    }}
    .card:hover {{
        transform: scale(1.02);
    }}

    /* Button styling */
    .stButton>button {{
        background-color: {button_bg};
        color: {text_color};
        border: none;
        border-radius: 12px;
        padding: 12px 24px;
        font-size: 1.2em;
        box-shadow: 0 4px 10px rgba(0, 0, 0, 0.3);
        transition: all 0.3s ease;
    }}
    .stButton>button:hover {{
        background-color: {button_hover};
        transform: translateY(-2px);
    }}

    /* Footer */
    .footer {{
        text-align: center;
        margin-top: 40px;
        color: {primary_color};
        font-size: 1.1em;
    }}
    
    /* Highlighted text */
    mark {{
        background-color: {highlight_color};
        color: black; /* Ensures contrast against highlight */
    }}
    </style>
    """, unsafe_allow_html=True
)

# Main title
st.markdown(f"<h1 class='header'>📄 Multilingual OCR Text Extraction</h1>", unsafe_allow_html=True)

# Preprocessing for better OCR results
def preprocess_image(image):
    img = Image.open(image).convert('L')
    enhancer = ImageEnhance.Contrast(img)
    img = enhancer.enhance(2)
    return img

# Improved Language Detection Function
def detect_language(text):
    try:
        lang = detect(text)
    except LangDetectException:
        lang = "Unknown"
    return lang

# Extract text with multi-language support
def extract_text_multilingual(images, ocr_langs):
    extracted_texts = []
    for image in images:
        img = preprocess_image(image)
        
        # OCR with user-selected language support
        try:
            text = pytesseract.image_to_string(img, lang=ocr_langs)
        except Exception as e:
            st.error(f"An error occurred while processing the image: {e}")
            continue
        
        # Detect language
        detected_lang = detect_language(text)
        
        extracted_texts.append((text.strip(), detected_lang))
    return extracted_texts

# Copy to clipboard function
def copy_to_clipboard(text):
    pyperclip.copy(text)
    st.success("Text copied to clipboard!")

# Main Workflow: Upload, Extract, Display, and Search
st.subheader("Upload Image(s) for OCR")
uploaded_files = st.file_uploader("Choose image files", type=["jpg", "jpeg", "png"], accept_multiple_files=True)

if uploaded_files:
    st.image([Image.open(f) for f in uploaded_files], caption=[f.name for f in uploaded_files], use_column_width=True)

    if st.button("Start Text Extraction"):
        with st.spinner("Processing images..."):
            extracted_texts = extract_text_multilingual(uploaded_files, ocr_langs)
            st.session_state["extracted_texts"] = extracted_texts
            st.success("Text extracted successfully!")

# Display Results and Implement Search Functionality
if "extracted_texts" in st.session_state:
    st.subheader("Extracted Texts and Search")
    
    search_query = st.text_input("Enter a keyword to search within the extracted text")

    for idx, (text, lang) in enumerate(st.session_state["extracted_texts"]):
        st.markdown(f"<div class='card'><h4>Image {idx + 1} (Detected Language: {lang.capitalize()})</h4><p style='font-size: {text_size}px; color: {text_color};'>{text if text else 'No text detected'}</p></div>", unsafe_allow_html=True)

        # Copy text to clipboard
        if st.button(f"Copy Text from Image {idx + 1}"):
            copy_to_clipboard(text)

        # Download as text file
        st.download_button(label="Download as Text File", data=text, file_name=f"extracted_text_image_{idx+1}.txt", mime="text/plain")
        
        # Highlight search results
        if search_query:
            highlighted_text = re.sub(f"({search_query})", r"<mark>\1</mark>", text, flags=re.IGNORECASE)
            st.markdown(f"<p style='font-size: {text_size}px; color: {text_color};'>{highlighted_text}</p>", unsafe_allow_html=True)

# Footer
st.markdown("<div class='footer'>© 2024 Multilingual OCR Tool | Designed with ❤️</div>", unsafe_allow_html=True)
