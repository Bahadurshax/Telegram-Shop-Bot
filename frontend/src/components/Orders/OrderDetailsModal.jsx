import { formatPrice, formatDateTime } from '../../utils/formatters'
import { getOrderStatusColor, getOrderStatusText } from '../../utils/statusUtils'
import { ORDER_STATUS } from '../../utils/constants'
import Modal from '../Common/Modal'

const OrderDetailsModal = ({ order, onClose, onStatusChange }) => {
    return (
        <Modal
            isOpen={true}
            onClose={onClose}
            title={`Заказ #${order._id}`}
            size="lg"
        >
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {/* Информация о клиенте */}
                <div className="bg-slate-50 dark:bg-slate-900/50 rounded-xl p-5 border border-slate-100 dark:border-slate-700 transition-colors">
                    <h4 className="text-sm font-semibold text-slate-900 dark:text-slate-100 uppercase tracking-wider mb-4">Информация о клиенте</h4>
                    <div className="space-y-3">
                        <div className="flex justify-between">
                            <span className="text-sm text-slate-500 dark:text-slate-400">Имя:</span>
                            <span className="text-sm font-medium text-slate-900 dark:text-slate-100 text-right">{order.user_name}</span>
                        </div>
                        <div className="flex justify-between">
                            <span className="text-sm text-slate-500 dark:text-slate-400">Телефон:</span>
                            <span className="text-sm font-medium text-slate-900 dark:text-slate-100 text-right">{order.user_phone}</span>
                        </div>
                        <div className="flex justify-between">
                            <span className="text-sm text-slate-500 dark:text-slate-400">Адрес:</span>
                            <span className="text-sm font-medium text-slate-900 dark:text-slate-100 text-right truncate max-w-[200px]">{order.user_address || 'Самовывоз'}</span>
                        </div>
                        <div className="flex justify-between">
                            <span className="text-sm text-slate-500 dark:text-slate-400">Дата заказа:</span>
                            <span className="text-sm font-medium text-slate-900 dark:text-slate-100 text-right">
                                {formatDateTime(order.created_at)}
                            </span>
                        </div>
                    </div>
                </div>

                {/* Статус и управление */}
                <div className="bg-slate-50 dark:bg-slate-900/50 rounded-xl p-5 border border-slate-100 dark:border-slate-700 transition-colors">
                    <h4 className="text-sm font-semibold text-slate-900 dark:text-slate-100 uppercase tracking-wider mb-4">Статус заказа</h4>
                    <div className="space-y-4">
                        <div className="flex items-center justify-between">
                            <span className="text-sm text-slate-500 dark:text-slate-400">Текущий статус:</span>
                            <span className={`px-3 py-1 inline-flex text-xs font-semibold rounded-full dark:ring-1 dark:ring-inset ${getOrderStatusColor(order.status)}`}>
                                {getOrderStatusText(order.status)}
                            </span>
                        </div>
                        <div className="pt-2 space-y-2">
                            {order.status === ORDER_STATUS.NEW && (
                                <button
                                    onClick={() => onStatusChange(order._id, ORDER_STATUS.PROCESSING)}
                                    className="w-full bg-emerald-600 text-white px-4 py-2 rounded-lg hover:bg-emerald-700 text-sm font-medium transition-colors shadow-sm"
                                >
                                    Взять в обработку
                                </button>
                            )}
                            {order.status === ORDER_STATUS.PROCESSING && (
                                <>
                                    <button
                                        onClick={() => onStatusChange(order._id, ORDER_STATUS.COMPLETED)}
                                        className="w-full bg-primary-600 text-white px-4 py-2 rounded-lg hover:bg-primary-700 text-sm font-medium transition-colors shadow-sm"
                                    >
                                        Завершить заказ
                                    </button>
                                    <button
                                        onClick={() => onStatusChange(order._id, ORDER_STATUS.CANCELLED)}
                                        className="w-full bg-white dark:bg-slate-800 text-red-600 dark:text-red-400 border border-red-200 dark:border-red-900/30 px-4 py-2 rounded-lg hover:bg-red-50 dark:hover:bg-red-900/20 text-sm font-medium transition-colors"
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
            <div className="mt-8">
                <h4 className="text-sm font-semibold text-slate-900 dark:text-slate-100 uppercase tracking-wider mb-4">Товары в заказе</h4>
                <div className="bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-xl overflow-hidden shadow-sm transition-colors">
                    <table className="min-w-full divide-y divide-slate-200 dark:divide-slate-700">
                        <thead className="bg-slate-50 dark:bg-slate-900/50">
                            <tr>
                                <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-slate-500 dark:text-slate-400 uppercase tracking-wider">
                                    Товар
                                </th>
                                <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-slate-500 uppercase tracking-wider">
                                    Количество
                                </th>
                                <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-slate-500 uppercase tracking-wider">
                                    Цена
                                </th>
                                <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-slate-500 uppercase tracking-wider">
                                    Сумма
                                </th>
                            </tr>
                        </thead>
                        <tbody className="bg-white dark:bg-slate-800 divide-y divide-slate-200 dark:divide-slate-700">
                            {order.items.map((item, index) => (
                                <tr key={index}>
                                    <td className="px-6 py-4">
                                        <div className="text-sm font-medium text-slate-900 dark:text-slate-100">{item.product_name}</div>
                                    </td>
                                    <td className="px-6 py-4 whitespace-nowrap text-sm text-slate-500 dark:text-slate-400">
                                        {item.quantity} шт.
                                    </td>
                                    <td className="px-6 py-4 whitespace-nowrap">
                                        <div className="text-sm text-slate-900 dark:text-slate-100">{formatPrice(item.price_uzs)} сум</div>
                                        <div className="text-xs text-slate-500 dark:text-slate-400">{item.price_usd} $</div>
                                    </td>
                                    <td className="px-6 py-4 whitespace-nowrap">
                                        <div className="text-sm font-medium text-slate-900 dark:text-slate-100">
                                            {formatPrice(item.price_uzs * item.quantity)} сум
                                        </div>
                                        <div className="text-xs text-slate-500 dark:text-slate-400">
                                            {(item.price_usd * item.quantity).toFixed(0)} $
                                        </div>
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                        <tfoot className="bg-slate-50 dark:bg-slate-900/50">
                            <tr>
                                <td colSpan="3" className="px-6 py-4 text-right text-sm font-medium text-slate-900 dark:text-slate-100">
                                    Итого:
                                </td>
                                <td className="px-6 py-4 whitespace-nowrap">
                                    <div className="text-base font-bold text-slate-900 dark:text-slate-100">
                                        {formatPrice(order.total_amount_uzs)} сум
                                    </div>
                                    <div className="text-xs font-bold text-slate-500 dark:text-slate-400">
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
                <div className="mt-8">
                    <h4 className="text-sm font-semibold text-slate-900 dark:text-slate-100 uppercase tracking-wider mb-4">Отчет AI-консультанта</h4>
                    <div className="bg-blue-50/50 dark:bg-blue-900/10 rounded-xl p-5 border border-blue-100 dark:border-blue-900/20">
                        <pre className="text-sm text-slate-700 dark:text-slate-300 whitespace-pre-wrap font-sans">{order.consultation_report}</pre>
                    </div>
                </div>
            )}

            <div className="mt-8 flex justify-end pt-5 border-t border-slate-100 dark:border-slate-700">
                <button
                    onClick={onClose}
                    className="bg-white dark:bg-slate-800 text-slate-700 dark:text-slate-300 px-6 py-2.5 border border-slate-300 dark:border-slate-700 rounded-lg hover:bg-slate-50 dark:hover:bg-slate-700 text-sm font-medium transition-colors focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-slate-500"
                >
                    Закрыть
                </button>
            </div>
        </Modal>
    )
}

export default OrderDetailsModal
