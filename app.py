import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import pandas as pd
import os
import io
import zipfile
import tempfile

# ---------------- FONT ----------------
def load_bold_font(size):
    try:
        fonts = [
            "Arial-Bold.ttf", "ArialBD.ttf",
            "DejaVuSans-Bold.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
            "C:\\Windows\\Fonts\\arialbd.ttf"
        ]
        for f in fonts:
            try:
                return ImageFont.truetype(f, size=size)
            except:
                continue
        return ImageFont.load_default()
    except:
        return ImageFont.load_default()


# ---------------- POSITION ----------------
def get_centered_position(text, font, y, width):
    bbox = font.getbbox(text)
    text_width = bbox[2] - bbox[0]
    return ((width - text_width) // 2, y)


# ---------------- PREVIEW ----------------
def preview_template(template, name, business, font, positions):
    img = template.copy()
    draw = ImageDraw.Draw(img)

    name_pos = get_centered_position(name, font, positions['name_y'], template.width)
    business_pos = get_centered_position(f"({business})", font, positions['business_y'], template.width)

    draw.text(name_pos, name, fill="black", font=font)
    draw.text(business_pos, f"({business})", fill="black", font=font)

    return img


# ---------------- GENERATION ----------------
def generate_birthday_cards(df, templates, font_size, template_positions):
    zip_buffer = io.BytesIO()

    with tempfile.TemporaryDirectory() as output_dir:
        font = load_bold_font(font_size)

        progress = st.progress(0)
        status = st.empty()

        for i, row in df.iterrows():
            status.text(f"{i+1}/{len(df)} → {row['Owner Name']}")

            idx = i % len(templates)
            template = templates[idx]
            positions = template_positions[idx]

            name = row['Owner Name']
            business = row['Business Name']

            img = template.copy()
            draw = ImageDraw.Draw(img)

            name_pos = get_centered_position(name, font, positions['name_y'], template.width)
            business_pos = get_centered_position(f"({business})", font, positions['business_y'], template.width)

            draw.text(name_pos, name, fill="black", font=font)
            draw.text(business_pos, f"({business})", fill="black", font=font)

            path = os.path.join(output_dir, f"{business.replace(' ', '_')}.png")
            img.save(path)

            progress.progress((i + 1) / len(df))

        with zipfile.ZipFile(zip_buffer, 'w') as z:
            for root, _, files in os.walk(output_dir):
                for f in files:
                    z.write(os.path.join(root, f), f)

    return zip_buffer


# ---------------- UI ----------------
st.set_page_config(layout="wide")
st.title("🎂 Card Generator")

excel_file = st.file_uploader("Upload Excel (.xlsx)", type=["xlsx"])
template_files = st.file_uploader("Upload Templates", type=["png", "jpg"], accept_multiple_files=True)

font_size = st.slider("Font Size", 10, 150, 25)

# ✅ KEY FEATURE
sync_text = st.checkbox("🔗 Move both texts together (single slider)")

templates = []
template_positions = []

if template_files:
    for i, file in enumerate(template_files):
        img = Image.open(file)
        templates.append(img)

        st.markdown(f"### Template {i+1}")

        # Base positions (original defaults)
        base_name_y = 590 if img.height > 590 else img.height // 2
        base_business_y = 700 if img.height > 700 else img.height // 2

        if sync_text:
            # ✅ SINGLE SLIDER CONTROLS BOTH TEXTS
            offset = st.slider(
                f"Move Text Block (Template {i+1})",
                min_value=-300,
                max_value=300,
                value=0,
                step=1,
                key=f"sync_{i}"
            )

            name_y = base_name_y + offset
            business_y = base_business_y + offset

        else:
            # ✅ ORIGINAL BEHAVIOR
            col1, col2 = st.columns(2)

            with col1:
                name_y = st.slider(
                    f"Name Position (T{i+1})",
                    0, img.height,
                    base_name_y,
                    key=f"name_{i}"
                )

            with col2:
                business_y = st.slider(
                    f"Business Position (T{i+1})",
                    0, img.height,
                    base_business_y,
                    key=f"business_{i}"
                )

        template_positions.append({
            "name_y": name_y,
            "business_y": business_y
        })

        # Preview
        font = load_bold_font(font_size)
        preview = preview_template(
            img,
            "Happy Birthday",
            "My Business",
            font,
            {"name_y": name_y, "business_y": business_y}
        )
        st.image(preview, width=300)


# ---------------- GENERATE ----------------
if excel_file and templates:
    if st.button("Generate Cards"):
        df = pd.read_excel(excel_file)

        if not {'Owner Name', 'Business Name'}.issubset(df.columns):
            st.error("Excel must contain required columns")
        else:
            zip_buffer = generate_birthday_cards(
                df,
                templates,
                font_size,
                template_positions
            )

            st.download_button(
                "Download ZIP",
                zip_buffer.getvalue(),
                "cards.zip"
            )