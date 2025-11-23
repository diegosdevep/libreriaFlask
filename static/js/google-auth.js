import { initializeApp } from 'https://www.gstatic.com/firebasejs/10.7.1/firebase-app.js';
import {
  getAuth,
  signInWithPopup,
  GoogleAuthProvider,
} from 'https://www.gstatic.com/firebasejs/10.7.1/firebase-auth.js';

function showError(message) {
  document.querySelector('.spinner').style.display = 'none';
  document.querySelector('.progress-bar').style.display = 'none';
  document.querySelector('.loading-text').style.display = 'none';
  document.querySelector('.google-badge').style.display = 'none';
  document.getElementById('errorText').textContent = message;
  document.getElementById('errorMessage').classList.add('show');
}

export function initGoogleAuth(firebaseConfig) {
  const app = initializeApp(firebaseConfig);
  const auth = getAuth(app);
  const provider = new GoogleAuthProvider();

  provider.addScope('email');
  provider.addScope('profile');

  signInWithPopup(auth, provider)
    .then((result) => {
      console.log('Usuario autenticado:', result.user.email);
      return result.user.getIdToken();
    })
    .then((idToken) => {
      console.log('Token obtenido, verificando con servidor...');
      return fetch('/verify-token', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ idToken: idToken }),
      });
    })
    .then((response) => {
      if (!response.ok) {
        throw new Error('Error al verificar el token con el servidor');
      }
      return response.json();
    })
    .then((data) => {
      if (data.success) {
        console.log('Autenticación exitosa, redirigiendo...');
        window.location.href = data.redirect;
      } else {
        throw new Error(data.error || 'Error desconocido');
      }
    })
    .catch((error) => {
      console.error('Error de autenticación:', error);

      let errorMessage = 'No se pudo completar la autenticación';

      if (error.code === 'auth/popup-closed-by-user') {
        errorMessage =
          'Cerraste la ventana de Google. Por favor intenta de nuevo.';
      } else if (error.code === 'auth/popup-blocked') {
        errorMessage =
          'El navegador bloqueó la ventana emergente. Habilita popups e intenta de nuevo.';
      } else if (error.code === 'auth/cancelled-popup-request') {
        errorMessage = 'Se canceló la solicitud. Intenta de nuevo.';
      } else if (error.message) {
        errorMessage = error.message;
      }

      showError(errorMessage);
    });
}
