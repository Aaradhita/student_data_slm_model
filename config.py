"""
Configuration Module
Define which dataset and table to use
"""

class DatasetConfig:
    """Configuration for the current dataset"""
    
    # Database configuration
    DATABASE_PATH = "students_2024.db"
    DATA_TABLE = "students"  # The main data table to query from
    
    # User identification
    USER_ID_COLUMN = "Register_Number"  # Which column identifies the user
    USER_NAME_COLUMN = "Student_Name"  # Column for user's display name
    
    # Optional: Define custom column mappings for better search
    # If a column isn't found by schema discovery, add it here
    CUSTOM_COLUMN_MAPPINGS = {
        # "query_keyword": "actual_column_name"
    }
    
    # Optional: Define which columns to prioritize in search
    PRIORITY_COLUMNS = [
        # Higher priority columns will be matched first
    ]
    
    # Optional: Define column type hints if auto-detection fails
    COLUMN_TYPE_HINTS = {
        # "column_name": "numeric|text|percentage|status|contact|date"
    }


class DatasetConfigBuilder:
    """Builder to configure for different datasets"""
    
    @staticmethod
    def for_students() -> DatasetConfig:
        """Configure for student portal dataset"""
        return DatasetConfig()
    
    @staticmethod
    def for_custom(db_path: str, data_table: str, 
                   id_column: str, name_column: str) -> DatasetConfig:
        """Create config for custom dataset"""
        config = DatasetConfig()
        config.DATABASE_PATH = db_path
        config.DATA_TABLE = data_table
        config.USER_ID_COLUMN = id_column
        config.USER_NAME_COLUMN = name_column
        return config
    
    @staticmethod
    def for_employees(db_path: str = "company.db") -> DatasetConfig:
        """Example: Configure for employee dataset"""
        return DatasetConfigBuilder.for_custom(
            db_path=db_path,
            data_table="employees",
            id_column="employee_id",
            name_column="employee_name"
        )
    
    @staticmethod
    def for_products(db_path: str = "inventory.db") -> DatasetConfig:
        """Example: Configure for product dataset"""
        return DatasetConfigBuilder.for_custom(
            db_path=db_path,
            data_table="products",
            id_column="product_id",
            name_column="product_name"
        )
    
    @staticmethod
    def for_patients(db_path: str = "hospital.db") -> DatasetConfig:
        """Example: Configure for hospital patient dataset"""
        return DatasetConfigBuilder.for_custom(
            db_path=db_path,
            data_table="patients",
            id_column="patient_id",
            name_column="patient_name"
        )


# Current active configuration
ACTIVE_CONFIG = DatasetConfig()
