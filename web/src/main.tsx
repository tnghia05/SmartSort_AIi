import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'

console.log('Main.tsx loading...');

const rootElement = document.getElementById('root');
console.log('Root element:', rootElement);

if (!rootElement) {
  console.error('Root element not found!');
  document.body.innerHTML = '<h1 style="padding: 20px; color: red;">ERROR: Root element not found!</h1>';
} else {
  // Dynamic import với error handling
  import('./App.tsx')
    .then((module) => {
      const App = module.default;
      console.log('App imported successfully');
      
      if (!App) {
        throw new Error('App component is not exported as default');
      }
      
      console.log('Attempting to render App...');
      createRoot(rootElement).render(
        <StrictMode>
          <App />
        </StrictMode>,
      );
      console.log('App rendered successfully');
    })
    .catch((error) => {
      console.error('Error importing or rendering App:', error);
      const errorMessage = error instanceof Error ? error.message : String(error);
      rootElement.innerHTML = `
        <div style="padding: 20px; color: red; background: #ffebee; border-radius: 8px;">
          <h1>ERROR: Failed to load App</h1>
          <p><strong>Error:</strong> ${errorMessage}</p>
          <p>Check console (F12) for more details.</p>
          <button 
            onclick="window.location.reload()" 
            style="padding: 10px 20px; background: #f44336; color: white; border: none; border-radius: 4px; cursor: pointer; margin-top: 10px;"
          >
            Reload Page
          </button>
        </div>
      `;
    });
}
