import { useState } from 'react'
import { apiService } from '../services/api'

const UploadPricelist = () => {
  const [selectedFile, setSelectedFile] = useState(null)
  const [uploading, setUploading] = useState(false)
  const [uploadResult, setUploadResult] = useState(null)
  const [availableSheets, setAvailableSheets] = useState([])
  const [selectedSheets, setSelectedSheets] = useState([])
  const [skipDuplicates, setSkipDuplicates] = useState(true)
  const [dragActive, setDragActive] = useState(false)

  const handleFileSelect = async (file) => {
    if (!file) return

    // Проверяем тип файла
    if (!file.name.toLowerCase().endsWith('.xlsx')) {
      alert('Пожалуйста, выберите файл .xlsx')
      return
    }

    // Проверяем размер (макс 10MB)
    if (file.size > 10 * 1024 * 1024) {
      alert('Файл слишком большой. Максимум 10MB')
      return
    }

    setSelectedFile(file)
    setUploadResult(null)
    setAvailableSheets([])
    setSelectedSheets([])

    // Получаем список листов
    try {
      const sheetsResponse = await apiService.getAvailableSheets(file)
      const sheets = sheetsResponse.sheets || []
      setAvailableSheets(sheets)
      setSelectedSheets(sheets) // по умолчанию выбираем все листы
    } catch (error) {
      console.error('Ошибка получения листов:', error)
      setAvailableSheets([])
      setSelectedSheets([])
    }
  }

  const handleDrag = (e) => {
    e.preventDefault()
    e.stopPropagation()
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true)
    } else if (e.type === "dragleave") {
      setDragActive(false)
    }
  }

  const handleDrop = (e) => {
    e.preventDefault()
    e.stopPropagation()
    setDragActive(false)
    
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFileSelect(e.dataTransfer.files[0])
    }
  }

  const handleUpload = async () => {
    if (!selectedFile) return

    setUploading(true)
    setUploadResult(null)

    try {
      const result = await apiService.uploadPricelist(
        selectedFile,
        selectedSheets,
        skipDuplicates
      )

      setUploadResult(result)
      
      if (result.success) {
        // Обновляем список товаров через 2 секунды
        setTimeout(() => {
          window.location.href = '/products'
        }, 2000)
      }
    } catch (error) {
      setUploadResult({
        success: false,
        error: error.message || 'Ошибка загрузки файла'
      })
    } finally {
      setUploading(false)
    }
  }

  const handleDownloadTemplate = async () => {
    try {
      const token = localStorage.getItem('admin_token')
      const url = `${apiService.baseURL}/upload/template`
      
      // Создаем ссылку для скачивания
      const response = await fetch(url, {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${token}`
        }
      })
      
      if (!response.ok) {
        throw new Error('Ошибка скачивания')
      }
      
      // Получаем blob
      const blob = await response.blob()
      
      // Создаем URL для blob
      const downloadUrl = window.URL.createObjectURL(blob)
      
      // Создаем временную ссылку и кликаем по ней
      const link = document.createElement('a')
      link.href = downloadUrl
      link.download = 'template_pricelist.xlsx'
      document.body.appendChild(link)
      link.click()
      
      // Очищаем
      document.body.removeChild(link)
      window.URL.revokeObjectURL(downloadUrl)
      
    } catch (error) {
      console.error('Ошибка скачивания шаблона:', error)
      alert('Ошибка скачивания шаблона. Попробуйте позже.')
    }
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold text-gray-900">Загрузка прайс-листа</h1>
        <button
          onClick={handleDownloadTemplate}
          className="flex items-center px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
        >
          <span className="mr-2">📥</span>
          Скачать шаблон
        </button>
      </div>

      {/* Инструкция */}
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
        <h3 className="font-medium text-blue-900 mb-2">📋 Инструкция</h3>
        <ul className="text-sm text-blue-800 space-y-1">
          <li>1. Скачайте шаблон Excel и заполните его данными товаров</li>
          <li>2. Добавьте изображения товаров прямо в ячейки (Вставка → Рисунок)</li>
          <li>3. Загрузите заполненный файл через форму ниже</li>
          <li>4. Система автоматически извлечет изображения и создаст товары</li>
        </ul>
      </div>

      {/* Зона загрузки файла */}
      <div className="bg-white rounded-lg shadow p-6">
        <div
          className={`border-2 border-dashed rounded-lg p-8 text-center transition-colors ${
            dragActive 
              ? 'border-blue-500 bg-blue-50' 
              : 'border-gray-300 hover:border-gray-400'
          }`}
          onDragEnter={handleDrag}
          onDragLeave={handleDrag}
          onDragOver={handleDrag}
          onDrop={handleDrop}
        >
          {selectedFile ? (
            <div className="space-y-4">
              <div className="flex items-center justify-center">
                <span className="text-4xl">📄</span>
              </div>
              <div>
                <p className="text-lg font-medium text-gray-900">{selectedFile.name}</p>
                <p className="text-sm text-gray-500">
                  {(selectedFile.size / 1024 / 1024).toFixed(2)} MB
                </p>
              </div>
              <button
                onClick={() => {
                  setSelectedFile(null)
                  setAvailableSheets([])
                  setSelectedSheets([])
                  setUploadResult(null)
                }}
                className="text-red-600 hover:text-red-700 text-sm"
              >
                Удалить файл
              </button>
            </div>
          ) : (
            <div className="space-y-4">
              <div className="flex items-center justify-center">
                <span className="text-6xl">📤</span>
              </div>
              <div>
                <p className="text-lg font-medium text-gray-900">
                  Перетащите файл сюда или
                </p>
                <label className="cursor-pointer">
                  <span className="text-blue-600 hover:text-blue-700">
                    выберите файл
                  </span>
                  <input
                    type="file"
                    accept=".xlsx"
                    onChange={(e) => handleFileSelect(e.target.files[0])}
                    className="hidden"
                  />
                </label>
              </div>
              <p className="text-sm text-gray-500">
                Поддерживаются только файлы .xlsx (макс. 10MB)
              </p>
            </div>
          )}
        </div>

        {/* Настройки загрузки */}
        {selectedFile && (
          <div className="mt-6 space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {/* Выбор листов */}
              {availableSheets.length > 0 && (
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Листы для импорта
                  </label>
                  <select
                    multiple
                    value={selectedSheets}
                    onChange={(e) =>
                      setSelectedSheets(
                        Array.from(e.target.selectedOptions, (option) => option.value)
                      )
                    }
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500 h-28"
                  >
                    {availableSheets.map((sheet) => (
                      <option key={sheet} value={sheet}>
                        {sheet}
                      </option>
                    ))}
                  </select>
                  <p className="text-xs text-gray-500 mt-1">
                    Удерживайте Ctrl (Windows) или Command (macOS), чтобы выбрать несколько листов
                  </p>
                </div>
              )}

              {/* Пропуск дубликатов */}
              <div>
                <label className="flex items-center space-x-2 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={skipDuplicates}
                    onChange={(e) => setSkipDuplicates(e.target.checked)}
                    className="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
                  />
                  <span className="text-sm font-medium text-gray-700">
                    Пропускать дубликаты
                  </span>
                </label>
                <p className="text-xs text-gray-500 mt-1 ml-6">
                  Товары с одинаковыми названиями будут пропущены
                </p>
              </div>
            </div>

            {/* Кнопка загрузки */}
            <button
              onClick={handleUpload}
              disabled={uploading}
              className="w-full bg-green-600 text-white px-6 py-3 rounded-md hover:bg-green-700 disabled:bg-gray-400 disabled:cursor-not-allowed flex items-center justify-center"
            >
              {uploading ? (
                <>
                  <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white mr-2"></div>
                  Загрузка и обработка...
                </>
              ) : (
                <>
                  <span className="mr-2">⬆️</span>
                  Загрузить прайс-лист
                </>
              )}
            </button>
          </div>
        )}
      </div>

      {/* Результат загрузки */}
      {uploadResult && (
        <div className={`rounded-lg p-6 ${
          uploadResult.success 
            ? 'bg-green-50 border border-green-200' 
            : 'bg-red-50 border border-red-200'
        }`}>
          <div className="flex items-start">
            <span className="text-3xl mr-4">
              {uploadResult.success ? '✅' : '❌'}
            </span>
            <div className="flex-1">
              <h3 className={`text-lg font-medium ${
                uploadResult.success ? 'text-green-900' : 'text-red-900'
              }`}>
                {uploadResult.success ? 'Загрузка успешна!' : 'Ошибка загрузки'}
              </h3>
              
              {uploadResult.success ? (
                <div className="mt-3 space-y-2">
                  <p className="text-sm text-green-800">
                    {uploadResult.message}
                  </p>
                  
                  {/* Статистика */}
                  {uploadResult.stats && (
                    <div className="bg-white rounded p-4 mt-3">
                      <h4 className="font-medium text-gray-900 mb-2">Статистика импорта:</h4>
                      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                        <div>
                          <span className="text-gray-600">Всего строк:</span>
                          <span className="ml-2 font-medium">{uploadResult.stats.total_rows}</span>
                        </div>
                        <div>
                          <span className="text-gray-600">Обработано:</span>
                          <span className="ml-2 font-medium text-green-600">{uploadResult.stats.processed}</span>
                        </div>
                        <div>
                          <span className="text-gray-600">Создано:</span>
                          <span className="ml-2 font-medium text-blue-600">{uploadResult.stats.created}</span>
                        </div>
                        <div>
                          <span className="text-gray-600">Пропущено:</span>
                          <span className="ml-2 font-medium text-gray-600">{uploadResult.stats.skipped}</span>
                        </div>
                        {uploadResult.stats.duplicates > 0 && (
                          <div>
                            <span className="text-gray-600">Дубликатов:</span>
                            <span className="ml-2 font-medium text-yellow-600">{uploadResult.stats.duplicates}</span>
                          </div>
                        )}
                        {uploadResult.stats.errors > 0 && (
                          <div>
                            <span className="text-gray-600">Ошибок:</span>
                            <span className="ml-2 font-medium text-red-600">{uploadResult.stats.errors}</span>
                          </div>
                        )}
                      </div>
                    </div>
                  )}

                  {/* Ошибки */}
                  {uploadResult.errors && uploadResult.errors.length > 0 && (
                    <div className="mt-3">
                      <details className="cursor-pointer">
                        <summary className="text-sm font-medium text-yellow-800">
                          Предупреждения ({uploadResult.errors.length})
                        </summary>
                        <ul className="mt-2 text-xs text-yellow-700 space-y-1 ml-4">
                          {uploadResult.errors.map((error, index) => (
                            <li key={index}>• {error}</li>
                          ))}
                        </ul>
                      </details>
                    </div>
                  )}

                  <p className="text-sm text-green-700 mt-3">
                    ↻ Перенаправление на страницу товаров...
                  </p>
                </div>
              ) : (
                <div className="mt-3">
                  <p className="text-sm text-red-800">
                    {uploadResult.error || 'Произошла ошибка при обработке файла'}
                  </p>
                  {uploadResult.errors && uploadResult.errors.length > 0 && (
                    <ul className="mt-2 text-xs text-red-700 space-y-1">
                      {uploadResult.errors.slice(0, 5).map((error, index) => (
                        <li key={index}>• {error}</li>
                      ))}
                      {uploadResult.errors.length > 5 && (
                        <li>... и еще {uploadResult.errors.length - 5} ошибок</li>
                      )}
                    </ul>
                  )}
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Справка */}
      <div className="bg-gray-50 rounded-lg p-6">
        <h3 className="font-medium text-gray-900 mb-3">💡 Полезная информация</h3>
        <div className="text-sm text-gray-700 space-y-2">
          <p><strong>Формат файла:</strong> Excel (.xlsx) с данными на первом листе</p>
          <p><strong>Обязательные столбцы:</strong> Название товара, Цена</p>
          <p><strong>Опциональные столбцы:</strong> Фото, Описание, Цена ($), Курс ($)</p>
          <p><strong>Изображения:</strong> Вставляйте картинки прямо в ячейки Excel</p>
          <p><strong>Категории:</strong> Определяются автоматически по ключевым словам в названии</p>
          <p><strong>Дубликаты:</strong> Товары с одинаковыми названиями пропускаются (если включена опция)</p>
        </div>
      </div>
    </div>
  )
}

export default UploadPricelist