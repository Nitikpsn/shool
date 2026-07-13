import { BrowserRouter, Routes, Route } from 'react-router-dom'
import Layout from './components/Layout'
import Home from './pages/Home'
import Compare from './pages/Compare'
import Reports from './pages/Reports'
import { Link } from 'react-router-dom'
import { Home as HomeIcon } from 'lucide-react'

function NotFound() {
  return (
    <div className="max-w-md mx-auto py-20 text-center">
      <div className="w-12 h-12 rounded-xl bg-neutral-100 dark:bg-neutral-800 flex items-center justify-center mx-auto mb-3">
        <HomeIcon className="w-5 h-5 text-neutral-400" />
      </div>
      <h2 className="text-base font-semibold text-neutral-800 dark:text-neutral-200 mb-1">Not found</h2>
      <p className="text-sm text-neutral-500 mb-4">This page does not exist.</p>
      <Link to="/" className="btn-primary"><HomeIcon className="w-4 h-4" /> Home</Link>
    </div>
  )
}

export default function App() {
  return (
    <BrowserRouter>
      <Layout>
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/compare/:sessionId" element={<Compare />} />
          <Route path="/reports/:sessionId" element={<Reports />} />
          <Route path="*" element={<NotFound />} />
        </Routes>
      </Layout>
    </BrowserRouter>
  )
}
