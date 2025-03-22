import os
import re
import json
import pandas as pd
import rapidfuzz.fuzz as fuzz  
import spacy
from openai import OpenAI

client = OpenAI(api_key="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")  


# Load spaCy model for NER
nlp = spacy.load("en_core_web_lg")

# --- Dynamic Field Configuration ---
field_config = {
    "Transaction ID": ["Transaction ID", "tid"],
    "Date": ["Date"],
    "Amount": ["Amount", "amt"],
    "Transaction Type": ["Transaction Type", "Type"],
    "Reference": ["Reference", "Ref"],
    "Sender Block": ["Sender", "sndr"],
    "Receiver Block": ["Receiver", "rvcr"],
    "Sender Name": ["Name"],
    "Sender Account": ["Account", "Acct"],
    "Sender Address": ["Address"],
    "Receiver Name": ["Name"],
    "Receiver Account": ["Account", "Acct"],
    "Receiver Address": ["Address"],
    "Additional Notes": ["Additional Notes", "Notes"]
}

# --- Abbreviation Mapping for Standardization ---
abbreviation_map = {
    "corp": "corporation",
    "inc": "incorporated",
    "ltd": "limited",
    "co": "company",
    "intl": "international",
    "plc": "public limited company",
    "llc": "limited liability company",
    "gmbh": "gesellschaft mit beschränkter haftung",
    "org": "organisation"
}

def robust_standardize(name, abbrev_map):
    """Standardizes a company name: lowercases, removes punctuation, expands abbreviations, and normalizes spaces."""
    if not name:
        return None
    name = name.lower().strip()
    name = re.sub(r'[^\w\s]', '', name)
    for abbr, full in sorted(abbrev_map.items(), key=lambda x: -len(x[0])):
        name = re.sub(r'\b' + re.escape(abbr) + r'\b', full, name)
    return re.sub(r'\s+', ' ', name)

def build_dynamic_regex(synonyms):
    """Builds a regex pattern to match any provided synonyms followed by ':' and capture the value."""
    return r"(" + "|".join([re.escape(label) for label in synonyms]) + r"):\s*(.+)"

def dynamic_extract(text, canonical_field, multi_line=False):
    """
    Extracts a field's value from text dynamically using synonyms from field_config.
    If multi_line is True, returns multi-line content.
    """
    synonyms = field_config.get(canonical_field, [])
    pattern = build_dynamic_regex(synonyms)
    flags = re.IGNORECASE | re.DOTALL if multi_line else re.IGNORECASE
    match = re.search(pattern, text, flags)
    if match:
        value = match.group(2).strip()
        if multi_line:
            return "\n".join([line.strip().strip('"') for line in value.splitlines() if line.strip()])
        return value
    return None

def llm_extract_field(transaction_text, field_name):
    """
    Uses an LLM (e.g., GPT-4) to extract a missing field from the transaction text.
    Uses the default prompt for all fields.
    """
    prompt = f"""Extract the '{field_name}' from the following financial transaction details.
If the field is not present, return 'null'.

Transaction details:
{transaction_text}

Output (in JSON format):
{{ "{field_name}": "extracted value" }}"""
    try:
        response = client.chat.completions.create(model="gpt-4",  # or "gpt-3.5-turbo"
        messages=[{"role": "user", "content": prompt}],
        temperature=0.0)
        content = response.choices[0].message.content
        extracted = json.loads(content)
        return extracted.get(field_name)
    except Exception as e:
        print(f"LLM extraction error for field '{field_name}': {e}")
        return None

def fallback_field(text, field_name):
    """Uses LLM fallback to extract a missing field."""
    value = llm_extract_field(text, field_name)
    if value and value.lower() != "null":
        return value.strip()
    return None

def extract_field(text, canonical_field, multi_line=False):
    """Extracts a field dynamically; if not found, falls back to LLM extraction."""
    value = dynamic_extract(text, canonical_field, multi_line)
    if not value:
        value = fallback_field(text, canonical_field)
    return value

def extract_block(text, block_field):
    """
    Extracts a block of text (e.g., Sender Block, Receiver Block) using dynamic field labels.
    Returns the block text or None.
    """
    synonyms = field_config.get(block_field, [])
    pattern = r"(" + "|".join([re.escape(s) for s in synonyms]) + r"):\s*(.*?)(?=\n\S+?:|$)"
    match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
    if match:
        return match.group(2).strip()
    return None

def filter_notes(notes_text):
    """
    Filters out unwanted header lines from the notes.
    Discards any line that exactly matches a synonym for "Additional Notes" or ends with a colon.
    Also discards lines starting with other field headers.
    """
    # Build a set of unwanted field labels (all keys except for Additional Notes)
    unwanted_labels = []
    for key, synonyms in field_config.items():
        if key != "Additional Notes":
            unwanted_labels.extend([s.lower() for s in synonyms])
    additional_headers = [s.lower() for s in field_config.get("Additional Notes", [])]

    lines = notes_text.splitlines()
    filtered = []
    for line in lines:
        line_clean = line.strip().strip('"')
        if not line_clean:
            continue
        if line_clean.lower() in additional_headers:
            continue
        if line_clean.endswith(":"):
            continue
        if any(re.match(rf"^\s*{re.escape(label)}\s*:", line_clean, re.IGNORECASE) for label in unwanted_labels):
            continue
        filtered.append(line_clean)
    return filtered

