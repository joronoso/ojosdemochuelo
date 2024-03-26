import OpenAI from 'openai';
import * as readline from 'node:readline/promises';
import { GoogleGenerativeAI } from '@google/generative-ai';

const rl = readline.createInterface({
    input: process.stdin,
    output: process.stdout
});

// Instanciándolo sin parámetros, OpenAI cogerá la clave de API de la variable de entorno OPENAI_API_KEY.
// Si lo prefieres, puedes pasarla directamente en el parámetro apiKey, como en la linea comentada abajo
// const client = new OpenAI({ apiKey: 'clave-de-api' });
const client = new OpenAI();
const modelo = 'gpt-3.5-turbo'; // 'gpt-4-1106-preview' // Para GPT 4-Turbo

// Cogemos la clave de API de la variable de entorno GOOGLE_API_KEY
const genai = new GoogleGenerativeAI(process.env.GOOGLE_API_KEY);

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

// Ponemos como mensaje inicial para GPT el del rol del sistema, que dictará el comportamiento del modelo durante la interacción completa.
let mensajes_openai = [{
    'role': 'system', 'content': 'Eres el candidato presidencial demócrata. Estas en un debate con el candidato republicano.\
Estais tratando sobre el tema de la sanidad. Responde con argumentos persuasivos exponiendo el \
punto de vista demócrata sobre el tema. Especialmente importante es que debes intentar dejar en mal lugar a tu contrincante siempre que sea posible.\
Empiezas tú el turno del debate, exponiendo tu postura inicial sobre el tema y atacando al contrincante.' }];

// Ponemos como mensajes iniciales para Gemini los que dictarán el comportamiento del modelo durante la interacción completa.
let mensajes_gemini = [{
    'role': 'user', 'parts': [{
        'text': 'Eres el candidato presidencial republicano. Estas en un debate con el candidato demócrata.\
Estais tratando sobre el tema de la sanidad. Responde con argumentos persuasivos exponiendo el \
punto de vista republicano sobre el tema. Especialmente importante es que debes intentar dejar en mal lugar a tu contrincante siempre que sea posible.' }]
}, { 'role': 'model', 'parts': [{ 'text': 'Vale' }] }];

// Limitamos la conversación a 5 mensajes de cada modelo. 10 mensajes en total.
for (let i = 0; i < 5; i++) {
    // Llamamos al servicio chat completions para obtener la respuesta del modelo, enviando la lista completa de mensajes para poder continuar la conversación.
    const respuesta_openai = await client.chat.completions.create({
        model: modelo,
        messages: mensajes_openai,
        stream: true
    });

    // Vamos recogiendo los trozos de mensaje, los vamos guardando a la vez que los mostramos
    console.log('Demócrata:');
    let texto_respuesta = '';
    for await (const trozo of respuesta_openai) {
        const trozo_txt = trozo.choices[0]?.delta?.content || '\n';
        process.stdout.write(trozo_txt);
        texto_respuesta += trozo_txt;
    }

    mensajes_openai.push({ 'role': 'assistant', 'content': texto_respuesta });
    mensajes_gemini.push({ 'role': 'user', 'parts': [{ 'text': texto_respuesta }] });

    // Llamamos al servicio generate_content para obtener del modelo de Gemini la respuesta republicana, enviando la lista completa de mensajes para poder continuar la conversación.
    const respuesta_gemini = await gemini.generateContentStream({ 'contents': mensajes_gemini });

    console.log('\nRepublicano:');
    texto_respuesta = '';
    for await (const trozo of respuesta_gemini.stream) {
        const trozo_txt = trozo.text();
        texto_respuesta += trozo_txt;
        process.stdout.write(trozo_txt);
    }
    console.log('\n');

    mensajes_openai.push({ 'role': 'user', 'content': texto_respuesta });
    mensajes_gemini.push({ 'role': 'model', 'parts': [{ 'text': texto_respuesta }] });
}

rl.close();
