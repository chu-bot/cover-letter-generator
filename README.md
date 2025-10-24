# CV Writer 🚀

AI powered cover letter generator using web research, personalized notes to automate personalized cover letters.

## What it does

Takes your resume, your writing style, some company research, and your personal notes to generate cover letters that:

- Sound authentically like you (not a robot)
- Actually align with what the company values
- Include quantified wins and specific value props
- Skip the generic fluff and get straight to why you're a good fit

## How to use it

1. **Set up your files:**

   - `resume_input.txt` - Your resume content
   - `writing_example.txt` - Examples of your writing style
   - `global_notes.txt` - Any specific instructions or things to emphasize

2. **Install + add OPENAI_API_KEY to .env:**

   ```bash
   pip install -r requirements.txt
   ```

3. **Run it:**

   ```bash
   python cover_letter_generator.py -c "company"
   ```

   Prints to console and saves under generated_cover_letter.txt
