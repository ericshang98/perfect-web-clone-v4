import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App.jsx'
import './index.css'
import { initAnimations } from './animations.js'

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
)

// Boot the scroll-animation engine after the DOM is mounted & painted.
requestAnimationFrame(() => requestAnimationFrame(() => initAnimations()))
