import './App.css'
import Explorer from './pages/Explorer'

function App() {
  return (
    <>
      <header className="topbar">
        <strong>TrendScope</strong>
        <span>Explorador</span>
      </header>
      <main className="page">
        <Explorer />
      </main>
    </>
  )
}

export default App