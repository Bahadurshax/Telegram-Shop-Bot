import { useState } from 'react'
import { CATEGORIES, CATEGORY_NAMES } from '../../utils/constants'
import { validateProductForm } from '../../utils/validation'
import { apiService } from '../../services/api'
import Modal from '../Common/Modal'

const MAX_IMAGE_SIZE_MB = 10

const DEVICE_TYPE_NAMES = {
    camera_ip: 'IP-камера',
    camera_analog: 'Аналоговая камера',
    nvr: 'NVR',
    dvr: 'DVR',
    hdd: 'Жёсткий диск',
    accessory: 'Аксессуар'
}

// Атрибут -> человекочитаемая метка (для чипов в форме)
const attrsToChips = (attrs) => {
    if (!attrs) return []
    const chips = []
    if (attrs.device_type) chips.push(DEVICE_TYPE_NAMES[attrs.device_type] || attrs.device_type)
    if (attrs.resolution_mp) chips.push(`${attrs.resolution_mp} Мп`)
    if (attrs.outdoor === true) chips.push('Улица')
    if (attrs.outdoor === false) chips.push('Помещение')
    if (attrs.ir_range_m) chips.push(`ИК ${attrs.ir_range_m} м`)
    if (attrs.focal_length_mm) chips.push(`Объектив ${attrs.focal_length_mm} мм`)
    if (attrs.poe) chips.push('PoE')
    if (attrs.has_audio) chips.push('Звук')
    if (attrs.wdr) chips.push('WDR')
    if (attrs.channels) chips.push(`${attrs.channels} каналов`)
    if (attrs.poe_ports) chips.push(`${attrs.poe_ports} PoE-портов`)
    if (attrs.max_hdd_count) chips.push(`До ${attrs.max_hdd_count} HDD`)
    if (attrs.capacity_tb) chips.push(`${attrs.capacity_tb} ТБ`)
    return chips
}

