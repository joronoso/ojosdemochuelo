import ollama

mensajes = [{"role": "system", "content": "Eres un viejo gruñón y cascarrabias. Responde a todo con quejas y desgana, aunque termina ayudando en lo que se te pide."}]

# La conversación continuará hasta que dejemos un mensaje vacío
while len(texto_usuario := input("¿Qué le quieres decir al chatbot cascarrabias?\n> ").strip())>0:

    # Añadimos la entrada a la lista de mensajes, con el rol "user".
    mensajes.append({"role": "user", "content": texto_usuario})

    # Llamamos al servicio chat para obtener la respuesta del modelo, enviando la lista completa de mensajes para poder continuar la conversación.
    respuesta = ollama.chat(
        model="phi3.5:latest",
        messages=mensajes,
        stream=True)

    mensaje_respuesta = ""
    for trozo in respuesta:
        mensaje_respuesta += trozo["message"]["content"]
        print(trozo["message"]["content"], end="", flush=True)
    print("")

    # Añadimos la respuesta a la lista de mensajes, con rol "assistant"
    mensajes.append({"role": "assistant", "content": mensaje_respuesta})
