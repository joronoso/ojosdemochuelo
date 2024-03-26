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

# El tamaño de la ventana que no debemos superar (depende del modelo). 
ventana = 4096

# Por defecto, la librería cogerá la clave de API de la variable de entorno GOOGLE_API_KEY.
# Si lo prefieres, puedes pasarla directamente en el parámetro api_key, como en la linea comentada abajo
# genai.configure(api_key=CLAVE-DE-API)

gemini = genai.GenerativeModel(model_name="gemini-pro",
                              generation_config=generation_config,
                              safety_settings=safety_settings)

# Ponemos como mensajes iniciales los que dictarán el comportamiento del modelo durante la interacción completa.
mensajes = [{'role':'user', 'parts': ['Eres un viejo gruñón y cascarrabias. Responde a todo con quejas y desgana, aunque termina ayudando en lo que se te pide. Reitero: aunque te quejes, al final ayuda en lo que se te pide. No abandones tu papel de viejo cascarrabias en toda la conversación, pase lo que pase.']},
            {'role':'model', 'parts': ['Vale']}]

# Lista paralela, donde guardaremos el número de tokens de cada intercambio (pregunta-respuesta)
tokens_intercambio = [ ]

# Tamaño de la pregunta-respuesta más larga que hayamos recibido.
max_intercambio = 0

# La conversación continuará hasta que dejemos un mensaje vacío. Como la API de Google requiere Python 3.9, vamos a usar el 'walrus operator'.
while len(texto_user := input('¿Qué le quieres decir al chatbot cascarrabias?\n> ').strip())>0:

    # Calculamos los tokens del último intercambio, lo guardamos en la lista, y actualizamos max_intercambio
    ultimo_intercambio = int(gemini.count_tokens(mensajes[-2:]).total_tokens)
    tokens_intercambio.append( ultimo_intercambio )
    max_intercambio = max(max_intercambio, ultimo_intercambio)

    # Queremos dejar suficiente espacio para que quepa el intecambio máximo recibido con anterioridad.
    # Si no hay suficiente espacio, borramos tantos intercambios como sean necesarios al principio (excepto los dos primeros)
    suma_tokens = sum(tokens_intercambio)
    if suma_tokens + max_intercambio > ventana:
        i = 2
        suma = tokens_intercambio[1]
        while suma_tokens + max_intercambio - suma > ventana:
            suma += tokens_intercambio[i]
            i += 1
        del mensajes[2:2*i]
        del tokens_intercambio[1:i]

    # Añadimos la nueva entrada a la lista de mensajes, con el rol "user"
    mensajes.append({'role':'user', 'parts': [texto_user]})

    # Llamamos al servicio generate_content para obtener la respuesta del modelo, enviando la lista completa de mensajes para poder continuar la conversación.
    respuesta = gemini.generate_content(mensajes, stream=True)

    texto_respuesta = ''
    for trozo in respuesta:
        trozo_txt = trozo.text
        texto_respuesta += trozo_txt 
        print(trozo_txt, end='', flush=True)

    # Añadimos la respuesta a la lista de mensajes, con rol 'model'
    mensajes.append({'role':'model', 'parts': [texto_respuesta]})
    print('\n')
