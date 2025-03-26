import json
from main import invoke_research_agent

def load_sample_output():
    """Loads the sample output from sampleoutput.json."""
    try:
        with open("sampleoutput.json", "r") as f:
            data = json.load(f)
        return data
    except FileNotFoundError:
        print("Error: sampleoutput.json not found.")
        return None
    except json.JSONDecodeError:
        print("Error: Invalid JSON format in sampleoutput.json.")
        return None

sample_output_data = load_sample_output()

if sample_output_data:
    print("Sample output data loaded successfully.")
    # You can now use the 'sample_output_data' variable
    # which contains the data from sampleoutput.json
else:
    print("Failed to load sample output data.")


def filter_data(data):
    """Filters the input data to include only 'Raw Transaction' and 'Proper Noun Entities'."""
    filtered_data = []
    for item in data:
        filtered_item = {
            "Raw Transaction": item["Raw Transaction"],
            "Proper Noun Entities": item["Proper Noun Entities"]
        }
        filtered_data.append(filtered_item)
    return filtered_data

if sample_output_data:
    filtered_output = filter_data(sample_output_data)
    print(json.dumps(filtered_output, indent=2))



from tools import invoke_groq_cloud
from main import agent_executor
from tools import save_to_txt

def invoke_agent(entity):
    """Invokes the agent executor for a given entity."""
    try:
        raw_response = agent_executor.invoke({"query": entity})
        return raw_response.get("output")
    except Exception as e:
        print(f"Error invoking agent for {entity}: {e}")
        return None

def get_agent_prompt(entity: str) -> str:
    prompt_template = """
        
        "Please research the entity '{entity}' and provide a detailed analysis of its background, industry, any sanctions or 
        regulatory actions, and any involvement of politically exposed persons (PEPs). 
        Use only verified evidence from search results, including URLs for each finding, to assess the risk level associated with 
        transactions involving this entity, dont fabricate the result. Save the final results to a file."
 
                
    """

    return prompt_template.format(entity=entity)

def process_entities(data):
    """
    Iterates over the items in the JSON list, then iterates over proper noun entities,
    and calls the invoke_agent() for entities with type 'organisation' or 'person'.
    """
    results = []
    markdown_list = ""
    for item in data:
        raw_transaction = item["Raw Transaction"]
        entities = item["Proper Noun Entities"]
        for entity_info in entities:
            entity_name = entity_info["Entity Name"]
            entity_type = entity_info["Entity Type"]
            if entity_type.lower() in ["organisation", "person", "organization"]:
                print(f"Processing entity: {entity_name} (Type: {entity_type})")
                prompt = get_agent_prompt(entity_name)
                agent_response = invoke_research_agent(prompt)
                
                print("Final Research Output: " + agent_response)
    return results

if sample_output_data:
    processed_data = process_entities(sample_output_data)
    # print(json.dumps(processed_data, indent=2))
