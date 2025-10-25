import requests
from bs4 import BeautifulSoup
from openai import OpenAI
import os
from urllib.parse import urlparse
import argparse
import json


def scrape_job_specifications(url, client=None):
    """
    Scrape job specifications from a given webpage URL.

    Args:
        url (str): The URL of the job posting webpage
        client: OpenAI client instance (optional)

    Returns:
        dict: Dictionary containing scraped content and analysis
    """
    try:
        # Validate URL
        parsed_url = urlparse(url)
        if not parsed_url.scheme or not parsed_url.netloc:
            return {"error": "Invalid URL provided"}

        # Add https if no scheme provided
        if not parsed_url.scheme:
            url = "https://" + url

        # Set up headers to mimic a real browser
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }

        # Make the request
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()

        # Parse the HTML
        soup = BeautifulSoup(response.content, "html.parser")

        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()

        # Extract text content
        text_content = soup.get_text()

        # Clean up the text
        lines = (line.strip() for line in text_content.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = " ".join(chunk for chunk in chunks if chunk)

        # Use GPT to analyze and synthesize job specifications from the HTML
        job_specs = None
        if client:
            job_specs = synthesize_job_specifications_with_gpt(text, client)

        return {
            "url": url,
            "raw_text": text,
            "job_specifications": job_specs,
            "success": True,
        }

    except requests.exceptions.RequestException as e:
        return {"error": f"Failed to fetch webpage: {str(e)}"}
    except Exception as e:
        return {"error": f"Error scraping webpage: {str(e)}"}


def synthesize_job_specifications_with_gpt(text, client):
    """
    Use GPT to analyze the scraped HTML content and synthesize job specifications.

    Args:
        text: Raw text content from the webpage
        client: OpenAI client instance

    Returns:
        dict: Structured job specifications synthesized by GPT
    """
    prompt = f"""
    Analyze the following job posting content and extract structured information in JSON format.

    JOB POSTING CONTENT:
    {text[:4000]}  # Limit to first 4000 characters

    Please extract and structure the following information as a JSON object:

    {{
        "job_title": "The job title",
        "company": "Company name",
        "location": "Job location and work arrangement (remote/hybrid/onsite)",
        "requirements": [
            "List of key requirements and qualifications"
        ],
        "responsibilities": [
            "List of main responsibilities and duties"
        ],
        "benefits": [
            "List of benefits and perks offered"
        ],
        "experience_level": "Required experience level (entry/mid/senior)",
        "skills": [
            "List of required technical and soft skills"
        ],
        "company_culture": "Description of company culture and values if mentioned",
        "salary_range": "Salary information if mentioned",
        "employment_type": "Full-time/Part-time/Contract etc.",
        "key_qualifications": [
            "Most important qualifications for this role"
        ],
        "red_flags": [
            "Any potential concerns or red flags"
        ]
    }}

    Focus on extracting concrete, actionable information that would help a job candidate understand:
    - What they need to qualify for this role
    - What the day-to-day work involves
    - What the company values and culture are like
    - How to tailor their application

    Return ONLY the JSON object, no additional text.
    """

    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert job posting analyzer. Extract structured information from job postings and return it as clean JSON. Be precise and focus on actionable information for job candidates.",
                },
                {"role": "user", "content": prompt},
            ],
            max_tokens=2000,
            temperature=0.3,
        )

        # Try to parse the JSON response
        try:
            job_specs = json.loads(response.choices[0].message.content)
            return job_specs
        except json.JSONDecodeError:
            # If JSON parsing fails, return the raw response
            return {"raw_analysis": response.choices[0].message.content}

    except Exception as e:
        return {"error": f"Error synthesizing job specifications: {str(e)}"}


def get_job_specifications_for_cover_letter(url, client=None):
    """
    Simplified function to get job specifications for use in cover letter generation.

    Args:
        url (str): The URL of the job posting webpage
        client: OpenAI client instance (optional)

    Returns:
        str: Formatted job specifications for cover letter generation
    """
    result = scrape_job_specifications(url, client)

    if result.get("error"):
        return f"Error scraping job posting: {result['error']}"

    job_specs = result.get("job_specifications", {})

    if not job_specs or job_specs.get("error"):
        return f"Error analyzing job specifications: {job_specs.get('error', 'No specifications found')}"

    # Format the structured job specifications for cover letter generation
    formatted_specs = f"""
JOB POSTING ANALYSIS:
URL: {result['url']}
Job Title: {job_specs.get('job_title', 'Not specified')}
Company: {job_specs.get('company', 'Not specified')}
Location: {job_specs.get('location', 'Not specified')}
Experience Level: {job_specs.get('experience_level', 'Not specified')}
Employment Type: {job_specs.get('employment_type', 'Not specified')}

KEY REQUIREMENTS:
{chr(10).join(f"- {req}" for req in job_specs.get('requirements', ['No specific requirements found']))}

RESPONSIBILITIES:
{chr(10).join(f"- {resp}" for resp in job_specs.get('responsibilities', ['No specific responsibilities found']))}

REQUIRED SKILLS:
{chr(10).join(f"- {skill}" for skill in job_specs.get('skills', ['No specific skills listed']))}

KEY QUALIFICATIONS:
{chr(10).join(f"- {qual}" for qual in job_specs.get('key_qualifications', ['No key qualifications specified']))}

BENEFITS:
{chr(10).join(f"- {benefit}" for benefit in job_specs.get('benefits', ['No benefits information found']))}

COMPANY CULTURE:
{job_specs.get('company_culture', 'No company culture information found')}

SALARY RANGE:
{job_specs.get('salary_range', 'No salary information found')}
"""

    if job_specs.get("red_flags"):
        formatted_specs += f"\nPOTENTIAL CONCERNS:\n{chr(10).join(f"- {flag}" for flag in job_specs.get('red_flags', []))}"

    return formatted_specs


