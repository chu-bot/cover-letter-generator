import os
import argparse
from dotenv import load_dotenv
from openai import OpenAI
from motto_research import research_company_mission_and_recruiter_priorities
from job_spec_scraper import get_job_specifications_for_cover_letter

# Load environment variables from a .env file, if present
load_dotenv()

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def read_file_content(filename):
    """
    Read content from a text file.
    """
    try:
        with open(filename, "r", encoding="utf-8") as file:
            return file.read().strip()
    except FileNotFoundError:
        return ""
    except Exception as e:
        print(f"Error reading {filename}: {e}")
        return ""


def generate_cover_letter(company_name="Anthropic", job_url=None):
    """
    Generate a personalized cover letter by combining resume input, writing example,
    and company research to maintain consistent tone and style.

    Args:
        company_name (str): Name of the company
        job_url (str, optional): URL of the specific job posting to scrape
    """

    # Read input files
    resume_content = read_file_content("resume_input.txt")
    writing_example = read_file_content("writing_example.txt")
    global_notes = read_file_content("global_notes.txt")
    header_content = read_file_content("header.txt")
    projects_content = read_file_content("projects.txt")

    # Get company research
    print(f"Researching {company_name}...")
    company_research = research_company_mission_and_recruiter_priorities(
        company_name, client
    )

    # Get job specifications if URL is provided
    job_specs = ""
    if job_url:
        print(f"Scraping job specifications from: {job_url}")
        job_specs = get_job_specifications_for_cover_letter(job_url, client)

    # Create the comprehensive prompt
    prompt = f"""
    You are the writer of the resume_input and writing_example. Keep your tone consistent with your writing style.

    RESUME INPUT:
    {resume_content}

    WRITING EXAMPLE (your typical writing style and tone):
    {writing_example}

    PROJECT PORTFOLIO (detailed project descriptions and achievements):
    {projects_content if projects_content else "No project portfolio provided."}

    COMPANY RESEARCH:
    {company_research}

    {f"JOB SPECIFICATIONS FROM POSTING:\n{job_specs}" if job_specs else ""}

    GLOBAL NOTES (additional instructions or corrections):
    {global_notes if global_notes else "No additional notes provided."}

    HEADER CONTENT (to be placed before the cover letter):
    {header_content if header_content else "No header content provided."}

    Based on the above information, write a two-paragraph cover letter that:
    1. Demonstrates why you would be a good fit for {company_name}
    2. Maintains the same tone and writing style as shown in your writing example
    3. Incorporates insights from the company research to show alignment with their values and needs
    4. {f"Specifically addresses the job requirements and responsibilities from the job posting" if job_specs else "Highlights relevant experience from your resume in a compelling way"}
    5. Uses specific project examples and achievements from the project portfolio to demonstrate relevant skills and experience
    6. Follows any specific instructions or corrections provided in the global notes

    Write the cover letter as if you are the person described in the resume_input, using the writing style from writing_example, and addressing the company's specific needs and values as identified in the research. {f"Pay special attention to the specific job requirements and responsibilities from the job posting." if job_specs else ""} Use concrete examples from your project portfolio to showcase your capabilities. Pay special attention to any additional instructions in the global notes.
    
    IMPORTANT: Always start the cover letter with the header content (if provided), followed by the two-paragraph cover letter body. If the header content contains outdated information (such as the date), you may replace that ONLY.
    """

    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {
                    "role": "system",
                    "content": "You are a professional cover letter writer who helps job candidates write compelling, personalized cover letters that match their writing style and align with company values.",
                },
                {"role": "user", "content": prompt},
            ],
            max_tokens=1000,
            temperature=0.7,
        )

        return response.choices[0].message.content

    except Exception as e:
        return f"Error generating cover letter: {str(e)}"


def main():
    """
    Main function to generate the cover letter.
    """
    # Set up command line argument parsing
    parser = argparse.ArgumentParser(description="Generate a personalized cover letter")
    parser.add_argument(
        "--company",
        "-c",
        type=str,
        default="Anthropic",
        help="Company name to generate cover letter for (default: Anthropic)",
    )
    parser.add_argument(
        "--job-url",
        "-j",
        type=str,
        help="URL of the specific job posting to scrape for requirements",
    )

    args = parser.parse_args()
    company_name = args.company
    job_url = args.job_url

    print("=" * 60)
    print("COVER LETTER GENERATOR")
    print("=" * 60)
    print(f"Generating cover letter for: {company_name}")
    if job_url:
        print(f"Using job specifications from: {job_url}")
    print("=" * 60)

    cover_letter = generate_cover_letter(company_name, job_url)

    print("\nGENERATED COVER LETTER:")
    print("-" * 40)
    print(cover_letter)
    print("-" * 40)

    # Optionally save to file
    with open("generated_cover_letter.txt", "w", encoding="utf-8") as f:
        f.write(cover_letter)

    print(f"\nCover letter saved to: generated_cover_letter.txt")


if __name__ == "__main__":
    main()
