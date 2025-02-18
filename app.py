# Imports
import openpyxl  # Required for Excel support
import streamlit as st
import pandas as pd
import os
from io import BytesIO


# Set up the app
st.set_page_config(page_title="💿 Data Cleaner", layout="wide")
st.title("💿 Data Cleaner")
st.write(
    "Transform your data between CSV and Excel with the ability to clean it along the way."
)

uploaded_files: list | None = st.file_uploader(
    "Upload CSV or Excel:",
    type=["csv", "xlsx"],
    accept_multiple_files=True,
)

if uploaded_files:
    for file in uploaded_files:
        file_ext: str = os.path.splitext(file.name)[-1].lower()

        if file_ext == ".csv":
            df = pd.read_csv(file)
        elif file_ext == "xlsx":
            df = pd.read_excel(file)
        else:
            st.error(f"Unsupported file type: {file_ext}")
            continue

        # Display info about the file.
        st.write(f"**File Name:** {file.name}")
        st.write(f"**File Size:** {file.size/1024}")

        # Preview first five rows
        st.write("Preview:")
        st.dataframe(df.head())

        # Cleaning options
        st.subheader("Cleaning Options")
        if st.checkbox(f"Clean {file.name}"):
            col1, col2 = st.columns(2)

            with col1:
                if st.button("Remove Duplicates"):
                    df.drop_duplicates(inplace=True)
                    st.write("Removed Duplicates")

            with col2:
                if st.button("Fill Missing Values"):
                    numeric_colums = df.select_dtypes(include=["number"]).columns
                    df[numeric_colums] = df[numeric_colums].fillna(
                        df[numeric_colums].mean()
                    )
                    st.write("Wrote Missing Values")

        # Choose columns to convert or clean
        st.subheader("Select Columns to Convert:")
        columns = st.multiselect(
            f"Chose columns for {file.name}:", df.columns, default=df.columns
        )
        df = df[columns]

        # Create Visualization:
        st.subheader("📊 Data Visualization")
        if st.checkbox(f"Show Visualization for {file.name}"):
            st.bar_chart(df.select_dtypes(include=["number"]).iloc[:, :2])

        # File conversion
        st.subheader("📄 Conversion Options")
        conversion_type = st.radio(
            f"Convert {file.name} to:",
            ["CSV", "Excel"],
            key=file.name,
        )
        if st.button("Convert"):
            buffer = BytesIO()
            if conversion_type == "CSV":
                df.to_csv(buffer, index=False)
                file_name: str = file.name.replace(file_ext, ".csv")
                mime_type: str = "text/csv"
            elif conversion_type == "Excel":
                df.to_excel(buffer, index=False)
                file_name: str = file.name.replace(file_ext, ".xlsx")
                mime_type: str = (
                    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
            buffer.seek(0)

            # Download Button
            st.download_button(
                label=f"⬇️ Download {file.name} as {conversion_type}",
                data=buffer,
                file_name=file_name,
                mime=mime_type,
            )

st.success("🚀 All actions completed! 🚀")
