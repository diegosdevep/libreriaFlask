from transformers import pipeline
import os

class LibreriaAssistant:
    def __init__(self):
        # Modelo de Q&A en español
        self.qa_pipeline = pipeline(
            "question-answering",
            model="mrm8488/bert-base-spanish-wwm-cased-finetuned-spa-squad2-es"
        )
        
        # Contexto sobre cómo usar la plataforma
        self.context = """
        Bienvenido a la Librería Editorial. Esta es una plataforma donde autores pueden enviar sus manuscritos y editores pueden revisarlos.
        
        Si eres AUTOR:
        - Puedes registrarte con tu email o con Google.
        - Accede a tu dashboard en /dashboard/autor
        - Para enviar una propuesta: Click en "Nueva Propuesta"
        - Completa el formulario con: título, género, número de páginas, descripción
        - Puedes subir un archivo PDF/DOC o proporcionar un enlace
        - Tus propuestas pueden estar: Pendientes, En Revisión, Aceptadas o Rechazadas
        - Puedes editar propuestas pendientes
        - Puedes eliminar propuestas pendientes o rechazadas
        - Ver el estado de todas tus propuestas en el dashboard
        
        Si eres EDITOR:
        - Accede a tu dashboard en /dashboard/editor
        - Verás todas las propuestas enviadas por autores
        - Puedes filtrar por estado: Pendiente, En Revisión, Aceptada, Rechazada
        - Para revisar una propuesta: Click en "Ver detalles"
        - Puedes cambiar el estado de la propuesta: Aceptar, Rechazar, o Poner en Revisión
        - Una vez aceptada, puedes publicar el libro con un precio
        - Solo puedes editar propuestas que no han sido asignadas a otro editor
        
        Funciones generales:
        - Login: /login (con email/password o Google)
        - Registro: /register
        - Cerrar sesión: Click en "Cerrar sesión"
        - Catálogo: /catalogo (ver libros publicados)
        - Home: / (página principal)
        """
    
    def ask(self, question):
        """Responde preguntas sobre cómo usar la plataforma"""
        try:
            result = self.qa_pipeline({
                'question': question,
                'context': self.context
            })
            
            answer = result['answer']
            confidence = result['score']
            
            # Si la confianza es muy baja, dar una respuesta genérica
            if confidence < 0.3:
                return {
                    'answer': "No estoy seguro de esa respuesta. ¿Podrías reformular tu pregunta? Por ejemplo: '¿Cómo envío una propuesta?' o '¿Cómo reviso manuscritos?'",
                    'confidence': confidence
                }
            
            return {
                'answer': answer,
                'confidence': confidence
            }
        except Exception as e:
            return {
                'answer': "Lo siento, hubo un error procesando tu pregunta. Intenta de nuevo.",
                'confidence': 0
            }

# Instancia global
assistant = LibreriaAssistant()