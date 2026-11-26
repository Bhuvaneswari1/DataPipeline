import pandas as pd

def read_orders(file_path):
    """
    Reads order data from a CSV file and returns a DataFrame.

    Parameters:
    file_path (str): The path to the CSV file containing order data.

    Returns:
    pd.DataFrame: A DataFrame containing the order data.
    """
    try:
        #orders_df = pd.read_csv(file_path)
        orders = pd.read_csv(file_path)

        preview = orders.head(5)
        shape = orders.shape
        laptops = orders.loc[orders["product"] == "Laptop"]

        return preview, shape, laptops

    except FileNotFoundError:
        print(f"Error: The file at {file_path} was not found.")
        return None
    except pd.errors.EmptyDataError:
        print("Error: The file is empty.")
        return None
    except pd.errors.ParserError:
        print("Error: There was a parsing error while reading the file.")
        return None

print(read_orders("data/orders.csv"))