from openai import OpenAI
import os


def research_company_mission_and_recruiter_priorities(
    company_name="Anthropic", client=None
):
    """
    Research a company's mission statement and what matters most to recruiters using web search.
    """
    # Create client if not provided
    if client is None:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            return "Error: OPENAI_API_KEY environment variable not set"
        client = OpenAI(api_key=api_key)

    prompt = f"""
    Research the following company and provide insights on:
    1. Their mission statement and core values
    2. What recruiters at this company typically look for in candidates
    3. Company culture and what makes a candidate a good fit
    4. Recent company news, developments, or strategic priorities
    5. Specific job requirements or skills they value
    
    Company: {company_name}
    
    Please provide a comprehensive analysis that would help a job candidate understand:
    - What the company stands for
    - What recruiters prioritize when evaluating candidates
    - How to align their application with company values and needs
    - Any recent company developments that might be relevant
    """

    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {
                    "role": "system",
                    "content": "You are a career research expert who helps job candidates understand companies and what recruiters look for. Use web search to find the most current and accurate information about companies.",
                },
                {"role": "user", "content": prompt},
            ],
            max_tokens=1500,
            temperature=0.7,
            tools=[
                {
                    "type": "web_search",
                    "web_search": {
                        "search_query": f"{company_name} mission statement values culture recruitment hiring"
                    },
                }
            ],
            tool_choice="auto",
        )

        return response.choices[0].message.content

    except Exception as e:
        return f"Error making API call: {str(e)}"
