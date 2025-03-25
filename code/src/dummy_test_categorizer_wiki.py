from financial_entity_categorizer import FinancialEntityCategorizer

def main():
    # Instantiate the categorizer
    categorizer = FinancialEntityCategorizer()
    
    # List of financial entities to categorize
    entities = [
        "BlackRock",
        "Bill & Melinda Gates Foundation",
        "Sequoia Capital",
        "NonExistentEntity"
    ]
    
    # Iterate over each entity and print the categories
    for entity in entities:
        try:
            categories = categorizer.get_matching_categories(entity)
            print(f"Entity: {entity}")
            if categories:
                print("Categories:")
                for category in categories:
                    print(f" - {category}")
            else:
                print("No matching categories found.")
            print("-" * 50)
        except Exception as e:
            print(f"Error processing entity '{entity}': {e}")

if __name__ == "__main__":
    main()