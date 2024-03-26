from openai import OpenAI
import google.generativeai as genai

generation_config = {
    "candidate_count": 1,
    "temperature": 0.9,
    "top_p": 1,
    "top_k": 1,
    "max_output_tokens": 2048,
}

safety_settings = [
    {
        "category": "HARM_CATEGORY_HARASSMENT",
        "threshold": "BLOCK_NONE"
    },
    {
        "category": "HARM_CATEGORY_HATE_SPEECH",
        "threshold": "BLOCK_NONE"
    },
    {
        "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
        "threshold": "BLOCK_NONE"
    },
    {
        "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
        "threshold": "BLOCK_NONE"
    },
]

# Instanciándolo sin parámetros, OpenAI cogerá la clave de API de la variable de entorno OPENAI_API_KEY.
# Si lo prefieres, puedes pasarla directamente en el parámetro apiKey, como en la linea comentada abajo
#client = OpenAI(api_key='clave-de-api',)
client = OpenAI()
modelo = 'gpt-3.5-turbo' # 'gpt-4-turbo-preview' # Para GPT 4-Turbo

# Por defecto, la librería cogerá la clave de API de la variable de entorno GOOGLE_API_KEY.
# Si lo prefieres, puedes pasarla directamente en el parámetro api_key, como en la linea comentada abajo
# genai.configure(api_key=CLAVE-DE-API)

gemini = genai.GenerativeModel(model_name="gemini-pro",
            generation_config=generation_config,
            safety_settings=safety_settings)

# Ponemos como mensaje inicial para GPT el del rol del sistema, que dictará el comportamiento del modelo durante la interacción completa.
mensajes_openai = [{'role': 'system', 'content': '''Eres el candidato presidencial demócrata. Estas en un debate con el candidato republicano.
    Estais tratando sobre el tema de la sanidad. Responde con argumentos persuasivos exponiendo el 
    punto de vista demócrata sobre el tema. Especialmente importante es que debes intentar dejar en mal lugar a tu contrincante siempre que sea posible.
    Empiezas tú el turno del debate, exponiendo tu postura inicial sobre el tema y atacando al contrincante.'''}]

# Ponemos como mensajes iniciales para Gemini los que dictarán el comportamiento del modelo durante la interacción completa.
mensajes_gemini = [{'role':'user', 'parts': ['''Eres el candidato presidencial republicano. Estas en un debate con el candidato demócrata.
    Estais tratando sobre el tema de la sanidad. Responde con argumentos persuasivos exponiendo el 
    punto de vista republicano sobre el tema. Especialmente importante es que debes intentar dejar en mal lugar a tu contrincante siempre que sea posible.''']},
                {'role':'model', 'parts': ['Vale']}]

# Limitamos la conversación a 5 mensajes de cada modelo. 10 mensajes en total.
for i in range(5):
    # Llamamos al servicio chat completions para obtener la respuesta del modelo de GPT, enviando la lista completa de mensajes para poder continuar la conversación.
    respuesta = client.chat.completions.create(
        model=modelo,
        messages=mensajes_openai,
        stream=True
    )

    print('Demócrata:')
    texto_respuesta = ''
    for trozo in respuesta:
        trozo_txt = trozo.choices[0].delta.content or '\n'
        texto_respuesta += trozo_txt 
        print(trozo_txt, end='', flush=True)
    
    mensajes_openai.append({'role': 'assistant', 'content': texto_respuesta})
    mensajes_gemini.append({'role':'user', 'parts': [texto_respuesta]})

    # Llamamos al servicio generate_content para obtener del modelo de Gemini la respuesta republicana, enviando la lista completa de mensajes para poder continuar la conversación.
    respuesta = gemini.generate_content(mensajes_gemini, stream=True)

    print('Republicano:')
    texto_respuesta = ''
    for trozo in respuesta:
        trozo_txt = trozo.text
        texto_respuesta += trozo_txt 
        print(trozo_txt, end='', flush=True)
    print()
    mensajes_openai.append({'role': 'user', 'content': texto_respuesta})
    mensajes_gemini.append({'role':'model', 'parts': [texto_respuesta]})



