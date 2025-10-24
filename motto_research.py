from openai import OpenAI
import os


def research_company_mission_and_recruiter_priorities(
    company_name="Anthropic", client=None
):
    """
    Research a company's mission statement and what matters most to recruiters.
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
    4. Company culture and what makes a candidate a good fit
    
    Company: {company_name}
    
    Please provide a comprehensive analysis that would help a job candidate understand:
    - What the company stands for
    - What recruiters prioritize when evaluating candidates
    - How to align their application with company values and needs
    """

    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {
                    "role": "system",
                    "content": "You are a career research expert who helps job candidates understand companies and what recruiters look for.",
                },
                {"role": "user", "content": prompt},
            ],
            max_tokens=1500,
            temperature=0.7,
        )

        return response.choices[0].message.content

    except Exception as e:
        return f"Error making API call: {str(e)}"


def main():
    """
    Main function to run the research.
    """
    print(f"Researching {COMPANY_TO_RESEARCH}...")
    print("=" * 50)

    result = research_company_mission_and_recruiter_priorities()
    print(result)


if __name__ == "__main__":
    main()
