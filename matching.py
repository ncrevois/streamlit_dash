## all the functions to run the matching 
import re 
import pandas as pd 
import numpy as np
from typing import Literal

BRAND_LIST = set([
    "apple", "asus", "dell", "google", "hp", "lenovo", "lexmark", "microsoft", 
    "samsung", "seagate", "climaveneta", "checkpoint", "cisco", "fujitsu",
    "palo alto", "schneider", "sdmo", "socomec", "trane", "toshiba", "vertiv"
])

def preprocess_function(name: str, type: Literal['model', 'brand']) -> str:
    """Preprocess the provided name string to make it easier to compare."""
    # Remove special characters and convert to lowercase
    name_words = re.sub(r"[^a-zA-Z0-9+]+", " ", name).strip().lower().split()

    if type == 'model':
        # Remove brand names for model comparison
        name_words = [word for word in name_words if word not in BRAND_LIST]

    return " ".join(name_words)

def get_matching_score(inventory_name: str, reference_name: str) -> float:
    """Make a score ranging from 0.0 to 1.0 to determine if the two given model name strings seem to be the same model,
    based on the identical word count in each string.
    This score is the ratio of the smallest identical word count to the highest.
    For instance, "proedge 2023 xd" and "proedge 2023" would get a 2/3 = 0.6667 matching score;
    "proedge 2023 xd" and "pro 2023" would get a 0.0 matching score; and
    "proedge 2023 xd" and "proedge 2023 xd" would get a 1.0 matching score.
    :param inventory_model_name: The first string to compare
    :param reference_model_name: The second string to compare
    """

    if inventory_name == reference_name:
        return 1.0

    inventory_words = inventory_name.split(" ")
    reference_words = reference_name.split(" ")

    if len(inventory_words) < len(reference_words):
        lower_word_count_list = inventory_words
        higher_word_count_list = reference_words

    else:
        lower_word_count_list = reference_words
        higher_word_count_list = inventory_words
        
    # Check if all words in the smaller list are in the larger list
    if all(word in higher_word_count_list for word in lower_word_count_list):
        return len(lower_word_count_list) / len(higher_word_count_list)

    return 0.0

def get_matching(inventory_model, inventory_brand, inventory_category, references_df):
    max_score = 0
    best_reference_model = None
    best_reference_brand = None
    co2_final = 0
    
    if pd.isna(inventory_model) or inventory_model is None:
        return('', max_score, co2_final, "No Match")
    
    ##check for match with model 
    # Preprocess the inventory model
    inventory_model_preprocessed = preprocess_function(str(inventory_model), 'model')
    
    # Compare with each value in references_df.model
    for _, ref_row in references_df.iterrows():
        reference_model = ref_row['ds_asset_model']
        co2 = ref_row['val_pcf_total_emission_kgco2eq']
        # Preprocess the reference model
        reference_model_preprocessed = preprocess_function(str(reference_model), 'model') 

        # Compute the score
        score = get_matching_score(inventory_model_preprocessed, reference_model_preprocessed)

        if score == 1: 
            return(reference_model, score, co2, 'M0')

        # Update the best match if this score is higher
        if score > max_score:
            max_score = score
            best_reference_model = reference_model
            co2_final = co2
    
    
    if max_score != 0 :
        return(best_reference_model, max_score, co2, 'M0')
    
    ## Check for match with brand 
    else: 
        inventory_brand_preprocessed = preprocess_function(str(inventory_brand), 'brand')
        brands_grouped_df = references_df.groupby(['cd_asset_category', 'ds_manufacturer'], as_index=False).val_pcf_total_emission_kgco2eq.mean()
        
        if (inventory_category, inventory_brand) in set(zip(brands_grouped_df['cd_asset_category'], brands_grouped_df['ds_manufacturer'])):  ## ensure the category exists in our references
            for reference_brand in set(brands_grouped_df.ds_manufacturer): 
                reference_brand_preprocessed = preprocess_function(str(reference_brand), 'brand')
                score = get_matching_score(inventory_brand_preprocessed, reference_brand_preprocessed)

                if score == 1: #perfect match 
                    co2 = brands_grouped_df[(brands_grouped_df.cd_asset_category == inventory_category)&(brands_grouped_df.ds_manufacturer == reference_brand)].val_pcf_total_emission_kgco2eq.values[0]
                    return(reference_brand, score, co2, 'M2')

                # Update the best match if this score is higher
                if score > max_score: #find the best match 
                    max_score = score
                    best_reference_brand = reference_brand
                    co2_final = brands_grouped_df[(brands_grouped_df.cd_asset_category == inventory_category)&(brands_grouped_df.ds_manufacturer == reference_brand)].val_pcf_total_emission_kgco2eq.values[0]
            
           
            if max_score != 0: #return best brand match if a match was found 
                return(best_reference_brand, max_score, co2_final, "M2")

        #no brand match was found, use category --> M3 
        if inventory_category in set(brands_grouped_df.cd_asset_category): 
            categories_grouped_df = references_df.groupby(['cd_asset_category'], as_index=False).val_pcf_total_emission_kgco2eq.mean()
            co2_final = categories_grouped_df[(categories_grouped_df.cd_asset_category == inventory_category)].val_pcf_total_emission_kgco2eq.values[0]
            max_score = 1 
            return(inventory_category, max_score, co2_final, "M3")

        else: # the category doesn't exist in the references --> No Match  
            return('', max_score, co2_final, "No Match")
    

#run through the whole clients' assets dataset 
def get_matchings(df, references_df): 
    results = []
    i = 0
    for _, row in df.iterrows():
        #print("row['model']", row['model'], "row['manufacturer']", row['manufacturer'],"row['category']", row['category'])
        best_reference, max_score, co2_final, matching_type = get_matching(row['model'], row['manufacturer'],row['category'], references_df)
        results.append([
            row['category'], row['manufacturer'], row['model'], 
            best_reference, float(max_score), matching_type, int(row['device_instances']), 
            float(co2_final), row['clients']
        ])
        i+=1 
        
        if i % 500 == 0: 
            print(i)
            
    results_df = pd.DataFrame(results, columns=[
        'category', 'manufacturer', 'inventory_model', 'reference_model', 
        'score', 'matching_type', 'device_instances', 'co2', 'clients'
    ])

    return(results_df)