import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import './styles/landing.css'
import './styles/app-shell.css'
import './styles/chat.css'
import './styles/client-picker.css'
import './styles/results.css'
import './styles/intake.css'
import './styles/client-detail.css'
import './styles/site-nav.css'
import './styles/about.css'
import App from './App.jsx'

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <App />
  </StrictMode>,
)