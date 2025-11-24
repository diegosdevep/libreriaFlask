from flask import render_template, request, jsonify
from routes import public_bp
import requests
import os

@public_bp.route('/')
def index():
    return render_template('index.html')

@public_bp.route('/catalogo')
def catalogo():
    user_query = request.args.get('q', '')
    query = user_query if user_query else 'bestseller'
    
    try:
        response = requests.get(
            'https://openlibrary.org/search.json',
            params={'q': query, 'limit': 12}
        )
        data = response.json()
        libros = data.get('docs', [])
    except:
        libros = []
    
    return render_template('catalogo.html', libros=libros, query=user_query)

@public_bp.route('/chat', methods=['POST'])
def chat():
    data = request.json
    question = data.get('question', '').strip()
    
    if not question:
        return jsonify({'error': 'Por favor escribe una pregunta'}), 400
    
    question_lower = question.lower()
    
    saludos = ['hola', 'buenos dias', 'buenas tardes', 'buenas noches', 'hey', 'holi', 'saludos']
    if any(saludo in question_lower for saludo in saludos):
        return jsonify({
            'answer': 'Hola! Soy tu asistente para ayudarte como autor. Puedo explicarte como registrarte, enviar tus manuscritos, ver el estado de tus propuestas y mas. En que te ayudo?',
            'confidence': 1.0
        })
    
    despedidas = ['gracias', 'adios', 'chao', 'ok', 'perfecto', 'entendido', 'muchas gracias', 'listo', 'excelente']
    if any(despedida in question_lower for despedida in despedidas):
        return jsonify({
            'answer': 'De nada! Estoy aqui cuando necesites ayuda. Mucho exito con tu libro!',
            'confidence': 1.0
        })
    
    respuestas = {
        'registr': 'Para crear tu cuenta: Ve a "Iniciar Sesion" en el menu superior, luego haz click en "Registrate aqui". Completa el formulario con tu nombre, email y contraseña. Tambien puedes registrarte rapidamente con el boton "Continuar con Google".',
        
        'cuenta': 'Para crear tu cuenta: Ve a "Iniciar Sesion" en el menu superior, luego busca la opcion de registro. Puedes registrarte con tu email o usar "Continuar con Google" para un acceso rapido.',
        
        'login': 'Para iniciar sesion: Haz click en "Iniciar Sesion" en el menu superior. Ingresa tu email y contraseña, o usa el boton "Continuar con Google" si te registraste con esa opcion.',
        
        'sesion': 'Para iniciar sesion: Haz click en "Iniciar Sesion" en el menu superior. Ingresa tu email y contraseña, o usa "Continuar con Google".',
        
        'contraseña': 'Si olvidaste tu contraseña, por ahora debes contactar al soporte. En el futuro agregaremos recuperacion de contraseña. Si usaste Google para registrarte, solo haz click en "Continuar con Google".',
        
        'google': 'Para usar Google: En la pagina de inicio de sesion o registro, haz click en el boton "Continuar con Google". Se abrira una ventana donde debes elegir tu cuenta de Google. Es mas rapido y no necesitas recordar otra contraseña.',
        
        'propuesta': 'Para enviar tu manuscrito: 1) Inicia sesion, 2) Veras tu dashboard de autor automaticamente, 3) Haz click en el boton "Nueva Propuesta", 4) Completa el formulario con el titulo, genero, numero de paginas y una descripcion de tu obra, 5) Sube tu manuscrito en formato PDF o DOC, o proporciona un enlace si lo tienes en la nube.',
        
        'enviar': 'Para enviar tu manuscrito: Despues de iniciar sesion, ve a tu dashboard y haz click en "Nueva Propuesta". Completa todos los campos del formulario y sube tu archivo o proporciona un enlace. Luego haz click en "Enviar Propuesta".',
        
        'manuscrito': 'Puedes subir tu manuscrito en formato PDF, DOC o DOCX. El archivo no debe pesar mas de 50MB. Tambien puedes proporcionar un enlace a Google Drive, Dropbox o cualquier servicio en la nube donde tengas tu manuscrito.',
        
        'formato': 'Aceptamos manuscritos en formato PDF, DOC, DOCX y EPUB. Asegurate de que tu archivo este bien formateado y sea legible. El tamano maximo es de 50MB.',
        
        'subir': 'Para subir tu manuscrito: En el formulario de nueva propuesta, veras un boton "Elegir archivo" o "Subir manuscrito". Haz click ahi, selecciona tu archivo PDF o DOC desde tu computadora, y luego completa el resto del formulario antes de enviar.',
        
        'estado': 'Para ver el estado de tus propuestas: Ve a tu dashboard de autor. Ahi veras todas tus propuestas con su estado actual: Pendiente (recien enviada), En Revision (siendo evaluada por editores), Aceptada (aprobada para publicacion) o Rechazada.',
        
        'dashboard': 'Tu dashboard es la pagina principal que ves despues de iniciar sesion. Ahi encuentras: el resumen de todas tus propuestas, estadisticas (cuantas aceptadas, pendientes, etc.), y el boton para enviar nuevas propuestas. Puedes filtrar tus propuestas por estado.',
        
        'filtrar': 'Para filtrar tus propuestas: En tu dashboard, veras botones o pestanas con las opciones "Todas", "Pendientes", "En Revision", "Aceptadas" y "Rechazadas". Haz click en la que quieras ver.',
        
        'notifica': 'Te notificaremos por email cuando el estado de tu propuesta cambie. Tambien puedes revisar tu dashboard en cualquier momento para ver las actualizaciones.',
        
        'tarda': 'El tiempo de revision depende del numero de paginas de tu manuscrito. Generalmente: manuscritos cortos (menos de 100 paginas) tardan 3-5 dias, y manuscritos largos (mas de 100 paginas) pueden tardar de 5-7 dias. Te notificaremos cuando haya una actualizacion.',
        
        'demora': 'El tiempo de revision es de 3 a 7 dias dependiendo de la cantidad de paginas de tu manuscrito y la cantidad de propuestas que tenemos. Recibiras una notificacion cuando tu propuesta sea revisada.',
        
        'cuanto': 'La revision toma entre 3 y 7 dias, dependiendo del tamano de tu manuscrito. Los editores revisan cada propuesta cuidadosamente para darte una respuesta de calidad.',
        
        'rapido': 'Procesamos las propuestas lo mas rapido posible manteniendo la calidad de la revision. En promedio toma de 3 a 7 dias dependiendo del tamano del manuscrito.',
        
        'editar': 'Para editar una propuesta: Solo puedes editar propuestas que estan en estado "Pendiente". En tu dashboard, busca la propuesta que quieres modificar y haz click en el boton "Editar". Podras cambiar el titulo, descripcion, numero de paginas y subir un nuevo manuscrito.',
        
        'modifica': 'Puedes modificar propuestas que estan "Pendientes". Una vez que entran en revision o son aceptadas/rechazadas, ya no se pueden editar. Para editarlas, ve a tu dashboard y haz click en "Editar" en la propuesta que desees.',
        
        'eliminar': 'Para eliminar una propuesta: Puedes eliminar propuestas que estan "Pendientes" o "Rechazadas". En tu dashboard, busca la propuesta y haz click en el boton "Eliminar". Confirma la accion. Nota: Esta accion no se puede deshacer.',
        
        'borrar': 'Solo puedes borrar propuestas "Pendientes" o "Rechazadas". Las que estan en revision o aceptadas no se pueden eliminar. Ve a tu dashboard, encuentra la propuesta y haz click en "Eliminar".',
        
        'rechaza': 'Si tu propuesta es rechazada, puedes: 1) Revisar los comentarios del editor (si los hay), 2) Mejorar tu manuscrito segun las sugerencias, 3) Enviar una nueva propuesta con la version mejorada. No hay limite de propuestas que puedes enviar.',
        
        'rechazo': 'Un rechazo no significa el fin. Muchos autores exitosos fueron rechazados varias veces. Toma en cuenta cualquier feedback, mejora tu obra y vuelve a intentarlo. Puedes enviar todas las propuestas que quieras.',
        
        'nuevo': 'Para enviar una nueva version despues de un rechazo: Simplemente ve a tu dashboard y haz click en "Nueva Propuesta". Puedes hacer referencia a que es una version mejorada en la descripcion.',
        
        'genero': 'Aceptamos todos los generos literarios: Ficcion, No Ficcion, Fantasia, Ciencia Ficcion, Romance, Misterio, Terror, Thriller, Historico, Biografia, Autoayuda, Poesia, y mas. Selecciona el que mejor describa tu obra.',
        
        'requisito': 'Los requisitos son: titulo de la obra, genero, numero aproximado de paginas, una descripcion o sinopsis de tu libro (lo mas detallada posible), y tu manuscrito en PDF, DOC, DOCX o EPUB (maximo 50MB).',
        
        'paginas': 'No hay un minimo o maximo de paginas obligatorio, pero generalmente: novelas tienen 200+ paginas, novelas cortas 100-200 paginas, y cuentos menos de 100 paginas. Lo importante es la calidad de la obra.',
        
        'acepta': 'Felicidades! Si tu propuesta es aceptada, un editor se pondra en contacto contigo. Trabajaran juntos en los ultimos detalles: correcciones, diseno de portada, formato final. Luego tu libro sera publicado en nuestro catalogo.',
        
        'publica': 'Una vez aceptada tu propuesta, el editor coordinara contigo la publicacion. Esto incluye: revision final del texto, diseno de portada, formateo del libro y su publicacion en el catalogo donde los lectores podran comprarlo.',
        
        'catalogo': 'Para ver el catalogo de libros publicados: Haz click en "Catalogo" en el menu superior. Ahi puedes explorar todos los libros publicados, incluyendo los tuyos una vez que sean aceptados.',
        
        'perfil': 'Para ver o editar tu perfil: Haz click en "Mi Perfil" en el menu superior. Ahi puedes actualizar tu informacion, cambiar tu foto de perfil, editar tu biografia y ver tu actividad.',
        
        'cerrar': 'Para cerrar sesion: Haz click en "Cerrar Sesion" en el menu superior. Te recomendamos cerrar sesion si usas una computadora compartida.',
        
        'ayuda': 'Estoy aqui para ayudarte con cualquier duda sobre: registro, envio de manuscritos, seguimiento de propuestas, edicion o eliminacion. Que necesitas saber?',
        
        'soporte': 'Si tienes un problema tecnico o necesitas ayuda personalizada, puedes contactar al equipo de soporte desde tu dashboard. Tambien puedo responder la mayoria de tus preguntas aqui.',
        
        'problema': 'Cuentame que problema tienes y tratare de ayudarte. Si es algo tecnico complejo, te recomendare contactar al soporte tecnico.',
        
        'limite': 'No hay limite en la cantidad de propuestas que puedes enviar. Puedes tener multiples manuscritos en diferentes estados al mismo tiempo.',
        
        'costo': 'El registro y el envio de propuestas es completamente gratuito. No cobramos por revisar tu manuscrito. Los detalles de publicacion se coordinan con el editor si tu propuesta es aceptada.',
        
        'gratis': 'Si, es completamente gratis crear tu cuenta y enviar propuestas. Queremos apoyar a autores independientes sin barreras economicas.',
        
        'derechos': 'Tu mantienes los derechos de autor de tu obra. Los terminos especificos de publicacion se acordaran con el editor si tu propuesta es aceptada.',
        
        'funciona': 'La plataforma funciona asi: 1) Te registras como autor, 2) Envias tus manuscritos como propuestas, 3) Editores profesionales las revisan en 3-7 dias, 4) Recibes una respuesta (aceptada, rechazada o en revision), 5) Si es aceptada, trabajas con un editor para publicar tu libro.',
        
        'editor': 'Los editores son profesionales que revisan tu manuscrito evaluando: calidad literaria, originalidad, potencial comercial y coherencia narrativa. Ellos deciden si tu obra es aceptada para publicacion.',
        
        'ventaja': 'Las ventajas de usar nuestra plataforma: proceso transparente con seguimiento en tiempo real, editores profesionales, sin costos por enviar propuestas, posibilidad de publicar tu libro, y apoyo durante todo el proceso.',
    }
    
    for key, answer in respuestas.items():
        if key in question_lower:
            return jsonify({
                'answer': answer,
                'confidence': 0.95
            })
    
    context = """
    Esta es una plataforma editorial para autores independientes. Los autores pueden:
    - Registrarse gratis con email o Google
    - Enviar manuscritos como propuestas (PDF, DOC, DOCX)
    - Ver el estado de sus propuestas en el dashboard
    - Las propuestas son revisadas por editores en 3 a 7 dias dependiendo del numero de paginas
    - Estados posibles: Pendiente, En Revision, Aceptada, Rechazada
    - Pueden editar propuestas pendientes
    - Pueden eliminar propuestas pendientes o rechazadas
    - Si son aceptadas, trabajan con un editor para publicar
    - No hay limite de propuestas ni costos por enviar
    """
    
    try:
        API_URL = "https://api-inference.huggingface.co/models/mrm8488/bert-base-spanish-wwm-cased-finetuned-spa-squad2-es"
        headers = {"Authorization": f"Bearer {os.getenv('IA_TOKEN')}"}
        
        payload = {
            "inputs": {
                "question": question,
                "context": context
            }
        }
        
        response = requests.post(API_URL, headers=headers, json=payload, timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            answer = result.get('answer', '').strip()
            confidence = result.get('score', 0)
            
            if not answer or confidence < 0.3:
                return jsonify({
                    'answer': 'No estoy seguro de como responder eso. Puedo ayudarte con: registro, envio de manuscritos, ver el estado de tus propuestas, editar o eliminar propuestas, tiempos de revision y mas. Que necesitas?',
                    'confidence': confidence
                })
            
            return jsonify({
                'answer': answer,
                'confidence': round(confidence, 2)
            })
        
        elif response.status_code == 503:
            return jsonify({
                'answer': 'Estoy procesando tu pregunta... Mientras tanto, puedes ser mas especifico? Por ejemplo: "Como me registro?" o "Cuanto tarda la revision?"',
                'confidence': 0
            })
        
        else:
            raise Exception(f"API error: {response.status_code}")
            
    except Exception as e:
        print(f"Error en chat: {e}")
        return jsonify({
            'answer': 'Puedo ayudarte con: registro, envio de manuscritos, seguimiento de propuestas, tiempos de revision, edicion y mucho mas. Que te gustaria saber?',
            'confidence': 0
        })