const ProductForm = ({ product, onSubmit, onCancel }) => {
    const [formData, setFormData] = useState({
        name: product?.name || '',
        description: product?.description || '',
        price_uzs: product?.price_uzs || '',
        price_usd: product?.price_usd || '',
        usd_rate: product?.usd_rate || '',
        category: product?.category || CATEGORIES.IP_CAMERAS,
        is_active: product?.is_active ?? true,
        image_url: product?.image_url || ''
    })
    const [uploadingImage, setUploadingImage] = useState(false)
    const [attrs, setAttrs] = useState(product?.attrs || null)
    const [enriching, setEnriching] = useState(false)

    const handleEnrich = async () => {
        if (!product?.id) return
        setEnriching(true)
        try {
            const updated = await apiService.enrichProduct(product.id)
            setAttrs(updated.attrs || null)
            if (updated.category) {
                setFormData(prev => ({ ...prev, category: updated.category }))
            }
        } catch (error) {
            console.error('Error enriching product:', error)
            alert('Не удалось извлечь характеристики')
        } finally {
            setEnriching(false)
        }
    }

    const handleImageSelect = async (e) => {
        const file = e.target.files[0]
        e.target.value = ''
        if (!file) return

        if (!file.type.startsWith('image/')) {
            alert('Пожалуйста, выберите файл изображения')
            return
        }
        if (file.size > MAX_IMAGE_SIZE_MB * 1024 * 1024) {
            alert(`Файл слишком большой. Максимум ${MAX_IMAGE_SIZE_MB}MB`)
            return
        }

        setUploadingImage(true)
        try {
            const { image_url } = await apiService.uploadProductImage(file)
            setFormData(prev => ({ ...prev, image_url }))
        } catch (error) {
            console.error('Error uploading image:', error)
            alert('Ошибка загрузки изображения')
        } finally {
            setUploadingImage(false)
        }
    }

    const handleImageRemove = () => {
        setFormData(prev => ({ ...prev, image_url: '' }))
    }

    const handleSubmit = (e) => {
        e.preventDefault()

        const { valid, errors } = validateProductForm(formData)
        if (!valid) {
            alert(Object.values(errors)[0])
            return
        }

        onSubmit({
            ...formData,
            price_uzs: parseFloat(formData.price_uzs) || 0,
            price_usd: parseFloat(formData.price_usd) || 0,
            usd_rate: parseFloat(formData.usd_rate) || 0
        })
    }

    const handleChange = (e) => {
        const value = e.target.type === 'checkbox' ? e.target.checked : e.target.value
        setFormData({
            ...formData,
            [e.target.name]: value
        })
    }

    return (
        <Modal
            isOpen={true}
            onClose={onCancel}
            title={product ? 'Редактировать товар' : 'Добавить новый товар'}
            size="lg"
        >
            <form onSubmit={handleSubmit} className="space-y-6">
                <div className="space-y-4">
                    <div>
                        <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">Название</label>
                        <input
                            type="text"
                            name="name"
                            value={formData.name}
                            onChange={handleChange}
                            required
                            placeholder="Например: Камера видеонаблюдения"
                            className="block w-full px-3 py-2 border border-slate-300 dark:border-slate-700 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-shadow bg-white dark:bg-slate-900 text-slate-900 dark:text-slate-100 placeholder-slate-400 dark:placeholder-slate-500"
                        />
                    </div>

                    <div>
                        <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">Описание</label>
                        <textarea
                            name="description"
                            value={formData.description}
                            onChange={handleChange}
                            rows={4}
                            placeholder="Подробное описание товара..."
                            className="block w-full px-3 py-2 border border-slate-300 dark:border-slate-700 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-shadow resize-none bg-white dark:bg-slate-800 text-slate-900 dark:text-slate-100 placeholder-slate-400 dark:placeholder-slate-500"
                        />
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
                        <div>
                            <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">Цена (сум)</label>
                            <div className="relative rounded-md shadow-sm">
                                <input
                                    type="number"
                                    name="price_uzs"
                                    value={formData.price_uzs}
                                    onChange={handleChange}
                                    min="0"
                                    className="block w-full px-3 py-2 border border-slate-300 dark:border-slate-700 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-shadow bg-white dark:bg-slate-900 text-slate-900 dark:text-slate-100 placeholder-slate-400 dark:placeholder-slate-500"
                                />
                            </div>
                        </div>

                        <div>
                            <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">Цена ($)</label>
                            <div className="relative rounded-md shadow-sm">
                                <span className="absolute inset-y-0 left-0 pl-3 flex items-center text-slate-500 dark:text-slate-400 sm:text-sm">$</span>
                                <input
                                    type="number"
                                    name="price_usd"
                                    value={formData.price_usd}
                                    onChange={handleChange}
                                    min="0"
                                    className="block w-full pl-7 pr-3 py-2 border border-slate-300 dark:border-slate-700 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-shadow bg-white dark:bg-slate-800 text-slate-900 dark:text-slate-100 placeholder-slate-400 dark:placeholder-slate-500"
                                />
                            </div>
                        </div>

                        <div>
                            <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">Курс ($)</label>
                            <input
                                type="number"
                                name="usd_rate"
                                value={formData.usd_rate}
                                onChange={handleChange}
                                min="0"
                                className="block w-full px-3 py-2 border border-slate-300 dark:border-slate-700 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-shadow bg-white dark:bg-slate-900 text-slate-900 dark:text-slate-100 placeholder-slate-400 dark:placeholder-slate-500"
                            />
                        </div>
                    </div>

                    <div>
                        <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">Категория</label>
                        <select
                            name="category"
                            value={formData.category}
                            onChange={handleChange}
                            className="block w-full px-3 py-2 border border-slate-300 dark:border-slate-700 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-shadow bg-white dark:bg-slate-800 text-slate-900 dark:text-slate-100"
                        >
                            {Object.entries(CATEGORY_NAMES).map(([key, value]) => (
                                <option key={key} value={key}>{value}</option>
                            ))}
                        </select>
                    </div>

                    {product?.id && (
                        <div>
                            <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">
                                Характеристики (AI)
                            </label>
                            <div className="flex flex-wrap items-center gap-2">
                                {attrsToChips(attrs).map((chip, i) => (
                                    <span
                                        key={i}
                                        className="px-2 py-1 rounded-md bg-slate-100 dark:bg-slate-700 text-xs text-slate-700 dark:text-slate-300"
                                    >
                                        {chip}
                                    </span>
                                ))}
                                {attrsToChips(attrs).length === 0 && (
                                    <span className="text-xs text-slate-400 dark:text-slate-500">
                                        Атрибуты не извлечены — консультант будет опираться только на текст описания
                                    </span>
                                )}
                                <button
                                    type="button"
                                    onClick={handleEnrich}
                                    disabled={enriching}
                                    className="px-3 py-1 rounded-md border border-slate-300 dark:border-slate-700 text-xs font-medium text-slate-700 dark:text-slate-300 hover:bg-slate-50 dark:hover:bg-slate-700 transition-colors disabled:opacity-50 disabled:cursor-wait"
                                >
                                    {enriching ? 'Извлекаем…' : '✨ Переизвлечь'}
                                </button>
                            </div>
                        </div>
                    )}

                    <div>
                        <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">Изображение</label>
                        <div className="flex items-center gap-4">
                            {formData.image_url ? (
                                <img
                                    src={formData.image_url}
                                    alt="Изображение товара"
                                    className="h-20 w-20 rounded-lg object-cover border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-900"
                                />
                            ) : (
                                <div className="h-20 w-20 rounded-lg border border-dashed border-slate-300 dark:border-slate-700 flex items-center justify-center text-slate-400 dark:text-slate-500">
                                    <svg className="w-8 h-8" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
                                    </svg>
                                </div>
                            )}
                            <div className="flex flex-col gap-2">
                                <label className={`px-4 py-2 bg-white dark:bg-slate-800 border border-slate-300 dark:border-slate-700 rounded-lg text-sm font-medium text-slate-700 dark:text-slate-300 hover:bg-slate-50 dark:hover:bg-slate-700 transition-colors text-center ${uploadingImage ? 'opacity-50 cursor-wait' : 'cursor-pointer'}`}>
                                    {uploadingImage ? 'Загрузка...' : (formData.image_url ? 'Заменить' : 'Загрузить изображение')}
                                    <input
                                        type="file"
                                        accept="image/*"
                                        onChange={handleImageSelect}
                                        disabled={uploadingImage}
                                        className="hidden"
                                    />
                                </label>
                                {formData.image_url && !uploadingImage && (
                                    <button
                                        type="button"
                                        onClick={handleImageRemove}
                                        className="text-sm font-medium text-red-600 dark:text-red-400 hover:text-red-700 dark:hover:text-red-300 transition-colors"
                                    >
                                        Удалить
                                    </button>
                                )}
                            </div>
                        </div>
                    </div>

                    <div className="flex items-center">
                        <input
                            id="is_active"
                            type="checkbox"
                            name="is_active"
                            checked={formData.is_active}
                            onChange={handleChange}
                            className="h-4 w-4 text-primary-600 focus:ring-primary-500 border-slate-300 dark:border-slate-700 rounded cursor-pointer bg-white dark:bg-slate-800"
                        />
                        <label htmlFor="is_active" className="ml-2 block text-sm text-slate-900 dark:text-slate-100 cursor-pointer">
                            Активный товар (отображается в каталоге)
                        </label>
                    </div>
                </div>

                <div className="flex justify-end space-x-3 pt-6 border-t border-slate-100 dark:border-slate-700">
                    <button
                        type="button"
                        onClick={onCancel}
                        className="px-4 py-2 bg-white dark:bg-slate-800 border border-slate-300 dark:border-slate-700 rounded-lg text-sm font-medium text-slate-700 dark:text-slate-300 hover:bg-slate-50 dark:hover:bg-slate-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-slate-500 transition-colors"
                    >
                        Отмена
                    </button>
                    <button
                        type="submit"
                        disabled={uploadingImage}
                        className="px-4 py-2 bg-blue-600 border border-transparent rounded-lg text-sm font-medium text-white hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 shadow-sm transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                        {product ? 'Сохранить' : 'Добавить'}
                    </button>
                </div>
            </form>
        </Modal>
    )
}

export default ProductForm
