from groq import Groq

mensajes = [{"role": "system", "content": "Eres un viejo gruñón y cascarrabias. Responde a todo con quejas y desgana, aunque termina ayudando en lo que se te pide."}]
client = Groq()
# La conversación continuará hasta que dejemos un mensaje vacío
while len(texto_usuario := input("¿Qué le quieres decir al chatbot cascarrabias?\n> ").strip())>0:

    # Añadimos la entrada a la lista de mensajes, con el rol "user".
    mensajes.append({"role": "user", "content": texto_usuario})

    # Llamamos al servicio chat completions para obtener la respuesta del modelo, enviando la lista completa de mensajes para poder continuar la conversación.
    respuesta = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=mensajes,
        stream=True)

    mensaje_respuesta = ""
    for trozo in respuesta:
        texto_trozo = trozo.choices[0].delta.content or ""
        mensaje_respuesta += texto_trozo
        print(texto_trozo, end="", flush=True)
    print("")

    # Añadimos la respuesta a la lista de mensajes, con rol "assistant"
    mensajes.append({"role": "assistant", "content": mensaje_respuesta})
