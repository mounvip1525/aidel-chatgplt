from langchain_community.tools import WikipediaQueryRun, DuckDuckGoSearchRun
from langchain_community.utilities import WikipediaAPIWrapper
from langchain.tools import Tool
from datetime import datetime
import os
import requests
import json
# Install with pip install firecrawl-py
from firecrawl import FirecrawlApp
from groq import Groq

def save_to_txt(data: str, filename: str = "research_output.md"):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    formatted_text = f"--- Research Output ---\nTimestamp: {timestamp}\n\n{data}\n\n"

    with open(filename, "a", encoding="utf-8") as f:
        f.write(formatted_text)
    
    return f"Data successfully saved to {filename}"

save_tool = Tool(
    name="save_text_to_file",
    func=save_to_txt,
    description="Saves structured research data to a text file.",
)

def serper_search(query: str) -> str:
    """
    Uses the serper.dev API to perform a Google search.
    """
    url = "https://google.serper.dev/search"

    payload = json.dumps({
    "q": query,
    })
    headers = {
    'X-API-KEY': '',
    'Content-Type': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data=payload)

    if response.status_code == 200:
        data = response.json()
        # For simplicity, we convert the response to a string.
        return f"Serper Search Results:\n{data}"
    else:
        return f"Error during serper search: {response.status_code} {response.text}"

# Wrap these functions in LangChain Tool objects.
serper_search_tool = Tool(
    name="GoogleSearch",
    func=serper_search,
    description=("Useful for conducting a Google search using the serper.dev API. "
                 "Input should be a well-crafted query to retrieve financial and background information about an entity.")
)


def firecrawl_scrape(url: str) -> str:
    """
    Uses the firecrawl API to scrape content from a given website.
    """  

    API_KEY = "YOUR_FIRECRAWL_API_KEY"  # Replace with your firecrawl API key

    app = FirecrawlApp(api_key='')

    try:
        response = app.scrape_url(url=url, params={
            'formats': [ 'markdown' ],
        })
        return f"Scraped Content:\n{response.get('markdown', 'No content found')}"
    except Exception as e:
        return f"Error during firecrawl scrape: {str(e)} - No content found"
    
scrape_tool = Tool(
    name="WebScraper",
    func=firecrawl_scrape,
    description=("Useful for scraping the full content of a webpage using the firecrawl API. "
                 "Input should be a URL from which detailed information is needed.")
)


search = DuckDuckGoSearchRun()
search_tool = Tool(
    name="search",
    func=search.run,
    description="Search the web for information",
)

api_wrapper = WikipediaAPIWrapper(top_k_results=5, doc_content_chars_max=10000)
wiki_tool = WikipediaQueryRun(api_wrapper=api_wrapper)



def invoke_groq_cloud()-> str:
       
    GROQ_API_KEY = ""
    client = Groq(
        api_key=GROQ_API_KEY,
    )

    research_content = """

        --- Research Output ---
            Timestamp: 2025-03-26 11:11:57

            # Acme Corporation Analysis Report

            ## Company Background

            The **Acme Corporation** is a fictional corporation that gained popularity through its use in the Warner Bros. cartoons, particularly in the Road Runner and Wile E. Coyote series. This company is depicted as a supplier of outrageous products that frequently fail or backfire in humorous ways, making it a recurring gag in various media, films, and television shows. The term 'Acme' itself comes from ancient Greek, meaning 'summit' or 'peak', which has been ironically applied in cartoons since the products are characteristically unreliable. 

            However, there is also a real-world entity known as **Acme United Corporation**, which operates in the field of cutting, measuring, first aid, and sharpening products. Founded in 1867, it has established itself as a prominent supplier within the industrial and commercial markets, with significant operations in various countries including the US, Canada, Germany, Hong Kong, and China. In 2023, Acme United reported net sales of $191.5 million and net income of $17.8 million.

            ## Risk Factors

            Despite the fictional nature of its namesake, the real **Acme United Corporation** faces several risks common to its industry, including:
            - **Market Competition:** As a supplier, it contends with competition from other firms in the manufacturing and retail of cutting and first aid products.
            - **Supply Chain Issues:** Disruptions in manufacturing or shipping could impact inventory and sales.
            - **Regulation Compliance:** Being involved in safety products means stringent adherence to safety regulations, which could pose risks if not managed properly.

            Limited specific information regarding legal sanctions or associations with politically exposed persons (PEPs) was found during the search. There appears to be no notable sanctions against Acme United Corporation.

            ## Additional Insights

            - **Industry Position:** Acme United is a leading manufacturer in its niche, serving educational institutions, healthcare facilities, and major retail businesses such as Walmart and Staples.
            - **PEP Involvement:** No politically exposed persons (PEPs) have been directly associated with Acme United's operations according to the latest findings.

            ## Sources/Citations
            1. [Acme United Corporation - Wikipedia](https://en.wikipedia.org/wiki/Acme_United_Corporation)
            2. [The Story Behind Acme, the Brand That Never Existed - Adweek](https://www.adweek.com/brand-marketing/how-warner-bros-built-a-fake-brand-that-lives-beyond-the-cartoon-world/)
            3. [Acme United Corporation Official Website](https://acmeunited.com/)
    
    """
    
    system_prompt = """
                    You are an excellent financial analyst. You must strictly base your response on the provided research content and not invent any details beyond it. Analyze the content to determine the riskiness of transacting with the given entity. Your output must be a single JSON object with the following keys:
                - "justification": Provide a concise explanation of the risk assessment using direct evidence from the research.
                - "evidence": List one or more URLs from the research content that support your justification.
                - "entity_name": The name of the entity.
                - "entity_type": The type of entity (e.g., corporation, individual).
                - "risk_factor": A classification of the risk (either "high", "medium", or "low").
                - "confidence": Indicate your confidence level in this analysis (e.g., on a scale or descriptive term).

                Do not include any text besides the JSON object. The research content will be provided as a parameter in the user prompt.

                """
    user_prompt = """

                Analyze the following research content and provide your risk analysis for Acme Corporation with proper justification and evidence (URLs). Output only a JSON object with the keys specified.

                Research Content: {research_content}
    
                """

    completion = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {
                "role": "system",
                "content": system_prompt,
            },
            {
                "role": "user",
                "content": user_prompt.format(research_content=research_content)},
            
        ],
        temperature=0.1,
        max_completion_tokens=3640,
        top_p=1,
        stream=False,
        response_format={"type": "json_object"},
        stop=None,
    )

    print(completion.choices[0].message.content)
    return completion.choices[0].message

# invoke_groq_cloud()