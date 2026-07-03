import { useState, useEffect } from 'react'
import { apiService } from '../services/api'
import { formatNumber, formatPrice, formatDate } from '../utils/formatters'
import {
  CATEGORIES,
  CATEGORY_NAMES,
  CATEGORY_ICONS,
  ORDER_STATUS,
  ORDER_STATUS_NAMES,
  ORDER_STATUS_COLORS
} from '../utils/constants'
import Loading from '../components/Common/Loading'
import StatusBadge from '../components/Common/StatusBadge'
import {
  Package,
  ShoppingCart,
  Users,
  TrendingUp,
  Cctv,
  Video,
  Server,
  HardDrive,
  Database,
  Plug,
  LayoutDashboard,
  ChevronRight
} from 'lucide-react'

const CategoryIcon = ({ iconName, ...props }) => {
  const icons = {
    Cctv,
    Video,
    Server,
    HardDrive,
    Database,
    Plug
  }
  const Icon = icons[iconName] || Package
  return <Icon {...props} />
}

const Dashboard = () => {
  const [stats, setStats] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadDashboardStats()
  }, [])

  const loadDashboardStats = async () => {
    try {
      const data = await apiService.getDashboardStats()
      setStats(data)
    } catch (error) {
      console.error('Error loading dashboard stats:', error)
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <div className="flex justify-center items-center h-96">
        <Loading className="w-10 h-10 text-primary-600" />
      </div>
    )
  }

  if (!stats) {
    return <div className="text-center text-red-500 bg-red-50 p-4 rounded-lg">Ошибка загрузки данных</div>
  }

  return (
    <div className="space-y-8">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="p-2 bg-primary-50 dark:bg-primary-900/20 rounded-lg">
            <LayoutDashboard className="w-6 h-6 text-primary-600 dark:text-primary-400" />
          </div>
          <div>
            <h1 className="text-2xl font-bold text-slate-900 dark:text-slate-100">Дашборд</h1>
            <p className="mt-1 text-sm text-slate-500 dark:text-slate-400">Обзор ключевых показателей магазина</p>
          </div>
        </div>
      </div>

      {/* Статистика в карточках */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="bg-white dark:bg-slate-800 rounded-2xl shadow-sm border border-slate-100 dark:border-slate-700 p-6 transition-all hover:shadow-md">
          <div className="flex items-center">
            <div className="flex-shrink-0 bg-blue-50 dark:bg-blue-900/20 text-blue-600 dark:text-blue-400 rounded-xl p-3">
              <Package className="w-6 h-6" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-slate-500 dark:text-slate-400">Всего товаров</p>
              <div className="flex items-baseline gap-2">
                <p className="text-2xl font-bold text-slate-900 dark:text-slate-100">{stats.products.total}</p>
                <p className="text-xs font-medium text-emerald-600 bg-emerald-50 px-1.5 py-0.5 rounded-full">
                  {stats.products.active} активных
                </p>
              </div>
            </div>
          </div>
        </div>

        <div className="bg-white dark:bg-slate-800 rounded-2xl shadow-sm border border-slate-100 dark:border-slate-700 p-6 transition-all hover:shadow-md">
          <div className="flex items-center">
            <div className="flex-shrink-0 bg-violet-50 dark:bg-violet-900/20 text-violet-600 dark:text-violet-400 rounded-xl p-3">
              <ShoppingCart className="w-6 h-6" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-slate-500 dark:text-slate-400">Всего заказов</p>
              <div className="flex items-baseline gap-2">
                <p className="text-2xl font-bold text-slate-900 dark:text-slate-100">{stats.orders.total}</p>
                <p className="text-xs font-medium text-blue-600 bg-blue-50 px-1.5 py-0.5 rounded-full">
                  +{stats.orders.new} новых
                </p>
              </div>
            </div>
          </div>
        </div>

        <div className="bg-white dark:bg-slate-800 rounded-2xl shadow-sm border border-slate-100 dark:border-slate-700 p-6 transition-all hover:shadow-md">
          <div className="flex items-center">
            <div className="flex-shrink-0 bg-indigo-50 dark:bg-indigo-900/20 text-indigo-600 dark:text-indigo-400 rounded-xl p-3">
              <Users className="w-6 h-6" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-slate-500 dark:text-slate-400">Пользователей</p>
              <p className="text-2xl font-bold text-slate-900 dark:text-slate-100">{stats.users.total}</p>
            </div>
          </div>
        </div>

        <div className="bg-white dark:bg-slate-800 rounded-2xl shadow-sm border border-slate-100 dark:border-slate-700 p-6 transition-all hover:shadow-md">
          <div className="flex items-center">
            <div className="flex-shrink-0 bg-emerald-50 dark:bg-emerald-900/20 text-emerald-600 dark:text-emerald-400 rounded-xl p-3">
              <TrendingUp className="w-6 h-6" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-slate-500 dark:text-slate-400">За неделю</p>
              <div className="flex items-baseline gap-2">
                <p className="text-2xl font-bold text-slate-900 dark:text-slate-100">{stats.orders.this_week}</p>
                <p className="text-xs text-slate-400">заказов</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Статистика по категориям */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white dark:bg-slate-800 rounded-2xl shadow-sm border border-slate-100 dark:border-slate-700 p-6">
          <h3 className="text-lg font-bold text-slate-900 dark:text-slate-100 mb-6">Товары по категориям</h3>
          <div className="space-y-4">
            {Object.entries(CATEGORIES).map(([key, value]) => (
              <div key={key} className="flex justify-between items-center p-3 hover:bg-slate-50 dark:hover:bg-slate-700/50 rounded-xl transition-colors">
                <div className="flex items-center gap-3">
                  <span className="bg-slate-100 dark:bg-slate-700 w-10 h-10 flex items-center justify-center rounded-xl text-slate-600 dark:text-slate-300">
                    <CategoryIcon iconName={CATEGORY_ICONS[value]} className="w-5 h-5" />
                  </span>
                  <span className="text-sm font-medium text-slate-700 dark:text-slate-300">
                    {CATEGORY_NAMES[value]}
                  </span>
                </div>
                <span className="text-sm font-bold text-slate-900 dark:text-slate-100 bg-slate-100 dark:bg-slate-700 px-2.5 py-1 rounded-md">
                  {stats.products.by_category[value] || 0}
                </span>
              </div>
            ))}
          </div>
        </div>

        <div className="bg-white dark:bg-slate-800 rounded-2xl shadow-sm border border-slate-100 dark:border-slate-700 p-6">
          <h3 className="text-lg font-bold text-slate-900 dark:text-slate-100 mb-6">Статус заказов</h3>
          <div className="space-y-4">
            {Object.entries(ORDER_STATUS).map(([key, value]) => (
              <div key={key} className="flex justify-between items-center p-3 hover:bg-slate-50 dark:hover:bg-slate-700/50 rounded-xl transition-colors">
                <span className="text-sm font-medium text-slate-700 dark:text-slate-300">{ORDER_STATUS_NAMES[value]}</span>
                <span className={`px-2.5 py-1 text-xs font-semibold rounded-full ${ORDER_STATUS_COLORS[value]}`}>
                  {stats.orders[value] || 0}
                </span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Последние заказы */}
      <div className="bg-white dark:bg-slate-800 rounded-2xl shadow-sm border border-slate-100 dark:border-slate-700 overflow-hidden">
        <div className="px-6 py-5 border-b border-slate-100 dark:border-slate-700 flex justify-between items-center">
          <h3 className="text-lg font-bold text-slate-900 dark:text-slate-100">Последние заказы</h3>
          <button className="text-sm font-medium text-primary-600 hover:text-primary-700 flex items-center transition-colors">
            Все заказы
            <ChevronRight className="w-4 h-4 ml-1" />
          </button>
        </div>
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-slate-100 dark:divide-slate-700">
            <thead className="bg-slate-50/50 dark:bg-slate-900/50">
              <tr>
                <th scope="col" className="px-6 py-3 text-left text-xs font-semibold text-slate-500 uppercase tracking-wider">
                  Заказ
                </th>
                <th scope="col" className="px-6 py-3 text-left text-xs font-semibold text-slate-500 uppercase tracking-wider">
                  Клиент
                </th>
                <th scope="col" className="px-6 py-3 text-left text-xs font-semibold text-slate-500 uppercase tracking-wider">
                  Сумма
                </th>
                <th scope="col" className="px-6 py-3 text-left text-xs font-semibold text-slate-500 uppercase tracking-wider">
                  Статус
                </th>
                <th scope="col" className="px-6 py-3 text-left text-xs font-semibold text-slate-500 uppercase tracking-wider">
                  Дата
                </th>
              </tr>
            </thead>
            <tbody className="bg-white dark:bg-slate-800 divide-y divide-slate-100 dark:divide-slate-700">
              {stats.recent_orders.map((order) => (
                <tr key={order.id} className="hover:bg-slate-50 dark:hover:bg-slate-700/50 transition-colors">
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-slate-900 dark:text-slate-100">
                    #{order.id.substring(0, 8)}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-slate-500">
                    {order.user_name}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-slate-900 dark:text-slate-100">
                    {formatNumber(order.total_uzs)} сум
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <StatusBadge status={order.status} type="order" />
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-slate-500">
                    {formatDate(order.created_at)}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}

export default Dashboard
