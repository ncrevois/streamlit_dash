import streamlit as st
import pandas as pd
import os
from matching import *
from plots import *
import sys

# Set the page config
st.set_page_config(
    page_title="Matching Dashboard",
    page_icon=":bar_chart:",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state variables
if 'client_assets' not in st.session_state:
    st.session_state.client_assets = pd.DataFrame()
if 'references_df' not in st.session_state:
    st.session_state.references_df = pd.DataFrame()
if 'results_df' not in st.session_state:
    st.session_state.results_df = pd.DataFrame()
if 'results_df_all' not in st.session_state:
    st.session_state.results_df_all = pd.DataFrame()
if 'update_triggered' not in st.session_state:
    st.session_state.update_triggered = False

# Define the path to the logo
logo_path = os.path.join(os.path.dirname(__file__), "assets", "Sopht_logo.png")
# Add your logo at the top
st.image(logo_path, width=150) 

## DEFINE FUNCTIONS
# Function to recompute metrics given new values in the reference tables were added
def update_results():
    updated_dict = st.session_state.references_editor

    added_rows = st.session_state.references_editor.get('added_rows', [])
    print("added_rows", added_rows)
    # Find new rows in references_df
    new_ref_rows = pd.DataFrame(added_rows, columns=st.session_state.references_df.columns)

    if not new_ref_rows.empty:
        # Get unmatched devices
        unmatched_devices = st.session_state.results_df[st.session_state.results_df.matching_type != "M0"]
        print("unmatched_devices", len(unmatched_devices))

        filtered_client_assets = st.session_state.client_assets[st.session_state.client_assets['model'].isin(unmatched_devices['inventory_model'])]

        # Perform matching only on new rows and unmatched devices
        new_matches = get_matchings(filtered_client_assets, new_ref_rows)
        new_matches = new_matches[new_matches.matching_type == "M0"]

        print("new_matches", new_matches)

        # Update table results_df with new matched rows
        for _, row in new_matches.iterrows():
            inventory_model = row['inventory_model']
            manufacturer = row['manufacturer']

            # Create a boolean mask for filtering
            mask = (st.session_state.results_df['inventory_model'] == inventory_model) & \
                (st.session_state.results_df['manufacturer'] == manufacturer)

            # Update the rows matching the mask
            st.session_state.results_df.loc[mask, 'reference_model'] = row['reference_model']
            st.session_state.results_df.loc[mask, 'co2'] = row['co2']
            st.session_state.results_df.loc[mask, 'score'] = row['score']
            st.session_state.results_df.loc[mask, 'matching_type'] = row['matching_type']

        # Update the references_df in session state
        new_refs_df = pd.concat([st.session_state.references_df, new_ref_rows], ignore_index=True)
        st.session_state.references_df = new_refs_df

        # Check updates successfully
        st.session_state.update_triggered = True

    else:
        st.write("No new values were added to the reference table.")

def lower_case(word):
    return(word.lower())

# Add a title and description
st.markdown(f"<h1 style='color: #d7ffcd;'>Matching Dashboard</h1>", unsafe_allow_html=True)
st.markdown("""
This dashboard provides insights into the CO2 emissions associated with various devices. 
You can view unmatched devices, check metrics, and update reference tables.
""")

# Upload data
uploader1, uploader2 = st.columns(2)
with uploader1:
    client_assets_file = st.file_uploader("Upload a clients' assets file.")

with uploader2:
    reference_file = st.file_uploader("Upload a reference file.")

if reference_file is not None and client_assets_file is not None:

    # Add a "Run" button
    run_button = st.button("Run")

    if run_button:
        # Define the dataframes
        st.session_state.client_assets = pd.read_csv(client_assets_file).fillna("NULL")
        st.session_state.client_assets_grouped = client_assets_grouped = st.session_state.client_assets.groupby(['manufacturer', 'model', 'category']).agg({
            'device_instances': 'sum',
            'client': lambda x: ', '.join(x.unique())
        }).reset_index().rename(columns={'client': 'clients'})
        st.session_state.references_df = pd.read_csv(reference_file)

        with st.spinner('Computing the metrics... This will take a few minutes... Come back a bit later...'):
            st.session_state.results_df_all = get_matchings(st.session_state.client_assets_grouped, st.session_state.references_df).sort_values(by="device_instances", ascending=False, ignore_index=True)

    if 'results_df_all' in st.session_state:

        client_options = ['All clients'] + st.session_state.client_assets['client'].unique().tolist()

        selected_client = st.selectbox('Select a client:', client_options) 

        # Filter the results_df if a specific client is selected
        if selected_client != 'All clients':
            st.session_state.results_df = st.session_state.results_df_all[
                st.session_state.results_df_all['clients'].str.contains(selected_client)
            ]

            # Replace device_instances with original values from df if a specific client is selected
            original_df_filtered = st.session_state.client_assets[
                st.session_state.client_assets['client'] == selected_client
            ]

            # Rename 'model' to 'inventory_model' in original_df_filtered
            original_df_filtered = original_df_filtered.rename(columns={'model': 'inventory_model'})

            # Join the original device_instances to the filtered results
            st.session_state.results_df = st.session_state.results_df.merge(
                original_df_filtered[['manufacturer', 'inventory_model', 'category', 'device_instances']],
                on=['manufacturer', 'inventory_model', 'category'],
                suffixes=('', '_original')
            )


            # Replace the summed device_instances with the original device_instances
            st.session_state.results_df['device_instances'] = st.session_state.results_df['device_instances_original']
            st.session_state.results_df.drop(columns=['device_instances_original'], inplace=True)
            st.session_state.results_df['clients'] = selected_client

        else: 
            st.session_state.results_df = st.session_state.results_df_all 


        # Data editor
        st.markdown("<hr>", unsafe_allow_html=True)  # Horizontal line
        st.markdown(f"<h3 style='color: #d7ffcd;'>Reference Table</h3>", unsafe_allow_html=True)
        st.data_editor(
            st.session_state.references_df,
            num_rows="dynamic",
            key="references_editor"
        )

        # Rerun button
        st.session_state.update_triggered = False
        if st.button("Rerun"):
            with st.spinner('Updating results...'):
                update_results()

        # Check if update was triggered and show a success message
        if st.session_state.get('update_triggered', False):
            st.success("Results updated successfully!")
            st.session_state.update_triggered = False

        st.markdown("---")  # Horizontal separator

        st.write("**Note:** Updates to the reference table will be reflected in the metrics and unmatched devices displayed above.")

        # Layout of the clients' devices dataset with multiple filters
        st.markdown(f"<h3 style='color: #d7ffcd;'>All Clients' Devices</h3>", unsafe_allow_html=True)
        filt1, filt2, filt3 = st.columns(3)

        with filt1:
            categories_input = st.text_input("CATEGORY", value="", placeholder="e.g., category1, category2")

        with filt2:
            manufacturers_input = st.text_input("MANUFACTURER", value="", placeholder="e.g., manufacturer1, manufacturer2")

        with filt3:
            clients_input = st.text_input("CLIENTS", value="", placeholder="e.g., client1, client2")

        st.write("Filter by Matching type: ")
        st.write("(M0: perfect match, M1: match by previous/next generation (WIP), M2: match by brand, category, M3: match by category, No Match)")

        match1, match2, match3, match4, match5 = st.columns(5)

        with match1:
            m0_checked = st.checkbox("M0", value=True)
        with match2:
            m1_checked = st.checkbox("M1", value=True)
        with match3:
            m2_checked = st.checkbox("M2", value=True)
        with match4:
            m3_checked = st.checkbox("M3", value=True)
        with match5:
            no_match_checked = st.checkbox("No Match", value=True)

        # Apply filters
        filtered_df = st.session_state.results_df.copy()

        if categories_input:
            filter_categories = [cat.strip().lower() for cat in categories_input.split(',')]
            filtered_df = filtered_df[filtered_df['category'].apply(lower_case).isin(filter_categories)]

        if manufacturers_input:
            filter_manufacturers = [manuf.strip().lower() for manuf in manufacturers_input.split(',')]
            filtered_df = filtered_df[filtered_df['manufacturer'].apply(lower_case).isin(filter_manufacturers)]

        if clients_input:
            filter_clients = [client.strip().lower() for client in clients_input.split(',')]
            filtered_df = filtered_df[filtered_df['clients'].apply(
                lambda x: any(client in [cl.strip().lower() for cl in x.split(',')] for client in filter_clients)
            )]

        selected_filters = []
        if m0_checked:
            selected_filters.append("M0")
        if m1_checked:
            selected_filters.append("M1")
        if m2_checked:
            selected_filters.append("M2")
        if m3_checked:
            selected_filters.append("M3")
        if no_match_checked:
            selected_filters.append("No Match")

        if selected_filters:
            filtered_df = filtered_df[filtered_df['matching_type'].isin(selected_filters)]

        # Calculate percentage of devices shown
        total_devices = len(st.session_state.results_df)
        filtered_devices = len(filtered_df)
        percentage_shown = (filtered_devices / total_devices) * 100 if total_devices > 0 else 0

        devices_shown1, devices_shown2 = st.columns(2)
        with devices_shown1:
            st.markdown(f"***{filtered_devices}** devices shown*")

        with devices_shown2:
            st.markdown(f"*{percentage_shown:.2f}% of total devices*")

        # Display filtered dataframe
        st.dataframe(filtered_df.sort_values(by="device_instances", ascending=False, ignore_index=True))

        ## Show updated plots with filtered data

        # Generate and get the plot as a BytesIO object
        buf1 = generate_plots(filtered_df, 'count')
        buf2 = generate_plots(filtered_df, 'sum')
        buf3 = generate_plots(filtered_df, 'co2')

        # Show plots
        st.image(buf1, use_column_width=True)
        st.image(buf2, use_column_width=True)
        st.image(buf3, use_column_width=True)

        print("successful run!")
