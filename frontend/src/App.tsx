import './App.css'
import Explorer from './pages/Explorer'

function App() {
  return (
    <>
      <a className="skip-link" href="#main-content">Saltar al contenido</a>
      <header className="topbar">
        <span className="brand-mark" aria-hidden="true">🌎</span>
        <strong>EarthPulse</strong>
        <span>Explorador de la Tierra</span>
      </header>
      <main className="page" id="main-content">
        <Explorer />
      </main>
    </>
  )
}

export default App
