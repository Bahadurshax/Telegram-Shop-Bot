import { FILE_UPLOAD } from './constants'

/**
 * Validate a file for upload
 * @param {File} file - The file to validate
 * @returns {object} { valid: boolean, error: string|null }
 */
export const validateFile = (file) => {
    if (!file) {
        return { valid: false, error: 'Файл не выбран' }
    }

    // Check file extension
    const fileName = file.name.toLowerCase()
    const hasValidExtension = FILE_UPLOAD.ALLOWED_EXTENSIONS.some(ext =>
        fileName.endsWith(ext)
    )

    if (!hasValidExtension) {
        return {
            valid: false,
            error: `Пожалуйста, выберите файл ${FILE_UPLOAD.ALLOWED_EXTENSIONS.join(', ')}`
        }
    }

    // Check file size
    if (file.size > FILE_UPLOAD.MAX_SIZE_BYTES) {
        return {
            valid: false,
            error: `Файл слишком большой. Максимум ${FILE_UPLOAD.MAX_SIZE_MB}MB`
        }
    }

    return { valid: true, error: null }
}

/**
 * Validate product form data
 * @param {object} formData - Product form data
 * @returns {object} { valid: boolean, errors: object }
 */
export const validateProductForm = (formData) => {
    const errors = {}

    if (!formData.name || !formData.name.trim()) {
        errors.name = 'Введите название товара'
    }

    if (formData.price_uzs && formData.price_uzs < 0) {
        errors.price_uzs = 'Цена не может быть отрицательной'
    }

    if (formData.price_usd && formData.price_usd < 0) {
        errors.price_usd = 'Цена не может быть отрицательной'
    }

    if (formData.usd_rate && formData.usd_rate < 0) {
        errors.usd_rate = 'Курс не может быть отрицательным'
    }

    return {
        valid: Object.keys(errors).length === 0,
        errors
    }
}
