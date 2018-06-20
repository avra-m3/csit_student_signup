class OutputObject:
    """
    An abstract class describing the attributes a Output object should have.
    """
    # File path to the output csv file
    file = None
    # A List object containing the columns to write to the file, length must equal the rows field
    columns = None
    # A List object describing How each entry should be formatted
    rows = None
    # Only allow unique rows to be added to the output csv
    enforce_unique = None
    # If enforce_unique is set to true, the primary key field should be set to the value you want to be unique
    primary_key = None
    # The directory where images captured will be saved to.
    cache_dir = None