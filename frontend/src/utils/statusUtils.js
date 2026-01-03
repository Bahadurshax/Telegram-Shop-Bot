import {
    ORDER_STATUS_COLORS,
    ORDER_STATUS_NAMES,
    CATEGORY_NAMES,
    CATEGORY_ICONS
} from './constants'

/**
 * Get the Tailwind CSS color classes for an order status
 * @param {string} status - Order status
 * @returns {string} Tailwind CSS classes
 */
export const getOrderStatusColor = (status) => {
    return ORDER_STATUS_COLORS[status] || 'bg-gray-100 text-gray-800'
}

/**
 * Get the display text for an order status
 * @param {string} status - Order status
 * @returns {string} Display text
 */
export const getOrderStatusText = (status) => {
    return ORDER_STATUS_NAMES[status] || status
}

/**
 * Get the display name for a category
 * @param {string} categoryKey - Category key
 * @returns {string} Category display name
 */
export const getCategoryName = (categoryKey) => {
    return CATEGORY_NAMES[categoryKey] || categoryKey
}