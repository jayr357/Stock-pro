import pandas as pd
import io

def convert_to_csv(df):
    """
    Convert a pandas DataFrame to CSV format.
    """
    csv_buffer = io.StringIO()
    df.to_csv(csv_buffer, index=True)
    return csv_buffer.getvalue()
