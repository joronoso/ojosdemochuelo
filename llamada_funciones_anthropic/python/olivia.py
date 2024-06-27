from anthropic import Anthropic
import sqlite3
import io
import json

declaracion_guardar_receta = {
    "name": "guardar_receta",
    "description": "Guarda una nueva receta",
    "input_schema": {
        "type": "object",
        "properties": {
            "nombre": {
                "type": "string",
                "description": "Nombre de la receta.",
            },
            "ingredientes": {
                "type": "string",
                "description": "Lista de ingredientes necesarios para preparar la receta, con sus cantidades.",
            },
            "preparacion": {
                "type": "string",
                "description": "Lista de pasos específicos necesarios para preparar la receta, incluyendo el orden, tiempos de cocción y cualquier criterio que sea necesario especificar para que una persona sin conocimiento previo pueda elaborarla con éxito.",
            },
        },
        "required": ["nombre", "ingredientes", "preparacion"],
    }
}

declaracion_listar_recetas = {
    "name": "listar_recetas",
    "description": "Lista las recetas guardadas.",
    "input_schema": {
        "type": "object",
        "properties": {}
    }
}

tabla_existe = False

def listar_recetas():
    # Obtiene la lista de recetas guardadas
    conn = sqlite3.connect("recetas.db")
    try:
        recetas = [{"nombre":row[0], "ingredientes":row[1], "preparacion":row[2]} for row in conn.execute("select nombre, ingredientes, preparacion from receta")]
    except:
        recetas = []
    conn.close()
    return recetas

def guardar_receta(nombre, ingredientes, preparacion):
    # Guarda una nueva receta
    conn = sqlite3.connect("recetas.db")
    cur = conn.cursor()
    if not tabla_existe:
        cur.execute("""CREATE TABLE if not exists receta (
                    [nombre] TEXT NOT NULL,
                    [ingredientes] TEXT,
                    [preparacion] TEXT)""")
    cur.execute("insert into receta (nombre, ingredientes, preparacion) values (?,?,?)",
                (nombre, ingredientes, preparacion))
    conn.commit()
    cur.close()
    conn.close()

class ClienteClaude:
    def __init__(self, modelo, mensaje_sistema):
        self.modelo = modelo
        self.mensaje_sistema = mensaje_sistema
        self.anthropic = Anthropic()
        self.mensajes = []

    def __llama_funcion(self, llf):
        if llf.name == "listar_recetas":
            return json.dumps(listar_recetas())
        elif llf.name == "guardar_receta":
            return json.dumps(guardar_receta(llf.input["nombre"], llf.input["ingredientes"], llf.input["preparacion"]))


    def chat(self, mensaje_usuario):
        self.mensajes.append(
            {
                "role": "user",
                "content": mensaje_usuario
            }
        )
        respuesta = self.anthropic.messages.create(
            max_tokens=4096,
            system=self.mensaje_sistema,
            messages=self.mensajes,
            model = self.modelo,
            tools=[declaracion_guardar_receta, declaracion_listar_recetas]
        )
        self.mensajes.append(
             {
                "role": "assistant",
                "content": respuesta.content
            }
        )
        if respuesta.stop_reason == "tool_use":
            salida = ""
            resultado_funcion = []
            for c in respuesta.content:
                if c.type == "text":
                    salida = c.text
                elif c.type == "tool_use":
                    resultado_funcion.append(
                        {
                            "type": "tool_result",
                            "tool_use_id": c.id,
                            "content": self.__llama_funcion(c)
                        })
            self.mensajes.append(
                {
                    "role": "user",
                    "content": resultado_funcion
                })
            respuesta2 = respuesta = self.anthropic.messages.create(
                max_tokens=4096,
                system=self.mensaje_sistema,
                messages=self.mensajes,
                model = self.modelo,
                tools=[declaracion_guardar_receta, declaracion_listar_recetas]
            )
            self.mensajes.append(
                {
                    "role": "assistant",
                    "content": respuesta2.content
                }
            )
            return salida+"\n"+respuesta2.content[0].text
        
        return respuesta.content[0].text

with io.open("olivia.md", "r") as arch:
    mensaje_sistema = "\n".join(arch.readlines())

cliente = ClienteClaude("claude-3-5-sonnet-20240620", mensaje_sistema)
while (texto_usuario := input("¿Qué le quieres decir a Olivia?\n> ").strip()) !="":
    if len(texto_usuario)==0: 
        break
    print(cliente.chat(texto_usuario))

