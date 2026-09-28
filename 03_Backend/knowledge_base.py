import pandas as pd
from pathlib import Path


# Path to the Excel knowledge base
EXCEL_FILE = (
    Path(__file__).parent.parent
    / "01_Knowledge_Base"
    / "Qlik_Troubleshooting_Flows.xlsx"
)


def load_knowledge_base():
    """
    Load troubleshooting information from Excel.
    """

    if not EXCEL_FILE.exists():
        raise FileNotFoundError(
            f"Knowledge base file not found: {EXCEL_FILE}"
        )

    df = pd.read_excel(
        EXCEL_FILE,
        sheet_name="Troubleshooting"
    )

    return df


if __name__ == "__main__":

    knowledge_base = load_knowledge_base()

    print("Knowledge Base Loaded Successfully!")
    print()

    print("Number of records:", len(knowledge_base))
    print()

    print("Columns:")
    print(list(knowledge_base.columns))
    print()

    print("First 5 records:")
    print(knowledge_base.head())