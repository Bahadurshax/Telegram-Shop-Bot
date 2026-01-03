import { useState } from 'react'
import { CATEGORIES, CATEGORY_NAMES } from '../../utils/constants'
import { validateProductForm } from '../../utils/validation'
import Modal from '../Common/Modal'

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
                        className="px-4 py-2 bg-blue-600 border border-transparent rounded-lg text-sm font-medium text-white hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 shadow-sm transition-colors"
                    >
                        {product ? 'Сохранить' : 'Добавить'}
                    </button>
                </div>
            </form>
        </Modal>
    )
}

export default ProductForm
