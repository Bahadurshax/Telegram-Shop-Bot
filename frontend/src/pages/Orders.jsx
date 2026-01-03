import { useState, useEffect } from 'react'
import { apiService } from '../services/api'
import { formatPrice, formatDateTime } from '../utils/formatters'
import { getOrderStatusText } from '../utils/statusUtils'
import { ORDER_STATUS, ORDER_STATUS_NAMES, PAGINATION } from '../utils/constants'
import Loading from '../components/Common/Loading'
import StatusBadge from '../components/Common/StatusBadge'
import Pagination from '../components/Common/Pagination'
import OrderDetailsModal from '../components/Orders/OrderDetailsModal'

const Orders = () => {
  const [orders, setOrders] = useState([])
  const [loading, setLoading] = useState(true)
  const [currentPage, setCurrentPage] = useState(0)
  const [totalCount, setTotalCount] = useState(0)
  const [selectedStatus, setSelectedStatus] = useState('')
  const [selectedOrder, setSelectedOrder] = useState(null)

  useEffect(() => {
    loadOrders()
    loadOrdersCount()
  }, [currentPage, selectedStatus])

  const loadOrders = async () => {
    setLoading(true)
    try {
      const params = {
        skip: currentPage * PAGINATION.ITEMS_PER_PAGE,
        limit: PAGINATION.ITEMS_PER_PAGE,
        ...(selectedStatus && { status: selectedStatus })
      }
      const data = await apiService.getOrders(params)
      setOrders(data)
    } catch (error) {
      console.error('Error loading orders:', error)
    } finally {
      setLoading(false)
    }
  }

  const loadOrdersCount = async () => {
    try {
      const params = {
        ...(selectedStatus && { status: selectedStatus })
      }
      const data = await apiService.getOrdersCount(params)
      setTotalCount(data.count)
    } catch (error) {
      console.error('Error loading orders count:', error)
    }
  }

  const handleStatusChange = async (orderId, newStatus) => {
    try {
      await apiService.updateOrderStatus(orderId, newStatus)
      loadOrders()
      if (selectedOrder && selectedOrder._id === orderId) {
        const updatedOrder = await apiService.getOrder(orderId)
        setSelectedOrder(updatedOrder)
      }
    } catch (error) {
      console.error('Error updating order status:', error)
      alert('Ошибка при обновлении статуса заказа')
    }
  }

  return (
    <div className="space-y-8">
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 dark:text-slate-100">Заказы</h1>
          <p className="mt-1 text-sm text-slate-500 dark:text-slate-400">
            Управление и отслеживание заказов
          </p>
        </div>
        <div className="bg-white dark:bg-slate-800 px-4 py-2 rounded-lg border border-slate-200 dark:border-slate-700 shadow-sm text-sm font-medium text-slate-600 dark:text-slate-400 transition-colors">
          Всего заказов: <span className="text-slate-900 dark:text-slate-100 font-bold">{totalCount}</span>
        </div>
      </div>

      {/* Фильтр по статусу */}
      <div className="bg-white dark:bg-slate-800 rounded-xl shadow-sm border border-slate-200 dark:border-slate-700 p-5 transition-colors">
        <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">Фильтр по статусу</label>
        <div className="max-w-xs">
          <select
            value={selectedStatus}
            onChange={(e) => {
              setSelectedStatus(e.target.value)
              setCurrentPage(0)
            }}
            className="block w-full pl-3 pr-10 py-2.5 text-base border border-slate-300 dark:border-slate-600 focus:outline-none focus:ring-primary-500 focus:border-primary-500 sm:text-sm rounded-lg bg-white dark:bg-slate-800 text-slate-900 dark:text-slate-100 transition-colors"
          >
            <option value="">Все заказы</option>
            {Object.entries(ORDER_STATUS_NAMES).map(([key, value]) => (
              <option key={key} value={key}>{value}</option>
            ))}
          </select>
        </div>
      </div>

      {/* Таблица заказов */}
      <div className="bg-white dark:bg-slate-800 rounded-xl shadow-sm border border-slate-200 dark:border-slate-700 overflow-hidden transition-colors">
        {loading ? (
          <div className="flex justify-center items-center h-64">
            <Loading className="w-8 h-8 text-primary-600" />
          </div>
        ) : (
          <>
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-slate-200 dark:divide-slate-700">
                <thead className="bg-slate-50 dark:bg-slate-900/50">
                  <tr>
                    <th scope="col" className="px-6 py-4 text-left text-xs font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wider">
                      Заказ
                    </th>
                    <th scope="col" className="px-6 py-4 text-left text-xs font-semibold text-slate-500 uppercase tracking-wider">
                      Клиент
                    </th>
                    <th scope="col" className="px-6 py-4 text-left text-xs font-semibold text-slate-500 uppercase tracking-wider">
                      Телефон
                    </th>
                    <th scope="col" className="px-6 py-4 text-left text-xs font-semibold text-slate-500 uppercase tracking-wider">
                      Сумма
                    </th>
                    <th scope="col" className="px-6 py-4 text-left text-xs font-semibold text-slate-500 uppercase tracking-wider">
                      Статус
                    </th>
                    <th scope="col" className="px-6 py-4 text-left text-xs font-semibold text-slate-500 uppercase tracking-wider">
                      Дата
                    </th>
                    <th scope="col" className="relative px-6 py-4">
                      <span className="sr-only">Действия</span>
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white dark:bg-slate-800 divide-y divide-slate-200 dark:divide-slate-700">
                  {orders.map((order) => (
                    <tr key={order._id} className="hover:bg-slate-50 dark:hover:bg-slate-700/50 transition-colors">
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm font-medium text-slate-900 dark:text-slate-100">
                          #{order._id}
                        </div>
                        <div className="text-xs text-slate-500 dark:text-slate-400 mt-0.5">
                          {order.items.length} товар(ов)
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm font-medium text-slate-900 dark:text-slate-100">{order.user_name}</div>
                        <div className="text-sm text-slate-500 dark:text-slate-400 truncate max-w-xs">
                          {order.user_address || 'Самовывоз'}
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-slate-600 dark:text-slate-400">
                        {order.user_phone}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm font-medium text-slate-900 dark:text-slate-100">
                          {formatPrice(order.total_amount_uzs)} сум
                        </div>
                        <div className="text-xs text-slate-500 dark:text-slate-400">
                          {order.total_amount_usd.toFixed(0)} $
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <StatusBadge status={order.status} type="order" />
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-slate-500 dark:text-slate-400">
                        {formatDateTime(order.created_at)}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                        <div className="flex items-center justify-end space-x-3">
                          <button
                            onClick={() => setSelectedOrder(order)}
                            className="text-primary-600 dark:text-primary-400 hover:text-primary-900 dark:hover:text-primary-300 hover:underline"
                          >
                            Подробнее
                          </button>
                          {order.status === ORDER_STATUS.NEW && (
                            <button
                              onClick={() => handleStatusChange(order._id, ORDER_STATUS.PROCESSING)}
                              className="text-emerald-600 dark:text-emerald-400 hover:text-emerald-900 dark:hover:text-emerald-300 bg-emerald-50 dark:bg-emerald-900/20 px-2 py-1 rounded hover:bg-emerald-100 dark:hover:bg-emerald-900/30 transition-colors"
                            >
                              В работу
                            </button>
                          )}
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            <div className="border-t border-slate-200 dark:border-slate-700 px-6 py-4">
              <Pagination
                currentPage={currentPage}
                totalCount={totalCount}
                itemsPerPage={PAGINATION.ITEMS_PER_PAGE}
                onPageChange={setCurrentPage}
                itemName="заказов"
              />
            </div>
          </>
        )}
      </div>

      {/* Модальное окно с деталями заказа */}
      {selectedOrder && (
        <OrderDetailsModal
          order={selectedOrder}
          onClose={() => setSelectedOrder(null)}
          onStatusChange={handleStatusChange}
        />
      )}
    </div>
  )
}

export default Orders