def parse_transaction(text):
    """
    Extracts all desired fields from a transaction text block using dynamic extraction and fallbacks.
    Returns a dictionary with structured transaction data.
    """
    data = {}
    # Extract simple fields dynamically
    for field in ["Transaction ID", "Date", "Amount", "Transaction Type", "Reference"]:
        extracted = extract_field(text, field)
        if field == "Amount" and extracted:
            try:
                extracted = float(re.sub(r'[^\d\.]', '', extracted))
            except Exception:
                extracted = None
        data[field] = extracted

    sender_block = extract_block(text, "Sender Block")
    receiver_block = extract_block(text, "Receiver Block")

    sender_name = extract_field(sender_block, "Sender Name") if sender_block else None
    sender_account = extract_field(sender_block, "Sender Account") if sender_block else None
    sender_address = extract_field(sender_block, "Sender Address") if sender_block else None

    receiver_name = extract_field(receiver_block, "Receiver Name") if receiver_block else None
    receiver_account = extract_field(receiver_block, "Receiver Account") if receiver_block else None
    receiver_address = extract_field(receiver_block, "Receiver Address") if receiver_block else None

    # Fallback using spaCy NER for organization names if missing
    if not sender_name or not receiver_name:
        doc = nlp(text)
        orgs = [ent.text for ent in doc.ents if ent.label_ == "ORG"]
        if not sender_name and orgs:
            sender_name = orgs[0]
        if not receiver_name and len(orgs) > 1:
            receiver_name = orgs[1]

    # Standardize organization names
    data["Sender Name"] = robust_standardize(sender_name, abbreviation_map) if sender_name else None
    data["Receiver Name"] = robust_standardize(receiver_name, abbreviation_map) if receiver_name else None

    data["Sender Account"] = sender_account
    data["Sender Address"] = sender_address
    data["Receiver Account"] = receiver_account
    data["Receiver Address"] = receiver_address

    # Extract and filter Additional Notes (multi-line)
    notes_text = extract_field(text, "Additional Notes", multi_line=True)
    data["Notes"] = filter_notes(notes_text) if notes_text else []

    return data

def process_transactions_txt(file_path, separator="---"):
    """
    Reads a .txt file containing multiple transactions separated by a delimiter.
    Processes each transaction using dynamic extraction and returns a list of dictionaries.
    """
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
    transactions_raw = [block.strip() for block in content.split(separator) if block.strip()]
    return [parse_transaction(block) for block in transactions_raw]

# --- Starter Function: Automatic Flow Selection ---
def process_transactions(input_file):
    """
    Determines whether the input_file is structured (CSV) or unstructured (TXT)
    based on its extension, and processes it accordingly.
    Returns a list of transaction dictionaries.
    """
    _, ext = os.path.splitext(input_file)
    if ext.lower() == ".csv":
        return process_structured_transactions(input_file)
    elif ext.lower() == ".txt":
        return process_transactions_txt(input_file, separator="---")
    else:
        raise ValueError("Unsupported file type. Only CSV and TXT are supported.")

# --- Structured Extraction Function ---
def process_structured_transactions(csv_file):
    """Processes structured CSV transactions and returns a list of dictionaries with unified keys."""
    df = pd.read_csv(csv_file)
    print("Raw CSV Data:")
    print(df.head())

    # Map CSV columns to unified keys.
    df['Transaction ID'] = df['Transaction']
    df['Sender Name'] = df['Payer Name']
    # Assume "Receiver Name" is already present.

    # For missing fields, add columns with None.
    df['Date'] = df.get('Date', None)
    df['Transaction Type'] = None
    df['Reference'] = None
    df['Sender Account'] = None
    df['Sender Address'] = None
    df['Receiver Account'] = None
    df['Receiver Address'] = None

    # Clean the "Amount" field.
    df['Amount'] = df['Amount'].replace({'\$': '', ',': ''}, regex=True).astype(float)

    # Standardize company names.
    df['Sender Name'] = df['Sender Name'].apply(lambda name: robust_standardize(name, abbreviation_map))
    df['Receiver Name'] = df['Receiver Name'].apply(lambda name: robust_standardize(name, abbreviation_map))

    # Use "Transaction Details" as Notes.
    def make_notes(details):
        if pd.isna(details) or not details.strip():
            return []
        return [details.strip()]
    df['Notes'] = df['Transaction Details'].apply(make_notes)

    unified_columns = [
        "Transaction ID", "Date", "Amount", "Transaction Type", "Reference",
        "Sender Name", "Receiver Name",
        "Sender Account", "Sender Address",
        "Receiver Account", "Receiver Address",
        "Notes"
    ]
    df_unified = df[unified_columns]
    return df_unified.to_dict(orient='records')

if __name__ == "__main__":
    # Change input_file as needed (CSV for structured, TXT for unstructured)
    input_file = "data/transactions.csv"  # or "data/transactions.csv"
    transactions = process_transactions(input_file)

    json_output = json.dumps(transactions, indent=2)
    print("Processed Transactions in JSON Format:")
    print(json_output)

    with open("data/processed_transactions.json", "w", encoding="utf-8") as json_file:
        json_file.write(json_output)