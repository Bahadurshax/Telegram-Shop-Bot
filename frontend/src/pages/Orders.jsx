import React, { useState, useEffect } from 'react'
import { apiService } from '../services/api'

const Orders = () => {
  const [orders, setOrders] = useState([])
  const [loading, setLoading] = useState(true)
  const [currentPage, setCurrentPage] = useState(0)
  const [totalCount, setTotalCount] = useState(0)
  const [selectedStatus, setSelectedStatus] = useState('')
  const [selectedOrder, setSelectedOrder] = useState(null)

  const itemsPerPage = 10

  useEffect(() => {
    loadOrders()
    loadOrdersCount()
  }, [currentPage, selectedStatus])

  const loadOrders = async () => {
    setLoading(true)
    try {
      const params = {
        skip: currentPage * itemsPerPage,
        limit: itemsPerPage,
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
    console.log(orderId, newStatus);
    
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

  const formatPrice = (price) => {
    return new Intl.NumberFormat('ru-RU').format(price)
  }

  const getStatusColor = (status) => {
    switch (status) {
      case 'new': return 'bg-blue-100 text-blue-800'
      case 'processing': return 'bg-yellow-100 text-yellow-800'
      case 'completed': return 'bg-green-100 text-green-800'
      case 'cancelled': return 'bg-red-100 text-red-800'
      default: return 'bg-gray-100 text-gray-800'
    }
  }

  const getStatusText = (status) => {
    switch (status) {
      case 'new': return 'Новый'
      case 'processing': return 'В обработке'
      case 'completed': return 'Выполнен'
      case 'cancelled': return 'Отменен'
      default: return status
    }
  }

  const totalPages = Math.ceil(totalCount / itemsPerPage)

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold text-gray-900">Заказы</h1>
        <div className="text-sm text-gray-500">
          Всего заказов: {totalCount}
        </div>
      </div>

      {/* Фильтр по статусу */}
      <div className="bg-white rounded-lg shadow p-4">
        <div className="flex items-center space-x-4">
          <label className="text-sm font-medium text-gray-700">Фильтр по статусу:</label>
          <select
            value={selectedStatus}
            onChange={(e) => {
              setSelectedStatus(e.target.value)
              setCurrentPage(0)
            }}
            className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500"
          >
            <option value="">Все заказы</option>
            <option value="new">Новые</option>
            <option value="processing">В обработке</option>
            <option value="completed">Выполненные</option>
            <option value="cancelled">Отмененные</option>
          </select>
        </div>
      </div>

      {/* Таблица заказов */}
      <div className="bg-white rounded-lg shadow overflow-hidden">
        {loading ? (
          <div className="flex items-center justify-center h-64">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
          </div>
        ) : (
          <>
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Заказ
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Клиент
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Телефон
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Сумма
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Статус
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Дата
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Действия
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {orders.map((order) => (
                    <tr key={order._id}>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm font-medium text-gray-900">
                          #{order._id}
                        </div>
                        <div className="text-sm text-gray-500">
                          {order.items.length} товар(ов)
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm font-medium text-gray-900">{order.user_name}</div>
                        <div className="text-sm text-gray-500">
                          {order.user_address || 'Самовывоз'}
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {order.user_phone}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm font-medium text-gray-900">
                          {formatPrice(order.total_amount_uzs)} сум
                        </div>
                        <div className="text-sm text-gray-500">
                          {order.total_amount_usd.toFixed(0)} $
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${getStatusColor(order.status)}`}>
                          {getStatusText(order.status)}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {new Date(order.created_at).toLocaleDateString('ru-RU', {
                          day: '2-digit',
                          month: '2-digit',
                          year: 'numeric',
                          hour: '2-digit',
                          minute: '2-digit'
                        })}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium space-x-2">
                        <button
                          onClick={() => setSelectedOrder(order)}
                          className="text-blue-600 hover:text-blue-900"
                        >
                          Подробнее
                        </button>
                        {order.status === 'new' && (
                          <button
                            onClick={() => handleStatusChange(order._id, 'processing')}
                            className="text-green-600 hover:text-green-900"
                          >
                            В работу
                          </button>
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            {/* Пагинация */}
            {totalPages > 1 && (
              <div className="bg-white px-4 py-3 flex items-center justify-between border-t border-gray-200">
                <div className="flex-1 flex justify-between sm:hidden">
                  <button
                    onClick={() => setCurrentPage(Math.max(0, currentPage - 1))}
                    disabled={currentPage === 0}
                    className="relative inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 disabled:opacity-50"
                  >
                    Предыдущая
                  </button>
                  <button
                    onClick={() => setCurrentPage(Math.min(totalPages - 1, currentPage + 1))}
                    disabled={currentPage >= totalPages - 1}
                    className="ml-3 relative inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 disabled:opacity-50"
                  >
                    Следующая
                  </button>
                </div>
                <div className="hidden sm:flex-1 sm:flex sm:items-center sm:justify-between">
                  <div>
                    <p className="text-sm text-gray-700">
                      Показано <span className="font-medium">{currentPage * itemsPerPage + 1}</span> до{' '}
                      <span className="font-medium">
                        {Math.min((currentPage + 1) * itemsPerPage, totalCount)}
                      </span>{' '}
                      из <span className="font-medium">{totalCount}</span> заказов
                    </p>
                  </div>
                  <div>
                    <nav className="relative z-0 inline-flex rounded-md shadow-sm -space-x-px">
                      <button
                        onClick={() => setCurrentPage(Math.max(0, currentPage - 1))}
                        disabled={currentPage === 0}
                        className="relative inline-flex items-center px-2 py-2 rounded-l-md border border-gray-300 bg-white text-sm font-medium text-gray-500 hover:bg-gray-50 disabled:opacity-50"
                      >
                        ‹
                      </button>
                      {Array.from({ length: Math.min(5, totalPages) }, (_, i) => {
                        const pageNum = currentPage < 3 ? i : currentPage - 2 + i
                        if (pageNum >= totalPages) return null
                        return (
                          <button
                            key={pageNum}
                            onClick={() => setCurrentPage(pageNum)}
                            className={`relative inline-flex items-center px-4 py-2 border text-sm font-medium ${
                              pageNum === currentPage
                                ? 'z-10 bg-blue-50 border-blue-500 text-blue-600'
                                : 'bg-white border-gray-300 text-gray-500 hover:bg-gray-50'
                            }`}
                          >
                            {pageNum + 1}
                          </button>
                        )
                      })}
                      <button
                        onClick={() => setCurrentPage(Math.min(totalPages - 1, currentPage + 1))}
                        disabled={currentPage >= totalPages - 1}
                        className="relative inline-flex items-center px-2 py-2 rounded-r-md border border-gray-300 bg-white text-sm font-medium text-gray-500 hover:bg-gray-50 disabled:opacity-50"
                      >
                        ›
                      </button>
                    </nav>
                  </div>
                </div>
              </div>
            )}
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

// Модальное окно с деталями заказа
const OrderDetailsModal = ({ order, onClose, onStatusChange }) => {
  const formatPrice = (price) => {
    return new Intl.NumberFormat('ru-RU').format(price)
  }

  const getStatusColor = (status) => {
    switch (status) {
      case 'new': return 'bg-blue-100 text-blue-800'
      case 'processing': return 'bg-yellow-100 text-yellow-800'
      case 'completed': return 'bg-green-100 text-green-800'
      case 'cancelled': return 'bg-red-100 text-red-800'
      default: return 'bg-gray-100 text-gray-800'
    }
  }

  const getStatusText = (status) => {
    switch (status) {
      case 'new': return 'Новый'
      case 'processing': return 'В обработке'
      case 'completed': return 'Выполнен'
      case 'cancelled': return 'Отменен'
      default: return status
    }
  }

  return (
    <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
      <div className="relative top-10 mx-auto p-5 border w-11/12 md:w-4/5 lg:w-3/5 shadow-lg rounded-md bg-white">
        <div className="mt-3">
          <div className="flex justify-between items-center mb-6">
            <h3 className="text-xl font-medium text-gray-900">
              Заказ #{order._id}
            </h3>
            <button
              onClick={onClose}
              className="text-gray-400 hover:text-gray-600 text-2xl"
            >
              ×
            </button>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Информация о клиенте */}
            <div className="bg-gray-50 rounded-lg p-4">
              <h4 className="text-lg font-medium text-gray-900 mb-3">Информация о клиенте</h4>
              <div className="space-y-2">
                <div>
                  <span className="text-sm font-medium text-gray-500">Имя:</span>
                  <span className="ml-2 text-sm text-gray-900">{order.user_name}</span>
                </div>
                <div>
                  <span className="text-sm font-medium text-gray-500">Телефон:</span>
                  <span className="ml-2 text-sm text-gray-900">{order.user_phone}</span>
                </div>
                <div>
                  <span className="text-sm font-medium text-gray-500">Адрес:</span>
                  <span className="ml-2 text-sm text-gray-900">{order.user_address || 'Самовывоз'}</span>
                </div>
                <div>
                  <span className="text-sm font-medium text-gray-500">Дата заказа:</span>
                  <span className="ml-2 text-sm text-gray-900">
                    {new Date(order.created_at).toLocaleDateString('ru-RU', {
                      day: '2-digit',
                      month: '2-digit',
                      year: 'numeric',
                      hour: '2-digit',
                      minute: '2-digit'
                    })}
                  </span>
                </div>
              </div>
            </div>

            {/* Статус и управление */}
            <div className="bg-gray-50 rounded-lg p-4">
              <h4 className="text-lg font-medium text-gray-900 mb-3">Статус заказа</h4>
              <div className="space-y-3">
                <div>
                  <span className={`px-3 py-1 inline-flex text-sm leading-5 font-semibold rounded-full ${getStatusColor(order.status)}`}>
                    {getStatusText(order.status)}
                  </span>
                </div>
                <div className="space-y-2">
                  {order.status === 'new' && (
                    <button
                      onClick={() => onStatusChange(order._id, 'processing')}
                      className="w-full bg-yellow-600 text-white px-4 py-2 rounded-md hover:bg-yellow-700 text-sm"
                    >
                      Взять в обработку
                    </button>
                  )}
                  {order.status === 'processing' && (
                    <>
                      <button
                        onClick={() => onStatusChange(order._id, 'completed')}
                        className="w-full bg-green-600 text-white px-4 py-2 rounded-md hover:bg-green-700 text-sm"
                      >
                        Завершить заказ
                      </button>
                      <button
                        onClick={() => onStatusChange(order._id, 'cancelled')}
                        className="w-full bg-red-600 text-white px-4 py-2 rounded-md hover:bg-red-700 text-sm"
                      >
                        Отменить заказ
                      </button>
                    </>
                  )}
                </div>
              </div>
            </div>
          </div>

          {/* Товары в заказе */}
          <div className="mt-6">
            <h4 className="text-lg font-medium text-gray-900 mb-3">Товары в заказе</h4>
            <div className="bg-white border rounded-lg overflow-hidden">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Товар
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Количество
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Цена за шт.
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Сумма
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {order.items.map((item, index) => (
                    <tr key={index}>
                      <td className="px-6 py-4">
                        <div className="text-sm font-medium text-gray-900">{item.product_name}</div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {item.quantity} шт.
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm text-gray-900">{formatPrice(item.price_uzs)} сум</div>
                        <div className="text-sm text-gray-500">{item.price_usd} $</div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm font-medium text-gray-900">
                          {formatPrice(item.price_uzs * item.quantity)} сум
                        </div>
                        <div className="text-sm text-gray-500">
                          {(item.price_usd * item.quantity).toFixed(0)} $
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
                <tfoot className="bg-gray-50">
                  <tr>
                    <td colSpan="3" className="px-6 py-4 text-right text-sm font-medium text-gray-900">
                      Итого:
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm font-bold text-gray-900">
                        {formatPrice(order.total_amount_uzs)} сум
                      </div>
                      <div className="text-sm font-bold text-gray-500">
                        {order.total_amount_usd.toFixed(0)} $
                      </div>
                    </td>
                  </tr>
                </tfoot>
              </table>
            </div>
          </div>

          {/* Отчет консультации */}
          {order.consultation_report && (
            <div className="mt-6">
              <h4 className="text-lg font-medium text-gray-900 mb-3">Отчет AI-консультанта</h4>
              <div className="bg-blue-50 rounded-lg p-4">
                <pre className="text-sm text-gray-700 whitespace-pre-wrap">{order.consultation_report}</pre>
              </div>
            </div>
          )}

          <div className="mt-6 flex justify-end">
            <button
              onClick={onClose}
              className="bg-gray-300 text-gray-700 px-6 py-2 rounded-md hover:bg-gray-400"
            >
              Закрыть
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}

export default Orders