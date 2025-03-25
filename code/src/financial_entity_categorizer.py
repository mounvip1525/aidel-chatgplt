import wikipedia
from typing import List, Dict, Optional
import time
from wikipedia.exceptions import WikipediaException

class FinancialEntityCategorizer:
    def __init__(self):
        self.categories = {
            'trusts_and_foundations': [
                'trust', 'foundation', 'endowment', 'trustee', 'trusteeship'
            ],
            'charities_and_ngos': [
                'charity', 'non-governmental organization', 'ngo', 'nonprofit',
                'non-profit', 'crowdfunding', 'crowd funding', 'charitable organization'
            ],
            'investment_companies': [
                'investment company', 'investment firm', 'investment management',
                'asset management', 'mutual fund', 'hedge fund', 'private equity',
                'financial services', 'asset manager', 'wealth management'
            ],
            'venture_capital': [
                'venture capital', 'vc firm', 'startup investment',
                'private equity', 'seed funding'
            ],
            'shell_companies': [
                'shell company', 'shell corporation', 'paper company',
                'letterbox company', 'front company'
            ]
        }
        # Set language and enable rate limiting
        wikipedia.set_lang('en')
        wikipedia.set_rate_limiting(True)

    def search_wikipedia(self, entity_name: str) -> Optional[str]:
        """
        Search Wikipedia for the entity and return its page content.
        
        Args:
            entity_name (str): Name of the entity to search for
            
        Returns:
            Optional[str]: The page content if found, None otherwise
            
        Raises:
            WikipediaException: If there's an error accessing Wikipedia
        """
        max_retries = 3
        retry_delay = 2  # seconds
        
        for attempt in range(max_retries):
            try:
                # Search for the entity
                search_results = wikipedia.search(entity_name)
                if not search_results:
                    return None
                
                # Get the first result
                page = wikipedia.page(search_results[0])
                return page.content.lower()
                
            except wikipedia.exceptions.DisambiguationError:
                return None
            except wikipedia.exceptions.PageError:
                return None
            except WikipediaException as e:
                if attempt < max_retries - 1:
                    time.sleep(retry_delay)
                    continue
                raise WikipediaException(f"Failed to access Wikipedia after {max_retries} attempts: {str(e)}")
            except Exception as e:
                raise Exception(f"Unexpected error while searching Wikipedia: {str(e)}")

    def get_matching_categories(self, entity_name: str) -> List[str]:
        """
        Get a list of categories that match the given entity.
        
        Args:
            entity_name (str): Name of the financial entity to categorize
            
        Returns:
            List[str]: List of matching category names in human-readable format
            
        Raises:
            WikipediaException: If there's an error accessing Wikipedia
            Exception: For other unexpected errors
        """
        content = self.search_wikipedia(entity_name)
        if not content:
            return []

        matching_categories = []
        for category, keywords in self.categories.items():
            if any(keyword in content for keyword in keywords):
                # Convert category name to human-readable format
                readable_category = category.replace('_', ' ').title()
                matching_categories.append(readable_category)

        return matching_categories

# Example usage:
if __name__ == "__main__":
    categorizer = FinancialEntityCategorizer()
    # Example: Get categories for BlackRock
    categories = categorizer.get_matching_categories("BlackRock")
    print(f"Matching categories: {categories}") 
# use in other code like this:
# categorizer = FinancialEntityCategorizer()
# categories = categorizer.get_matching_categories("BlackRock")
# print(f"Matching categories: {categories}") 