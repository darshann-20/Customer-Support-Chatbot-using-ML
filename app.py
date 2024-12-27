from flask import Flask, render_template, request, jsonify
import openai
from googletrans import Translator

app = Flask(__name__)

# Initialize OpenAI API and Translator
openai.api_key = '# Replace with your actual OpenAI API key'
translator = Translator()

# List of supported languages for targeted output
SUPPORTED_LANGUAGES = {"kn": "Kannada", "ta": "Tamil", "te": "Telugu", "hi": "Hindi"}

def detect_language(text):
    """Detect the language of the input text."""
    try:
        detection = translator.detect(text)
        return detection.lang
    except Exception as e:
        return "en"  # Default to English if detection fails

def translate_to_english(text, source_lang):
    """Translate text to English if not already in English."""
    if source_lang == "en":
        return text
    try:
        translated = translator.translate(text, src=source_lang, dest="en")
        return translated.text
    except Exception as e:
        return text  # Return original text if translation fails

def translate_to_target_language(text, target_lang):
    """Translate text from English to the target language."""
    if target_lang == "en":
        return text
    try:
        translated = translator.translate(text, src="en", dest=target_lang)
        return translated.text
    except Exception as e:
        return text  # Return original text if translation fails

def get_response_in_english(prompt):
    """Get a response from OpenAI GPT model in English."""
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a helpful customer support assistant."},
                {"role": "user", "content": prompt},
            ],
        )
        return response['choices'][0]['message']['content']
    except Exception as e:
        return "I'm sorry, I couldn't process your request."

def multilingual_chatbot(user_input):
    """Main chatbot function to handle multilingual support."""
    # Step 1: Detect the user's language
    user_language = detect_language(user_input)

    # Check if the user's language is among the supported ones
    if user_language not in SUPPORTED_LANGUAGES and user_language != "en":
        return f"Sorry, your language ({user_language}) is not currently supported."

    # Step 2: Translate input to English (if needed)
    translated_input = translate_to_english(user_input, user_language)

    # Step 3: Generate a response in English
    english_response = get_response_in_english(translated_input)

    # Step 4: Translate the response back to the user's language
    final_response = translate_to_target_language(english_response, user_language)

    return final_response

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    user_message = request.json.get('message')
    response = multilingual_chatbot(user_message)
    return jsonify({'response': response})

if __name__ == '__main__':
    app.run(debug=True)
