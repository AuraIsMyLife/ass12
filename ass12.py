import streamlit as st                                          # Import Streamlit for the web UI
import pandas as pd                                             # Import Pandas for map data formatting
from streamlit_gps_location import gps_location_button          # Import custom GPS capture button
from fpdf import FPDF                                           # Import FPDF class for PDF generation
from datetime import datetime                                   # Import datetime to timestamp reports
import os                                                       # Import os for temporary file cleanup

st.set_page_config(                                             # Configure Streamlit page settings
    page_title="Field Scientific Report",                       # Set the browser tab title
    layout="centered"                                           # Center the app layout on the screen
)                                                               # End of page configuration

st.title("Field Researcher App")                                # Display the main application title
st.write("Document and report a discovery in a structured...")  # Display instructions for the user

st.header("1. User Information")                                # Create a header for the user info section
name = st.text_input("Name of the researcher")                  # Input field for the researcher's name
discovery_title = st.text_input("Title of the discovery")       # Input field for the discovery title
description = st.text_area("Description / Notes")               # Text area for detailed observations

st.header("2. GPS Location")                                    # Create a header for the GPS section
st.write("Capture your current location coordinates.")          # Provide instructions for GPS capture
location_data = gps_location_button(label="Get my location")          # Button widget to trigger browser GPS

lat, lon = None, None                                           # Initialize coordinates as None
if location_data is not None:                                   # Check if GPS data was captured
    if location_data.get('latitude') is not None and \
       location_data.get('longitude') is not None:              # Verify both lat and lon exist
        lat = location_data['latitude']                         # Extract latitude value
        lon = location_data['longitude']                        # Extract longitude value
        
        st.success(f"Coordinates captured: Lat {lat}, Lon {lon}")# Display success message with coordinates
        
        map_data = pd.DataFrame({                               # Create a DataFrame for map rendering
            'lat': [lat],                                       # Insert latitude into DataFrame
            'lon': [lon]                                        # Insert longitude into DataFrame
        })                                                      # End of DataFrame creation
        st.subheader("Your location on the map")                # Create a subheader for the map display
        st.map(map_data)                                        # Render the map using the coordinates
else:                                                           # If location data is missing
    st.info("Press 'Get my location' to capture coordinates.")  # Prompt the user to use the GPS button

st.header("3. Visual Evidence")                                 # Create a header for the photo section
photo = st.camera_input("Take a photo of the discovery")        # Widget to capture images from the device camera

st.header("4. Generate Report")                                 # Create a header for report generation

if st.button("Generate Professional PDF Report"):               # Button to trigger the PDF generation process
    if not name or not discovery_title or not description:      # Validate that all text fields are filled
        st.error("Please fill in all User Information fields.") # Show error if text data is missing
    elif lat is None or lon is None:                            # Validate that GPS data was captured
        st.error("Please capture your GPS location.")           # Show error if coordinates are missing
    elif photo is None:                                         # Validate that a photo was taken
        st.error("Please take a photo as visual evidence.")     # Show error if image is missing
    else:                                                       # If all validation checks pass
        try:                                                    # Begin try block to handle potential PDF errors
            temp_image_path = "temp_photo.jpg"                  # Define a filename for the temporary photo
            with open(temp_image_path, "wb") as f:              # Open the temporary file in write-binary mode
                f.write(photo.getbuffer())                      # Write the camera image buffer to the file

            pdf = FPDF()                                        # Initialize a new PDF document object
            pdf.add_page()                                      # Add a blank page to the PDF
            
            pdf.set_font("Helvetica", "B", 18)                  # Set font for the main title (Bold, 18pt)
            pdf.cell(0, 10, "FIELD REPORT", align="C",          # Add the centered title string
                     new_x="LMARGIN", new_y="NEXT")             # Move the cursor to the next line
            pdf.ln(5)                                           # Add a 5mm vertical line break
            
            pdf.set_font("Helvetica", "", 12)                   # Set font for standard text (Regular, 12pt)
            curr_date = datetime.now().strftime("%d/%m/%Y")     # Format the current date as DD/MM/YYYY
            pdf.cell(0, 10, f"Date: {curr_date}",               # Add the date string to the document
                     new_x="LMARGIN", new_y="NEXT")             # Move the cursor to the next line
            
            pdf.cell(0, 10, f"Researcher: {name}",              # Add the researcher's name
                     new_x="LMARGIN", new_y="NEXT")             # Move the cursor to the next line
            pdf.cell(0, 10, f"Finding: {discovery_title}",      # Add the discovery title
                     new_x="LMARGIN", new_y="NEXT")             # Move the cursor to the next line
            pdf.cell(0, 10, f"Coordinates: Lat {lat}, Lon {lon}",# Add the geographic coordinates
                     new_x="LMARGIN", new_y="NEXT")             # Move the cursor to the next line
            pdf.ln(5)                                           # Add a 5mm vertical line break
            
            pdf.set_font("Helvetica", "B", 12)                  # Set font for the observations header (Bold)
            pdf.cell(0, 10, "Observations:",                    # Add the observations label
                     new_x="LMARGIN", new_y="NEXT")             # Move the cursor to the next line
            pdf.set_font("Helvetica", "", 12)                   # Revert to standard regular font
            pdf.multi_cell(0, 10, description)                  # Add the multi-line description text
            pdf.ln(5)                                           # Add a 5mm vertical line break
            
            pdf.image(temp_image_path, w=100)                   # Insert the temporary image file into the PDF
            
            pdf_bytes = bytes(pdf.output())                     # Compile the PDF and convert it to a byte string
            
            if os.path.exists(temp_image_path):                 # Check if the temporary image file still exists
                os.remove(temp_image_path)                      # Delete the temporary file to keep the folder clean

            st.success("Report generated successfully!")        # Display a success message to the user
            
            clean_title = discovery_title.replace(' ', '_')     # Replace spaces with underscores for the filename
            st.download_button(                                 # Render the Streamlit download button
                label="Download PDF",                           # Set the label displayed on the button
                data=pdf_bytes,                                 # Pass the raw PDF byte data
                file_name=f"{clean_title}_Report.pdf",          # Set the default filename for the user's download
                mime="application/pdf",                         # Specify the MIME type so the browser knows it's a PDF
                use_container_width=True                        # Stretch the button to fit the column width
            )                                                   # End of download button configuration
            
        except Exception as e:                                  # Catch any errors that occur during generation
            st.error(f"An error occurred generating PDF: {e}")  # Display the specific error message to the user