import { useState, useEffect } from 'react'
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import Layout from './components/Layout/Layout'
import Login from './pages/Login'
import Dashboard from './pages/Dashboard'
import Products from './pages/Products'
import Orders from './pages/Orders'
import UploadPricelist from './pages/UploadPriceList'
import { apiService } from './services/api'
import { API_CONFIG } from './utils/constants'
import Loading from './components/Common/Loading'
import './App.css'

function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(false)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    checkAuthStatus()
  }, [])

  const checkAuthStatus = async () => {
    const token = localStorage.getItem(API_CONFIG.TOKEN_KEY)
    if (token) {
      try {
        await apiService.getCurrentUser()
        setIsAuthenticated(true)
      } catch (error) {
        localStorage.removeItem(API_CONFIG.TOKEN_KEY)
        setIsAuthenticated(false)
      }
    }
    setLoading(false)
  }

  const handleLogin = (token) => {
    localStorage.setItem(API_CONFIG.TOKEN_KEY, token)
    setIsAuthenticated(true)
  }

  const handleLogout = () => {
    localStorage.removeItem(API_CONFIG.TOKEN_KEY)
    setIsAuthenticated(false)
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <Loading size="large" />
      </div>
    )
  }

  return (
    <Router>
      <div className="min-h-screen bg-slate-50 dark:bg-slate-900 transition-colors duration-300">
        {!isAuthenticated ? (
          <Login onLogin={handleLogin} />
        ) : (
          <Layout onLogout={handleLogout}>
            <Routes>
              <Route path="/" element={<Navigate to="/dashboard" />} />
              <Route path="/dashboard" element={<Dashboard />} />
              <Route path="/products" element={<Products />} />
              <Route path="/orders" element={<Orders />} />
              <Route path="/upload" element={<UploadPricelist />} />
            </Routes>
          </Layout>
        )}
      </div>
    </Router>
  )
}

export default App