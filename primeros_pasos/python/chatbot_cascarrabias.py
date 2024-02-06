from openai import OpenAI

# Instanciándolo sin parámetros, OpenAI cogerá la clave de API de la variable de entorno OPENAI_API_KEY.
# Si lo prefieres, puedes pasarla directamente en el parámetro apiKey, como en la linea comentada abajo
#client = OpenAI(api_key='clave-de-api',)
client = OpenAI()
modelo = 'gpt-4-1106-preview' # GPT 4-Turbo

# Ponemos como mensaje inicial el del rol del sistema, que dictará el comportamiento del modelo durante la interacción completa.
mensajes = [{'role': 'system', 'content': 'Eres un viejo gruñón y cascarrabias. Responde a todo con quejas y desgana, aunque termina ayudando en lo que se te pide.'}]
while True:
    # La conversación continuará hasta que dejemos un mensaje vacío
    texto_user = input('¿Qué le quieres decir al chatbot cascarrabias?\n> ').strip()
    if len(texto_user)==0: 
        break

    # Añadimos la entrada a la lista de mensajes, con el rol 'user'
    mensajes.append({'role': 'user', 'content': texto_user})

    # Llamamos al servicio chat completions para obtener la respuesta del modelo, enviando la lista completa de mensajes para poder continuar la conversación.
    respuesta = client.chat.completions.create(
        model=modelo,
        messages=mensajes
    )

    # Además de mostrarla, añadimos la respuesta a la lista de mensajes, con rol 'assistant'
    print(respuesta.choices[0].message.content)
    mensajes.append({'role': 'assistant', 'content': respuesta.choices[0].message.content})

