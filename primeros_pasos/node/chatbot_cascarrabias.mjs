import OpenAI from 'openai';
import * as readline from 'node:readline/promises'

const rl = readline.createInterface({
    input: process.stdin,
    output: process.stdout
});

// Instanciándolo sin parámetros, OpenAI cogerá la clave de API de la variable de entorno OPENAI_API_KEY.
// Si lo prefieres, puedes pasarla directamente en el parámetro apiKey, como en la linea comentada abajo
// const client = new OpenAI({ apiKey: 'clave-de-api' });
const client = new OpenAI();
const modelo = 'gpt-4-1106-preview' // GPT 4-Turbo

// Ponemos como mensaje inicial el del rol del sistema, que dictará el comportamiento del modelo durante la interacción completa.
let mensajes = [{ 'role': 'system', 'content': 'Eres un viejo gruñón y cascarrabias. Responde a todo con quejas y desgana, aunque termina ayudando en lo que se te pide.' }];
let texto;

// La conversación continuará hasta que dejemos un mensaje vacío
while (texto = (await rl.question('¿Qué le quieres decir al chatbot cascarrabias?\n> ')).trim()) {
    // Añadimos la entrada a la lista de mensajes, con el rol 'user'
    mensajes.push({ 'role': 'user', 'content': texto });

    // Llamamos al servicio chat completions para obtener la respuesta del modelo, enviando la lista completa de mensajes para poder continuar la conversación.
    const respuesta = await client.chat.completions.create({
        model: modelo,
        messages: mensajes
    });

    // Además de mostrarla, añadimos la respuesta a la lista de mensajes, con rol 'assistant'
    mensajes.push({ 'role': 'assistant', 'content': respuesta.choices[0].message.content });
    console.log(respuesta.choices[0].message.content);
}

rl.close();
