from transformers import pipeline, AutoTokenizer

# Gemma 2 no soporta mensajes de sistema
mensajes = [{"role": "user", "content": "Eres un viejo gruñón y cascarrabias. Responde a todo con quejas y desgana, aunque termina ayudando en lo que se te pide."},
            {"role": "assistant", "content": "OK."}]

pipe = pipeline(
    task="text-generation",
    model="google/gemma-2-2b-it",
    device="cuda",  # "mps" para Mac, "cpu" si no tienes GPU
    token="HF_TOKEN", 
)

# La conversación continuará hasta que dejemos un mensaje vacío
while len(texto_usuario := input("¿Qué le quieres decir al chatbot cascarrabias?\n> ").strip())>0:
    # Añadimos la entrada a la lista de mensajes, con el rol "user".
    mensajes.append({"role": "user", "content": texto_usuario})

    # Generamos la respuesta del modelo usando pipe, enviando la lista completa de mensajes para poder continuar la conversación.
    mensaje_respuesta = pipe(mensajes, max_new_tokens=256)[0]["generated_text"][-1]["content"]

    # Añadimos la respuesta a la lista de mensajes, con rol "assistant"
    print(mensaje_respuesta)
    mensajes.append({"role": "assistant", "content": mensaje_respuesta})