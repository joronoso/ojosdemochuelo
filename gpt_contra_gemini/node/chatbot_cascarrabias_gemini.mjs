import * as readline from 'node:readline/promises';
import { GoogleGenerativeAI } from '@google/generative-ai';

const rl = readline.createInterface({
    input: process.stdin,
    output: process.stdout
});

// Cogemos la clave de API de la variable de entorno GOOGLE_API_KEY
const genai = new GoogleGenerativeAI(process.env.GOOGLE_API_KEY);

// El tamaño de la ventana que no debemos superar (también depende del modelo). 
const ventana = 4096

const gemini = genai.getGenerativeModel(
    {
        model: 'gemini-pro',
        safetySettings: [
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
        ],
        generationConfig: {
            //candidateCount: 1,
            //maxOutputTokens: 1700,
            stopSequences: [],
            temperature: 1,
            topK: 1,
            topP: 1
        }

    });

// Ponemos como mensajes iniciales los que dictarán el comportamiento del modelo durante la interacción completa.
let mensajes = [{ 'role': 'user', 'parts': [{ 'text': 'Eres un viejo gruñón y cascarrabias. Responde a todo con quejas y desgana, aunque termina ayudando en lo que se te pide. Reitero: aunque te quejes, al final ayuda en lo que se te pide. No abandones tu papel de viejo cascarrabias en toda la conversación, pase lo que pase.' }] },
{ 'role': 'model', 'parts': [{ 'text': 'Vale' }] }];

// Array paralelo, donde guardaremos el número de tokens de cada mensaje.
let tokens_intercambio = [];

// Tamaño de la pregunta-respuesta más larga que hayamos recibido.
let max_intercambio = 0

// La conversación continuará hasta que dejemos un mensaje vacío.
let texto_user;
while (texto_user = (await rl.question('¿Qué le quieres decir al chatbot cascarrabias?\n> ')).trim()) {
    // Calculamos los tokens del último intercambio, lo guardamos en la lista, y actualizamos max_intercambio
    const ultimo_intercambio = (await gemini.countTokens({ 'contents': mensajes.slice(mensajes.length - 2, mensajes.length) })).totalTokens;
    tokens_intercambio.push(ultimo_intercambio);
    max_intercambio = max_intercambio > ultimo_intercambio ? max_intercambio : ultimo_intercambio;

    // Queremos dejar suficiente espacio para que quepa el intecambio máximo recibido con anterioridad.
    // Si no hay suficiente espacio, borramos tantos intercambios como sean necesarios al principio (excepto los dos primeros)
    const suma_tokens = tokens_intercambio.reduce((sum, elem) => sum + elem, 0);
    if (suma_tokens + max_intercambio > ventana) {
        let i = 2;
        let suma = tokens_intercambio[1];
        while (suma_tokens + max_intercambio - suma > ventana) {
            suma += tokens_intercambio[i];
            i++;
        }
        mensajes.splice(2, 2 * (i - 1));
        tokens_intercambio.splice(1, i - 1);
    }

    // Añadimos la nueva entrada a la lista de mensajes, con el rol "user"
    mensajes.push({ 'role': 'user', 'parts': [{ 'text': texto_user }] });

    // Llamamos al servicio generate_content para obtener la respuesta del modelo, enviando la lista completa de mensajes para poder continuar la conversación.
    const respuesta = await gemini.generateContentStream({ 'contents': mensajes });

    let texto_respuesta = '';
    for await (const trozo of respuesta.stream) {
        const trozo_txt = trozo.text();
        texto_respuesta += trozo_txt;
        process.stdout.write(trozo_txt);
    }

    // Añadimos la respuesta a la lista de mensajes, con rol "model"
    mensajes.push({ 'role': 'model', 'parts': [{ 'text': texto_respuesta }] });

    console.log('\n');
}

rl.close();
