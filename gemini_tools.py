from google import genai
from config import API_KEY
from models import word_context


def get_word_info(word: str, definition: str):

    contents = ' '.join([
        'I am studying for the SAT\'s and am trying to learn vocabulary words for the verbal section.'
        f'Given the word: {word}, and the general definition: {definition}',
        'Please provide a concise and accurate definition of the word, two very close synonyms, and use the word in two interesting, and memorable sentences in a way that the meaning of the word is clear based on the context.',
    ])

    client = genai.Client(api_key=API_KEY)

    try: 
        response = client.models.generate_content(
            model="gemini-2.0-flash", 
            contents=contents,
            config = {
                'response_mime_type': 'application/json',
                'response_schema': list[word_context],
            }
        )
        if response.prompt_feedback and response.prompt_feedback.block_reason:
            print(f"Blocked for reason: {response.prompt_feedback.block_reason}")
            return None
        [answer] = response.parsed
        return answer
    except Exception as e:
        print(f'Exception: {e}')
        return None
    