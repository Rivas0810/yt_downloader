// --- HTML de la Interfaz ---

const statusMessageHTML = `
  <div id="status-message" class="status-hidden"></div>
`;

// HTML para los botones principales
const mainButtonsHTML = `
  <div id="main-buttons">
    <button id="dl-video-btn" class="action-btn video-btn">Descargar Video</button>
    <button id="dl-audio-btn" class="action-btn audio-btn">Descargar Audio</button>
  </div>
`;

// HTML para el formulario de metadatos de audio
const audioFormHTML = `
  <div id="audio-form" class="hidden">
    <h4>Metadatos de Audio</h4>
    <div class="form-group">
      <label for="audio-title">Título:</label>
      <input type="text" id="audio-title" placeholder="Nombre de la canción" autocomplete="off">
    </div>
    <div class="form-group">
      <label for="audio-artist">Artista:</label>
      <input type="text" id="audio-artist" placeholder="Nombre del artista" autocomplete="off">
    </div>
    <div class="form-group">
      <label for="audio-album">Álbum:</label>
      <input type="text" id="audio-album" placeholder="Nombre del álbum" autocomplete="off">
    </div>
    <div class="form-group">
      <label for="audio-art">URL de Portada:</label>
      <input type="text" id="audio-art" placeholder="https://.../imagen.jpg" autocomplete="off">
    </div>
    <div class="button-group">
      <button id="submit-audio-btn">Confirmar</button>
      <button id="cancel-audio-btn">Cancelar</button>
    </div>
  </div>
`;

const footerHTML = `
  <div id="panel-footer">Hecho por Fernando Rivas</div>
`;

// --- Creación e Inyección del Panel ---

const panel = document.createElement('div');
panel.id = 'flask-downloader-panel';

// Estructura: Botón Toggle (fuera del flow principal visualmente gracias a CSS) + Contenido
panel.innerHTML = `
    <button id="toggle-panel-btn" title="Abrir/Cerrar">⮕</button>
    <h3>Descargador de Youtube</h3>
    ${statusMessageHTML}
    ${mainButtonsHTML}
    ${audioFormHTML}
    ${footerHTML}

`;

document.body.appendChild(panel);

// --- Referencias ---

const toggleBtn = document.getElementById('toggle-panel-btn');
const mainButtonsDiv = document.getElementById('main-buttons');
const audioFormDiv = document.getElementById('audio-form');
const dlVideoBtn = document.getElementById('dl-video-btn');
const dlAudioBtn = document.getElementById('dl-audio-btn');
const submitAudioBtn = document.getElementById('submit-audio-btn');
const cancelAudioBtn = document.getElementById('cancel-audio-btn');
const flaskEndpoint = 'http://localhost:5000';
let statusTimer;

// --- Lógica de la Ventana Deslizante ---

toggleBtn.addEventListener('click', () => {
    panel.classList.toggle('panel-collapsed');
    
    // Cambiar la flechita del botón
    //toggleBtn.textContent = '⬅'; // Flecha apuntando a la izquierda (para abrir)

    if (panel.classList.contains('panel-collapsed')) {
        toggleBtn.textContent = '▶'; // Flecha apuntando a la izquierda (para abrir)
    } else {
        toggleBtn.textContent = '⮕'; // Flecha apuntando a la derecha (para cerrar)
    }
});

// --- Lógica del Downloader ---

function clearData(){
  document.getElementById('audio-title').value = '';
  document.getElementById('audio-artist').value = '';
  document.getElementById('audio-album').value = '';
  document.getElementById('audio-art').value = '';
}

function showStatusMessage(message, type = 'success') {
  const statusEl = document.getElementById('status-message');
  if (!statusEl) return;
  
  clearTimeout(statusTimer);
  statusEl.textContent = message;
  
  statusEl.className = ''; 
  statusEl.classList.add(type === 'success' ? 'status-success' : 'status-error');
  
  statusTimer = setTimeout(() => {
    statusEl.classList.add('status-hidden');
  }, 3000);
}

dlVideoBtn.addEventListener('click', () => {
  const currentUrl = window.location.href;
  console.log('Enviando solicitud de VIDEO para:', currentUrl);
  showStatusMessage('Enviando solicitud...', 'success');

  fetch(`${flaskEndpoint}/download_video`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ url: currentUrl }),
  })
  .then(response => response.json())
  .then(data => {
    showStatusMessage(data.mensaje || '¡Solicitud enviada!', 'success');
  })
  .catch(error => {
    console.log(error);
    showStatusMessage('Error al conectar con servidor', 'error');
  });
});

dlAudioBtn.addEventListener('click', () => {
  mainButtonsDiv.classList.add('hidden');
  audioFormDiv.classList.remove('hidden');
});

cancelAudioBtn.addEventListener('click', () => {
  audioFormDiv.classList.add('hidden');
  clearData();
  mainButtonsDiv.classList.remove('hidden');
});

submitAudioBtn.addEventListener('click', () => {
  const currentUrl = window.location.href;
  const audioData = {
    url: currentUrl,
    title: document.getElementById('audio-title').value || '',
    artist: document.getElementById('audio-artist').value || '',
    album: document.getElementById('audio-album').value || '',
    art_url: document.getElementById('audio-art').value || '',
  };

  showStatusMessage('Enviando audio...', 'success');

  fetch(`${flaskEndpoint}/download_audio`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(audioData),
  })
  .then(response => response.json())
  .then(data => {
    showStatusMessage(data.mensaje || '¡Audio enviado!', 'success');
    cancelAudioBtn.click();
    clearData();
  })
  .catch(error => {
    console.log(error);
    showStatusMessage('Error al conectar con servidor', 'error');
  });
});

console.log('--- Panel de Descarga Cargado (CSS Externo) ---');