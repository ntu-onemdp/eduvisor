import pandas as pd

class WhitelistFileProcessor:
    """Handles the processing of whitelist files."""

    @staticmethod
    def extract_emails_from_file(uploaded_file):
        """
        Extracts student emails from the uploaded CSV file.
        
        Args:
            uploaded_file (str): Path to the uploaded CSV file.

        Returns:
            list: A list of extracted email addresses.
        """
        emails = []
        try:
            # read the CSV file into a DataFrame
            df = pd.read_csv(uploaded_file, header=None, dtype=str)
            
            # find the row containing "Name" and extract emails from column 5
            name_row_index = df[df.iloc[:, 1].str.contains("Name", na=False)].index[0]
            print('name')
            print(name_row_index)
            emails = df.iloc[name_row_index + 1:, 5].dropna().tolist()
            print(emails)
            
        except Exception as e:
            # log or handle exceptions 
            print(f"Error processing whitelist file: {e}")
        
        return emails
    

