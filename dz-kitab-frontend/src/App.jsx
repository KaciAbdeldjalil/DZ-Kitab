import { useState } from 'react'
import { Landingpage } from './pages/landing-page'
import './App.css'

function App() {
  const [count, setCount] = useState(0)

  return (
    <>
      <Landingpage></Landingpage>
    </>
  )
}

export default App
