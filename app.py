# Imports
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
    # Store dataframes in session state, keyed by filename
    if "dataframes" not in st.session_state:
        st.session_state["dataframes"] = {}

    for file in uploaded_files:
        file_ext: str = os.path.splitext(file.name)[-1].lower()

        if file_ext == ".csv":
            try:
                df = pd.read_csv(file)
            except Exception as e:
                st.error(f"Error reading CSV file: {e}")
                continue
        elif file_ext == "xlsx":
            try:
                df = pd.read_excel(file)
            except Exception as e:
                st.error(f"Error reading Excel file: {e}")
                continue
        else:
            st.error(f"Unsupported file type: {file_ext}")
            continue

        # Store the original dataframe in session state
        if file.name not in st.session_state["dataframes"]:
            st.session_state["dataframes"][file.name] = df.copy()

        # Get the dataframe from session state
        df = st.session_state["dataframes"][file.name]

        # Display info about the file.
        st.write(f"**File Name:** {file.name}")
        st.write(f"**File Size:** {file.size / 1024:.2f} KB")

        # Preview first five rows
        st.write("Preview")
        st.dataframe(df.head())

        # Data Summary Statistics
        st.subheader("Summary Statistics")
        st.write(df.describe())

        # Data Filtering
        st.subheader("Data Filtering")
        filter_column = st.selectbox(
            "Select column to filter", df.columns, key=f"filter_column_{file.name}"
        )
        filter_value = st.text_input(
            "Enter value to filter", key=f"filter_value_{file.name}"
        )
        if st.button("Apply Filter", key=f"apply_filter_{file.name}"):
            try:
                df = df[df[filter_column] == filter_value]
                st.session_state["dataframes"][
                    file.name
                ] = df.copy()  # Update in session state
                st.write("Filtered Data:")
                st.dataframe(df)
            except KeyError:
                st.error(
                    "Invalid filter value. Please check the column and value entered."
                )

        # Cleaning options
        st.subheader("Cleaning Options")
        if st.checkbox(f"Clean {file.name}", key=f"clean_checkbox_{file.name}"):
            col1, col2 = st.columns(2)

            with col1:
                if st.button("Remove Duplicates", key=f"remove_duplicates_{file.name}"):
                    try:
                        df.drop_duplicates(inplace=True)
                        st.session_state["dataframes"][
                            file.name
                        ] = df.copy()  # Update in session state
                        st.write("Removed Duplicates")
                    except Exception as e:
                        st.error(f"Error removing duplicates: {e}")

            with col2:
                if st.button("Fill Missing Values", key=f"fill_missing_{file.name}"):
                    try:
                        numeric_colums = df.select_dtypes(include=["number"]).columns
                        df[numeric_colums] = df[numeric_colums].fillna(
                            df[numeric_colums].mean()
                        )
                        st.session_state["dataframes"][
                            file.name
                        ] = df.copy()  # Update in session state
                        st.write("Filled Missing Values")
                    except Exception as e:
                        st.error(f"Error filling missing values: {e}")

        # Column Renaming
        st.subheader("Rename Columns")
        columns_to_rename = st.multiselect(
            "Select columns to rename", df.columns, key=f"rename_select_{file.name}"
        )
        new_column_names = st.text_input(
            "Enter new column names (comma separated)", key=f"rename_input_{file.name}"
        )
        if st.button("Rename Columns", key=f"rename_button_{file.name}"):
            new_column_names_list = new_column_names.split(",")
            if len(columns_to_rename) == len(new_column_names_list):
                try:
                    df.rename(
                        columns=dict(zip(columns_to_rename, new_column_names_list)),
                        inplace=True,
                    )
                    st.session_state["dataframes"][
                        file.name
                    ] = df.copy()  # Update in session state
                    st.write("Renamed Columns")
                except Exception as e:
                    st.error(f"Error renaming columns: {e}")
            else:
                st.error(
                    "Number of new column names must match the number of selected columns"
                )

        # Choose columns to convert or clean
        st.subheader("Select Columns to Convert:")
        columns = st.multiselect(
            f"Chose columns for {file.name}:",
            df.columns,
            default=df.columns,
            key=f"convert_select_{file.name}",
        )
        df = df[columns]
        st.session_state["dataframes"][file.name] = df.copy()  # Update in session state

        # Create Visualization:
        st.subheader("📊 Data Visualization")
        if st.checkbox(
            f"Show Visualization for {file.name}",
            key=f"visualization_checkbox_{file.name}",
        ):
            try:
                st.bar_chart(df.select_dtypes(include=["number"]).iloc[:, :2])
            except Exception as e:
                st.error(f"Error creating visualization: {e}")

        # File conversion
        st.subheader("📄 Conversion Options")
        conversion_type = st.radio(
            f"Convert {file.name} to:",
            ["CSV", "Excel"],
            key=f"conversion_{file.name}",
        )
        if st.button("Convert", key=f"convert_button_{file.name}"):
            try:
                buffer = BytesIO()
                if conversion_type == "CSV":
                    df.to_csv(buffer, index=False)
                    file_name: str = file.name.replace(file_ext, ".csv")
                    mime_type: str = "text/csv"
                elif conversion_type == "Excel":
                    df.to_excel(buffer, index=False, engine="openpyxl")
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
                    key=f"download_{file.name}",
                )
                st.success("🚀 File conversion and download successful! 🚀")
            except Exception as e:
                st.error(f"Error during conversion or download: {e}")
