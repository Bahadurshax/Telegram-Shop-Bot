import { useState } from 'react'
import { Link, useLocation } from 'react-router-dom'
import { useTheme } from '../../context/ThemeContext'
import ThemeToggle from '../Common/ThemeToggle'
import {
  LayoutDashboard,
  Package,
  ShoppingCart,
  Upload,
  LogOut,
  Menu
} from 'lucide-react'

const Layout = ({ children, onLogout }) => {
  const [sidebarOpen, setSidebarOpen] = useState(false)
  const { theme } = useTheme()
  const location = useLocation()

  const navigation = [
    {
      name: 'Дашборд',
      href: '/dashboard',
      icon: <LayoutDashboard className="w-5 h-5" />
    },
    {
      name: 'Товары',
      href: '/products',
      icon: <Package className="w-5 h-5" />
    },
    {
      name: 'Заказы',
      href: '/orders',
      icon: <ShoppingCart className="w-5 h-5" />
    },
    {
      name: 'Загрузка прайса',
      href: '/upload',
      icon: <Upload className="w-5 h-5" />
    },
  ]

  const isCurrentPage = (href) => location.pathname === href

  return (
    <div className="h-screen bg-slate-50 dark:bg-slate-900 flex font-sans overflow-hidden transition-colors duration-300">
      {/* Mobile sidebar backdrop */}
      {sidebarOpen && (
        <div
          className="fixed inset-0 z-40 bg-slate-900/50 backdrop-blur-sm md:hidden"
          onClick={() => setSidebarOpen(false)}
        ></div>
      )}

      <div className={`
        fixed inset-y-0 left-0 z-50 w-64 bg-white dark:bg-slate-800 border-r border-slate-200 dark:border-slate-700 transform transition-transform duration-300 ease-in-out
        ${sidebarOpen ? 'translate-x-0' : '-translate-x-full'}
        md:translate-x-0 md:static md:inset-auto md:h-full
      `}>
        <div className="flex flex-col h-full">
          <div className="flex items-center h-16 px-6 border-b border-slate-100 dark:border-slate-700">
            <span className="text-xl font-bold text-primary-600 dark:text-primary-400">
              Telegram Shop
            </span>
          </div>

          <nav className="flex-1 px-4 py-6 space-y-1">
            {navigation.map((item) => (
              <Link
                key={item.name}
                to={item.href}
                className={`
                  flex items-center px-4 py-3 text-sm font-medium rounded-xl transition-all duration-200 group
                  ${isCurrentPage(item.href)
                    ? 'bg-primary-50 dark:bg-primary-900/20 text-primary-700 dark:text-primary-400 shadow-sm'
                    : 'text-slate-600 dark:text-slate-400 hover:bg-slate-50 dark:hover:bg-slate-700/50 hover:text-slate-900 dark:hover:text-slate-100'
                  }
                `}
              >
                <div className={`mr-3 transition-colors ${isCurrentPage(item.href) ? 'text-primary-500' : 'text-slate-400 dark:text-slate-500 group-hover:text-slate-600 dark:group-hover:text-slate-300'}`}>
                  {item.icon}
                </div>
                {item.name}
              </Link>
            ))}
          </nav>

          <div className="p-4 border-t border-slate-100 dark:border-slate-700 space-y-2">
            <ThemeToggle />

            <button
              onClick={onLogout}
              className="flex items-center w-full px-4 py-2 text-sm font-medium text-slate-600 dark:text-slate-400 rounded-lg hover:bg-red-50 dark:hover:bg-red-900/10 hover:text-red-600 dark:hover:text-red-400 transition-colors"
            >
              <LogOut className="w-5 h-5 mr-3" />
              Выйти
            </button>
          </div>
        </div>
      </div>

      {/* Main content */}
      <div className="flex-1 flex flex-col min-w-0 overflow-hidden">
        <header className="bg-white dark:bg-slate-800 border-b border-slate-200 dark:border-slate-700 lg:hidden">
          <div className="flex items-center justify-between px-4 py-3">
            <button
              onClick={() => setSidebarOpen(true)}
              className="p-2 -ml-2 text-slate-500 dark:text-slate-400 rounded-lg hover:bg-slate-100 dark:hover:bg-slate-700 focus:outline-none focus:ring-2 focus:ring-inset focus:ring-primary-500"
            >
              <Menu className="w-6 h-6" />
            </button>
            <span className="text-lg font-bold text-slate-900 dark:text-slate-100">Telegram Shop</span>
            <ThemeToggle showLabel={false} className="p-2 -mr-2" />
          </div>
        </header>

        <main className="flex-1 overflow-y-auto p-4 md:p-8">
          <div className="max-w-7xl mx-auto">
            {children}
          </div>
        </main>
      </div>
    </div>
  )
}

export default Layout