def main():
    """
    Main function to run the job specification scraper.
    """
    parser = argparse.ArgumentParser(
        description="Scrape and analyze job specifications from a webpage"
    )
    parser.add_argument("url", help="URL of the job posting webpage")
    parser.add_argument(
        "--analyze",
        "-a",
        action="store_true",
        help="Use GPT to analyze the scraped content",
    )

    args = parser.parse_args()

    # Initialize OpenAI client if analysis is requested
    client = None
    if args.analyze:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            print("Error: OPENAI_API_KEY environment variable not set")
            return
        client = OpenAI(api_key=api_key)

    print(f"Scraping job specifications from: {args.url}")
    print("=" * 60)

    result = scrape_job_specifications(args.url, client)

    if result.get("error"):
        print(f"Error: {result['error']}")
        return

    print("SCRAPED CONTENT:")
    print("-" * 40)
    print(
        result["raw_text"][:1000] + "..."
        if len(result["raw_text"]) > 1000
        else result["raw_text"]
    )
    print("-" * 40)

    if result.get("job_specifications"):
        print("\nSYNTHESIZED JOB SPECIFICATIONS:")
        print("-" * 40)
        job_specs = result["job_specifications"]

        if job_specs.get("error"):
            print(f"Error: {job_specs['error']}")
        else:
            print(f"Job Title: {job_specs.get('job_title', 'Not specified')}")
            print(f"Company: {job_specs.get('company', 'Not specified')}")
            print(f"Location: {job_specs.get('location', 'Not specified')}")
            print(
                f"Experience Level: {job_specs.get('experience_level', 'Not specified')}"
            )

            if job_specs.get("requirements"):
                print(f"\nRequirements:")
                for req in job_specs["requirements"][:3]:
                    print(f"  - {req}")

            if job_specs.get("responsibilities"):
                print(f"\nResponsibilities:")
                for resp in job_specs["responsibilities"][:3]:
                    print(f"  - {resp}")

            if job_specs.get("skills"):
                print(f"\nRequired Skills:")
                for skill in job_specs["skills"][:5]:
                    print(f"  - {skill}")

            if job_specs.get("benefits"):
                print(f"\nBenefits:")
                for benefit in job_specs["benefits"][:3]:
                    print(f"  - {benefit}")

            if job_specs.get("company_culture"):
                print(f"\nCompany Culture: {job_specs['company_culture']}")

            if job_specs.get("salary_range"):
                print(f"\nSalary Range: {job_specs['salary_range']}")

            if job_specs.get("red_flags"):
                print(f"\nPotential Concerns:")
                for flag in job_specs["red_flags"]:
                    print(f"  - {flag}")

    # Save results to file
    output_file = "scraped_job_specs.txt"
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(f"URL: {result['url']}\n")
        f.write("=" * 60 + "\n\n")
        f.write("RAW CONTENT:\n")
        f.write("-" * 40 + "\n")
        f.write(result["raw_text"])
        f.write("\n\n")

        if result.get("job_specifications"):
            f.write("SYNTHESIZED JOB SPECIFICATIONS:\n")
            f.write("-" * 40 + "\n")
            job_specs = result["job_specifications"]

            if job_specs.get("error"):
                f.write(f"Error: {job_specs['error']}\n")
            else:
                f.write(f"Job Title: {job_specs.get('job_title', 'Not specified')}\n")
                f.write(f"Company: {job_specs.get('company', 'Not specified')}\n")
                f.write(f"Location: {job_specs.get('location', 'Not specified')}\n")
                f.write(
                    f"Experience Level: {job_specs.get('experience_level', 'Not specified')}\n"
                )
                f.write(
                    f"Employment Type: {job_specs.get('employment_type', 'Not specified')}\n\n"
                )

                if job_specs.get("requirements"):
                    f.write("REQUIREMENTS:\n")
                    for req in job_specs["requirements"]:
                        f.write(f"  - {req}\n")
                    f.write("\n")

                if job_specs.get("responsibilities"):
                    f.write("RESPONSIBILITIES:\n")
                    for resp in job_specs["responsibilities"]:
                        f.write(f"  - {resp}\n")
                    f.write("\n")

                if job_specs.get("skills"):
                    f.write("REQUIRED SKILLS:\n")
                    for skill in job_specs["skills"]:
                        f.write(f"  - {skill}\n")
                    f.write("\n")

                if job_specs.get("key_qualifications"):
                    f.write("KEY QUALIFICATIONS:\n")
                    for qual in job_specs["key_qualifications"]:
                        f.write(f"  - {qual}\n")
                    f.write("\n")

                if job_specs.get("benefits"):
                    f.write("BENEFITS:\n")
                    for benefit in job_specs["benefits"]:
                        f.write(f"  - {benefit}\n")
                    f.write("\n")

                if job_specs.get("company_culture"):
                    f.write(f"COMPANY CULTURE: {job_specs['company_culture']}\n\n")

                if job_specs.get("salary_range"):
                    f.write(f"SALARY RANGE: {job_specs['salary_range']}\n\n")

                if job_specs.get("red_flags"):
                    f.write("POTENTIAL CONCERNS:\n")
                    for flag in job_specs["red_flags"]:
                        f.write(f"  - {flag}\n")

    print(f"\nResults saved to: {output_file}")


if __name__ == "__main__":
    main()
