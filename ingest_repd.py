import pandas as pd
import os

def ingest_repd_data():
    print("Fetching the latest UK Renewable Energy Planning Database...")
    
    # The public URL for the GOV.UK REPD dataset (April 2026 CSV extract)
    url = "https://assets.publishing.service.gov.uk/media/69fc56908cc72d2f863ea58d/REPD_publication_Q1_2026.csv"
    
    try:
        # Pandas can read a CSV directly from a URL!
        df = pd.read_csv(url, encoding='latin1') 
        
        # Clean the data: Drop rows that don't have geographic coordinates
        df_clean = df.dropna(subset=['X-coordinate', 'Y-coordinate'])
        
        # Save it locally into your new data folder
        output_path = os.path.join("data", "repd_cleaned.csv")
        df_clean.to_csv(output_path, index=False)
        
        print(f"Success! {len(df_clean)} renewable energy sites downloaded and saved to {output_path}.")
        
        # Print a quick preview of the columns for our documentation
        print("\nDataset Columns (Schema Preview):")
        print(list(df_clean.columns)[:10]) # Just showing the first 10 for now
        
    except Exception as e:
        print(f"Error fetching data: {e}")

if __name__ == "__main__":
    ingest_repd_data()