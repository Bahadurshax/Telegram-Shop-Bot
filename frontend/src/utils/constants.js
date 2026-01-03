// Category mappings
export const CATEGORIES = {
    IP_CAMERAS: 'ip_cameras',
    ANALOG: 'analog',
    DVR: 'dvr',
    ACCESSORIES: 'accessories'
}

export const CATEGORY_NAMES = {
    [CATEGORIES.IP_CAMERAS]: 'IP камеры',
    [CATEGORIES.ANALOG]: 'Аналоговые',
    [CATEGORIES.DVR]: 'Регистраторы',
    [CATEGORIES.ACCESSORIES]: 'Аксессуары'
}

export const CATEGORY_ICONS = {
    [CATEGORIES.IP_CAMERAS]: 'Cctv',
    [CATEGORIES.ANALOG]: 'Video',
    [CATEGORIES.DVR]: 'HardDrive',
    [CATEGORIES.ACCESSORIES]: 'Plug'
}

// Order statuses
export const ORDER_STATUS = {
    NEW: 'new',
    PROCESSING: 'processing',
    COMPLETED: 'completed',
    CANCELLED: 'cancelled'
}

export const ORDER_STATUS_NAMES = {
    [ORDER_STATUS.NEW]: 'Новый',
    [ORDER_STATUS.PROCESSING]: 'В обработке',
    [ORDER_STATUS.COMPLETED]: 'Выполнен',
    [ORDER_STATUS.CANCELLED]: 'Отменен'
}

export const ORDER_STATUS_COLORS = {
    [ORDER_STATUS.NEW]: 'bg-blue-100 text-blue-800',
    [ORDER_STATUS.PROCESSING]: 'bg-yellow-100 text-yellow-800',
    [ORDER_STATUS.COMPLETED]: 'bg-green-100 text-green-800',
    [ORDER_STATUS.CANCELLED]: 'bg-red-100 text-red-800'
}

// Pagination
export const PAGINATION = {
    ITEMS_PER_PAGE: 10,
    MAX_PAGE_BUTTONS: 5
}

// File upload
export const FILE_UPLOAD = {
    MAX_SIZE_MB: 10,
    MAX_SIZE_BYTES: 10 * 1024 * 1024,
    ALLOWED_EXTENSIONS: ['.xlsx']
}

// API
export const API_CONFIG = {
    BASE_URL: '/admin/api',
    TOKEN_KEY: 'admin_token'
}
