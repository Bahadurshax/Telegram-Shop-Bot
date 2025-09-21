import React, { useState } from 'react'
import { Link, useLocation } from 'react-router-dom'

const Layout = ({ children, onLogout }) => {
  const [sidebarOpen, setSidebarOpen] = useState(false)
  const location = useLocation()

  const navigation = [
    { name: 'Дашборд', href: '/dashboard', icon: '📊' },
    { name: 'Товары', href: '/products', icon: '📦' },
    { name: 'Заказы', href: '/orders', icon: '🛒' },
  ]

  const isCurrentPage = (href) => location.pathname === href

  return (
    <div className="min-h-screen bg-gray-100 flex">
      {/* Sidebar */}
      <div className={`${sidebarOpen ? 'block' : 'hidden'} fixed inset-0 z-40 md:hidden`}>
        <div className="fixed inset-0 bg-gray-600 opacity-75" onClick={() => setSidebarOpen(false)}></div>
      </div>

      <div className={`${sidebarOpen ? 'translate-x-0' : '-translate-x-full'} fixed z-40 inset-y-0 left-0 w-64 transition duration-300 transform bg-white border-r border-gray-200 md:translate-x-0 md:static md:inset-0`}>
        <div className="flex flex-col h-full">
          <div className="flex items-center justify-center h-16 px-4 bg-blue-600 text-white">
            <h1 className="text-xl font-bold">Telegram Shop</h1>
          </div>
          
          <nav className="flex-1 px-4 py-4 space-y-2">
            {navigation.map((item) => (
              <Link
                key={item.name}
                to={item.href}
                className={`flex items-center px-4 py-2 text-sm font-medium rounded-md transition-colors ${
                  isCurrentPage(item.href)
                    ? 'bg-blue-100 text-blue-700'
                    : 'text-gray-700 hover:bg-gray-100'
                }`}
              >
                <span className="mr-3">{item.icon}</span>
                {item.name}
              </Link>
            ))}
          </nav>
          
          <div className="px-4 py-4 border-t border-gray-200">
            <button
              onClick={onLogout}
              className="flex items-center w-full px-4 py-2 text-sm font-medium text-red-700 rounded-md hover:bg-red-50"
            >
              <span className="mr-3">🚪</span>
              Выйти
            </button>
          </div>
        </div>
      </div>

      {/* Main content */}
      <div className="flex-1 flex flex-col overflow-hidden">
        <header className="bg-white shadow-sm border-b border-gray-200">
          <div className="flex items-center justify-between px-4 py-4">
            <button
              onClick={() => setSidebarOpen(true)}
              className="md:hidden p-2 rounded-md text-gray-500 hover:text-gray-600 hover:bg-gray-100"
            >
              <span className="text-xl">☰</span>
            </button>
            <h2 className="text-lg font-semibold text-gray-900">
              Панель управления
            </h2>
            <div className="text-sm text-gray-500">
              Добро пожаловать, Администратор
            </div>
          </div>
        </header>

        <main className="flex-1 overflow-y-auto p-6">
          {children}
        </main>
      </div>
    </div>
  )
}

export default Layout