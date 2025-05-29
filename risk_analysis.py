import os
import json
from openai import OpenAI # Using OpenAI Python SDK v1+

def get_llm_analysis(simulation_data_json: str, llm_prompt_params: dict = None) -> str:
    """
    Analyzes simulation data using an LLM (GPT-4o) and provides a risk assessment.

    Args:
        simulation_data_json (str): The simulation results as a JSON string.
        llm_prompt_params (dict, optional): Additional parameters for the LLM prompt. Defaults to None.

    Returns:
        str: The LLM's natural language risk assessment.
    """
    # Initialize OpenAI client
    # The API key should be set as an environment variable (e.g., OPENAI_API_KEY)
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return "Error: OPENAI_API_KEY environment variable not set. Cannot perform LLM analysis."

    client = OpenAI(api_key=api_key)

    # Define the base prompt for the LLM
    base_prompt = """
    You are a Senior Tokenomics Advisor. Your task is to analyze the provided tokenomics simulation data
    and identify potential risks and opportunities. Provide clear, actionable insights and recommendations.

    Focus on the following areas:
    1.  **Inflationary Pressure:** Is the circulating supply growing too rapidly? What are the implications?
    2.  **Vesting Schedule Risks:** Are there large token unlocks (cliffs) that could lead to significant sell pressure?
        Are team/private sale vesting periods appropriate for long-term alignment?
    3.  **Centralization Risk:** Based on initial and long-term allocation percentages, is there a risk of token concentration
        (e.g., too much control by team, treasury, or early investors)?
    4.  **Burn/Sink Effectiveness:** Are the token burn mechanisms sufficient to counteract emissions and maintain value?
    5.  **Overall Sustainability & Value Accrual:** Does the model seem sustainable long-term? How does value accrue to the token?

    Provide your analysis in a structured format, using bullet points or numbered lists for risks and recommendations.
    Be concise but comprehensive.

    ---
    Simulation Data (JSON):
    """

    # Combine base prompt with simulation data
    full_prompt = f"{base_prompt}\n{simulation_data_json}"

    try:
        # Make the API call to GPT-4o
        response = client.chat.completions.create(
            model="gpt-4o", # Or "gpt-4-turbo", or "gemini-1.5-flash-latest" if using Google's API
            messages=[
                {"role": "system", "content": "You are a highly analytical and experienced tokenomics advisor."},
                {"role": "user", "content": full_prompt}
            ],
            temperature=0.7, # Controls randomness. Lower for more focused output.
            max_tokens=1000 # Limit the length of the response
        )
        # Extract the content from the response
        analysis_text = response.choices[0].message.content
        return analysis_text

    except Exception as e:
        return f"Error during LLM analysis: {e}"

# --- Example Usage (for testing the LLM analysis module) ---
if __name__ == "__main__":
    # This is mock simulation data for testing purposes.
    # In a real scenario, this would come from tokenomics_simulator.py
    mock_simulation_data = [
        {"month": 1, "circulating_supply": 150000000, "total_supply": 1000000000, "unlocked_team": 0, "unlocked_private_sale": 0, "minted_tokens": 5000000, "burned_tokens": 50000},
        {"month": 12, "circulating_supply": 250000000, "total_supply": 1100000000, "unlocked_team": 0, "unlocked_private_sale": 0, "minted_tokens": 5000000, "burned_tokens": 50000},
        {"month": 13, "circulating_supply": 260000000, "total_supply": 1105000000, "unlocked_team": 5000000, "unlocked_private_sale": 0, "minted_tokens": 5000000, "burned_tokens": 50000},
        {"month": 36, "circulating_supply": 450000000, "total_supply": 1250000000, "unlocked_team": 5000000, "unlocked_private_sale": 2500000, "minted_tokens": 5000000, "burned_tokens": 50000},
        {"month": 60, "circulating_supply": 600000000, "total_supply": 1400000000, "unlocked_team": 0, "unlocked_private_sale": 0, "minted_tokens": 5000000, "burned_tokens": 50000},
    ]
    mock_simulation_data_json = json.dumps(mock_simulation_data, indent=2)

    print("Running LLM analysis with mock data...")
    analysis_results = get_llm_analysis(mock_simulation_data_json)
    print("\n--- LLM Analysis ---")
    print(analysis_results)
