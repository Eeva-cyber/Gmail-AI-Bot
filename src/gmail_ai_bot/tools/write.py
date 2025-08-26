# rejection email
def generate_rejection_email(first_name: str, feedback: str) -> str:
    prompt = (
        f"Write a short, professional, and warm rejection email to an applicant named {first_name} "
        f"for a university student club, based on the following bullet point feedback:\n- {feedback}\n\n"
        "Keep the tone kind and encouraging. Do NOT include a subject line.\n"
        "Start with 'Dear {name},'. Keep it concise — no more than 3 short paragraphs.\n"
        "End with a warm invitation to apply again next semester.\n"
        "Sign off as 'DsCubed Recruitment Team'. Please structure the email as a properly formatted email in HTML and remove the HTML tag."
    )

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are a professional and kind recruiter at a student club."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7,
        max_tokens=300
    )

    return response.choices[0].message.content.strip()


