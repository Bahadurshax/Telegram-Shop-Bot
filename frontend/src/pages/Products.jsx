import { useState, useEffect } from 'react'
import { apiService } from '../services/api'
import { formatPrice } from '../utils/formatters'
import { getCategoryName } from '../utils/statusUtils'
import { CATEGORY_NAMES, PAGINATION } from '../utils/constants'
import Loading from '../components/Common/Loading'
import StatusBadge from '../components/Common/StatusBadge'
import Pagination from '../components/Common/Pagination'
import ProductForm from '../components/Products/ProductForm'

const Products = () => {
  const [products, setProducts] = useState([])
  const [loading, setLoading] = useState(true)
  const [currentPage, setCurrentPage] = useState(0)
  const [totalCount, setTotalCount] = useState(0)
  const [searchQuery, setSearchQuery] = useState('')
  const [selectedCategory, setSelectedCategory] = useState('')
  const [selectedStatus, setSelectedStatus] = useState('all')
  const [showForm, setShowForm] = useState(false)
  const [editingProduct, setEditingProduct] = useState(null)

  useEffect(() => {
    loadProducts()
    loadProductsCount()
  }, [currentPage, searchQuery, selectedCategory, selectedStatus])

  const loadProducts = async () => {
    setLoading(true)
    try {
      const params = {
        skip: currentPage * PAGINATION.ITEMS_PER_PAGE,
        limit: PAGINATION.ITEMS_PER_PAGE,
        ...(searchQuery && { search: searchQuery }),
        ...(selectedCategory && { category: selectedCategory }),
        ...(selectedStatus !== 'all' && { is_active: selectedStatus === 'active' })
      }
      const data = await apiService.getProducts(params)
      setProducts(data)
    } catch (error) {
      console.error('Error loading products:', error)
    } finally {
      setLoading(false)
    }
  }

  const loadProductsCount = async () => {
    try {
      const params = {
        ...(selectedCategory && { category: selectedCategory }),
        ...(selectedStatus !== 'all' && { is_active: selectedStatus === 'active' })
      }
      const data = await apiService.getProductsCount(params)
      setTotalCount(data.count)
    } catch (error) {
      console.error('Error loading products count:', error)
    }
  }

  const handleDeleteProduct = async (id) => {
    if (!confirm('Вы уверены, что хотите деактивировать этот товар?')) return

    try {
      await apiService.deleteProduct(id)
      loadProducts()
      loadProductsCount()
    } catch (error) {
      console.error('Error deleting product:', error)
      alert('Ошибка при деактивации товара')
    }
  }

  const handleToggleActive = async (product) => {
    try {
      await apiService.updateProduct(product._id, {
        ...product,
        is_active: !product.is_active
      })
      loadProducts()
      loadProductsCount()
    } catch (error) {
      console.error('Error toggling product status:', error)
      alert('Ошибка при изменении статуса товара')
    }
  }

  const handleEditProduct = (product) => {
    setEditingProduct(product)
    setShowForm(true)
  }

  const handleFormSubmit = async (productData) => {
    try {
      if (editingProduct) {
        await apiService.updateProduct(editingProduct._id, productData)
      } else {
        await apiService.createProduct(productData)
      }
      setShowForm(false)
      setEditingProduct(null)
      loadProducts()
      loadProductsCount()
    } catch (error) {
      console.error('Error saving product:', error)
      alert('Ошибка при сохранении товара')
    }
  }

  return (
    <div className="space-y-8">
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 dark:text-slate-100">Товары</h1>
          <p className="mt-1 text-sm text-slate-500 dark:text-slate-400">
            Управление каталогом товаров
          </p>
        </div>
        <button
          onClick={() => setShowForm(true)}
          className="inline-flex items-center px-4 py-2 bg-primary-600 hover:bg-primary-700 text-white text-sm font-medium rounded-lg shadow-sm transition-colors focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
        >
          <svg className="w-5 h-5 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
          </svg>
          Добавить товар
        </button>
      </div>

      {/* Фильтры */}
      <div className="bg-white dark:bg-slate-800 rounded-xl shadow-sm border border-slate-200 dark:border-slate-700 p-5 transition-colors">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
          <div className="relative">
            <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
              <svg className="h-5 w-5 text-slate-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
              </svg>
            </div>
            <input
              type="text"
              placeholder="Поиск товаров..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="block w-full pl-10 pr-3 py-2.5 border border-slate-300 dark:border-slate-600 rounded-lg leading-5 bg-white dark:bg-slate-800 placeholder-slate-400 dark:placeholder-slate-500 text-slate-900 dark:text-slate-100 focus:outline-none focus:ring-1 focus:ring-primary-500 focus:border-primary-500 sm:text-sm transition duration-150 ease-in-out"
            />
          </div>
          <div>
            <select
              value={selectedCategory}
              onChange={(e) => setSelectedCategory(e.target.value)}
              className="block w-full pl-3 pr-10 py-2.5 text-base border border-slate-300 dark:border-slate-600 focus:outline-none focus:ring-primary-500 focus:border-primary-500 sm:text-sm rounded-lg bg-white dark:bg-slate-800 text-slate-900 dark:text-slate-100 transition-colors"
            >
              <option value="">Все категории</option>
              {Object.entries(CATEGORY_NAMES).map(([key, value]) => (
                <option key={key} value={key}>{value}</option>
              ))}
            </select>
          </div>
          <div>
            <select
              value={selectedStatus}
              onChange={(e) => {
                setSelectedStatus(e.target.value)
                setCurrentPage(0)
              }}
              className="block w-full pl-3 pr-10 py-2.5 text-base border border-slate-300 dark:border-slate-600 focus:outline-none focus:ring-primary-500 focus:border-primary-500 sm:text-sm rounded-lg bg-white dark:bg-slate-800 text-slate-900 dark:text-slate-100 transition-colors"
            >
              <option value="all">Все (активные и нет)</option>
              <option value="active">Только активные</option>
              <option value="inactive">Только неактивные</option>
            </select>
          </div>
        </div>
      </div>

      {/* Таблица товаров */}
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
                      Фото
                    </th>
                    <th scope="col" className="px-6 py-4 text-left text-xs font-semibold text-slate-500 uppercase tracking-wider">
                      Название
                    </th>
                    <th scope="col" className="px-6 py-4 text-left text-xs font-semibold text-slate-500 uppercase tracking-wider">
                      Категория
                    </th>
                    <th scope="col" className="px-6 py-4 text-left text-xs font-semibold text-slate-500 uppercase tracking-wider">
                      Цена
                    </th>
                    <th scope="col" className="px-6 py-4 text-left text-xs font-semibold text-slate-500 uppercase tracking-wider">
                      Статус
                    </th>
                    <th scope="col" className="relative px-6 py-4">
                      <span className="sr-only">Действия</span>
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white dark:bg-slate-800 divide-y divide-slate-200 dark:divide-slate-700">
                  {products.map((product) => (
                    <tr key={product._id} className="hover:bg-slate-50 dark:hover:bg-slate-700/50 transition-colors">
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="h-12 w-12 flex-shrink-0">
                          {product.image_url ? (
                            <img
                              className="h-12 w-12 rounded-lg object-cover border border-slate-200 dark:border-slate-700"
                              src={product.image_url}
                              alt={product.name}
                            />
                          ) : (
                            <div className="h-12 w-12 rounded-lg bg-slate-100 dark:bg-slate-700 border border-slate-200 dark:border-slate-600 flex items-center justify-center">
                              <svg className="h-6 w-6 text-slate-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
                              </svg>
                            </div>
                          )}
                        </div>
                      </td>
                      <td className="px-6 py-4">
                        <div className="text-sm font-medium text-slate-900 dark:text-slate-100">{product.name}</div>
                        <div className="text-sm text-slate-500 dark:text-slate-400 truncate max-w-xs">{product.description}</div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-slate-600 dark:text-slate-400">
                        {getCategoryName(product.category)}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm font-medium text-slate-900 dark:text-slate-100">{formatPrice(product.price_uzs)}</div>
                        <div className="text-xs text-slate-500 dark:text-slate-400">${product.price_usd}</div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <StatusBadge status={product.is_active} type="product" />
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                        <div className="flex items-center justify-end space-x-3">
                          <button
                            onClick={() => handleEditProduct(product)}
                            className="text-primary-600 dark:text-primary-400 hover:text-primary-900 dark:hover:text-primary-300 p-1 rounded-full hover:bg-primary-50 dark:hover:bg-primary-900/20 transition-colors"
                            title="Изменить"
                          >
                            <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                            </svg>
                          </button>
                          {product.is_active ? (
                            <button
                              onClick={() => handleToggleActive(product)}
                              className="text-red-500 dark:text-red-400 hover:text-red-700 dark:hover:text-red-300 p-1 rounded-full hover:bg-red-50 dark:hover:bg-red-900/20 transition-colors"
                              title="Деактивировать"
                            >
                              <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                              </svg>
                            </button>
                          ) : (
                            <button
                              onClick={() => handleToggleActive(product)}
                              className="text-emerald-500 dark:text-emerald-400 hover:text-emerald-700 dark:hover:text-emerald-300 p-1 rounded-full hover:bg-emerald-50 dark:hover:bg-emerald-900/20 transition-colors"
                              title="Активировать"
                            >
                              <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                              </svg>
                            </button>
                          )}
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            {/* Пагинация */}
            <div className="border-t border-slate-200 dark:border-slate-700 px-6 py-4">
              <Pagination
                currentPage={currentPage}
                totalCount={totalCount}
                itemsPerPage={PAGINATION.ITEMS_PER_PAGE}
                onPageChange={setCurrentPage}
                itemName="товаров"
              />
            </div>
          </>
        )}
      </div>

      {/* Форма товара */}
      {showForm && (
        <ProductForm
          product={editingProduct}
          onSubmit={handleFormSubmit}
          onCancel={() => {
            setShowForm(false)
            setEditingProduct(null)
          }}
        />
      )}
    </div>
  )
}

export default Products