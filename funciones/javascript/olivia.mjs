import * as readline from "node:readline/promises";
import { GoogleGenerativeAI } from "@google/generative-ai";
import fs from "fs";
import Database from 'better-sqlite3';

const declaracionGuardarReceta = {
    name: "guardarReceta",
    parameters: {
        type: "OBJECT",
        description: "Guarda una nueva receta",
        properties: {
            nombre: {
                type: "STRING",
                description: "Nombre de la receta.",
            },
            ingredientes: {
                type: "STRING",
                description: "Lista de ingredientes necesarios para preparar la receta, con sus cantidades.",
            },
            preparacion: {
                type: "STRING",
                description: "Lista de pasos específicos necesarios para preparar la receta, incluyendo el orden, tiempos de cocción y cualquier criterio que sea necesario especificar para que una persona sin conocimiento previo pueda elaborarla con éxito.",
            },
        },
        required: ["nombre", "ingredientes", "preparacion"],
    }
};

const declaracionListarRecetas = {
    name: "listarRecetas"
}

let tablaExiste = false

function listarRecetas() {
    let recetas, db;
    try {
        db = new Database('recetas.db');
        const stmt = db.prepare("select nombre, ingredientes, preparacion from receta");
        recetas = stmt.all();
        tablaExiste = true;
    } catch {
        recetas = "No hay recetas.";
    } finally {
        db.close();
    }
    return recetas;
}

function guardarReceta(nombre, ingredientes, preparacion) {
    let resultado, db;
    try {
        db = new Database('recetas.db');
        if (!tablaExiste) {
            const stmtTabla = db.prepare(`CREATE TABLE if not exists receta (
                [nombre] TEXT NOT NULL,
                [ingredientes] TEXT,
                [preparacion] TEXT)`);
            stmtTabla.run();
        }
        const stmtInsert = db.prepare("insert into receta (nombre, ingredientes, preparacion) values (?,?,?)");
        stmtInsert.run(nombre, ingredientes, preparacion);
        resultado = "OK";
    } catch {
        resultado = "Error guardando la receta";
    } finally {
        db.close();
    }
    return resultado;
}

class ClienteGemini {
    constructor(modelo, mensajeSistema) {
        this.modelo = modelo;
        const genai = new GoogleGenerativeAI(process.env.GOOGLE_API_KEY);
        let cliente = genai.getGenerativeModel(
            {
                model: modelo,
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
                tools: {
                    functionDeclarations: [declaracionGuardarReceta, declaracionListarRecetas],
                },
            }, { apiVersion: 'v1beta', });
        this.sesionChat = cliente.startChat();
        this.sesionChat.sendMessage(mensajeSistema); // No mostramos la respuesta, así que no necesitamos hacer nada con la promesa
    }

    async _chat(nombreFuncion, respuestaFuncion) {
        const ret = await this.sesionChat.sendMessage([{ "functionResponse": { "name": nombreFuncion, "response": { recetas: respuestaFuncion } } }]);
        return ret.response.text();
    }

    async chat(mensajeUsuario) {
        const respuesta = await this.sesionChat.sendMessage(mensajeUsuario);
        let mensajeModelo;
        if (respuesta.response.functionCall()) {
            const fc = respuesta.response.functionCall();
            console.log("-- function call: " + fc.name); // Para tener visibilidad de las llamadas que se producen
            if (fc.name === "listarRecetas") {
                mensajeModelo = await this._chat(fc.name, listarRecetas());
            } else if (fc.name === "guardarReceta") {
                mensajeModelo = await this._chat(fc.name, guardarReceta(fc.args.nombre, fc.args.ingredientes, fc.args.preparacion));
            } else {
                mensajeModelo = "Llamada a función!! " + fc.name;
            }
        } else mensajeModelo = respuesta.response.text();
        return mensajeModelo;
    }
}

const rl = readline.createInterface({
    input: process.stdin,
    output: process.stdout
});

let cliente = new ClienteGemini("gemini-1.0-pro", fs.readFileSync("olivia.md", "utf8"), 2);
let texto_user;
while (texto_user = (await rl.question('¿Qué le quieres decir a Olivia?\n> ')).trim()) {
    console.log(await cliente.chat(texto_user));
}
rl.close();