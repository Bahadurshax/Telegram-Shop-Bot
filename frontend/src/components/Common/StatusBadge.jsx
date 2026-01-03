import { getOrderStatusColor, getOrderStatusText } from '../../utils/statusUtils'

const StatusBadge = ({ status, type = 'order' }) => {
    if (type === 'order') {
        return (
            <span className={`px-2.5 py-0.5 inline-flex text-xs font-medium rounded-full ring-1 ring-inset ${getOrderStatusColor(status)}`}>
                {getOrderStatusText(status)}
            </span>
        )
    }

    // Product active status
    if (type === 'product') {
        const activeClass = status
            ? 'bg-emerald-50 dark:bg-emerald-900/20 text-emerald-700 dark:text-emerald-400 ring-emerald-600/20'
            : 'bg-slate-50 dark:bg-slate-700/50 text-slate-600 dark:text-slate-400 ring-slate-500/10'

        return (
            <span className={`px-2.5 py-0.5 inline-flex text-xs font-medium rounded-md ring-1 ring-inset ${activeClass}`}>
                {status ? 'Активен' : 'Неактивен'}
            </span>
        )
    }

    return null
}

export default StatusBadge
