import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { apiService } from '../services/api'
import { formatFileSize } from '../utils/formatters'
import { validateFile } from '../utils/validation'
import { FILE_UPLOAD } from '../utils/constants'

const UploadPriceList = () => {
  const navigate = useNavigate()
  const [selectedFile, setSelectedFile] = useState(null)
  const [uploading, setUploading] = useState(false)
  const [uploadResult, setUploadResult] = useState(null)
  const [availableSheets, setAvailableSheets] = useState([])
  const [selectedSheets, setSelectedSheets] = useState([])
  const [skipDuplicates, setSkipDuplicates] = useState(true)
  const [dragActive, setDragActive] = useState(false)

  const handleFileSelect = async (file) => {
    const { valid, error } = validateFile(file)

    if (!valid) {
      alert(error)
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
          navigate('/products')
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
    <div className="space-y-8 max-w-4xl mx-auto">
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 dark:text-slate-100">Загрузка прайс-листа</h1>
          <p className="mt-1 text-sm text-slate-500 dark:text-slate-400">Импорт товаров из Excel файла</p>
        </div>
        <button
          onClick={handleDownloadTemplate}
          className="flex items-center px-4 py-2 bg-white dark:bg-slate-800 border border-slate-300 dark:border-slate-700 rounded-lg text-slate-700 dark:text-slate-300 hover:bg-slate-50 dark:hover:bg-slate-700 transition-colors shadow-sm text-sm font-medium"
        >
          <span className="mr-2 text-lg">📥</span>
          Скачать шаблон
        </button>
      </div>

      {/* Инструкция */}
      <div className="bg-primary-50/50 dark:bg-primary-900/10 border border-primary-100 dark:border-primary-900/20 rounded-xl p-6">
        <h3 className="font-semibold text-primary-900 dark:text-primary-400 mb-3 flex items-center">
          <span className="text-xl mr-2">💡</span> Инструкция по загрузке
        </h3>
        <ul className="text-sm text-primary-800 dark:text-primary-300 space-y-2 ml-1">
          <li className="flex items-start">
            <span className="font-bold mr-2 text-primary-600">1.</span>
            Скачайте шаблон Excel и заполните его данными товаров
          </li>
          <li className="flex items-start">
            <span className="font-bold mr-2 text-primary-600">2.</span>
            Добавьте изображения товаров прямо в ячейки (Вставка → Рисунок)
          </li>
          <li className="flex items-start">
            <span className="font-bold mr-2 text-primary-600">3.</span>
            Загрузите заполненный файл через форму ниже
          </li>
          <li className="flex items-start">
            <span className="font-bold mr-2 text-primary-600">4.</span>
            Система автоматически извлечет изображения и создаст товары
          </li>
        </ul>
      </div>

      {/* Зона загрузки файла */}
      <div className="bg-white dark:bg-slate-800 rounded-xl shadow-sm border border-slate-200 dark:border-slate-700 p-8 transition-colors">
        <div
          className={`
            border-2 border-dashed rounded-xl p-10 text-center transition-all cursor-pointer
            ${dragActive
              ? 'border-primary-500 bg-primary-50/30 dark:bg-primary-900/20'
              : 'border-slate-300 dark:border-slate-700 hover:border-primary-400 dark:hover:border-primary-500 hover:bg-slate-50 dark:hover:bg-slate-700/50'
            }
          `}
          onDragEnter={handleDrag}
          onDragLeave={handleDrag}
          onDragOver={handleDrag}
          onDrop={handleDrop}
        >
          {selectedFile ? (
            <div className="space-y-5">
              <div className="flex items-center justify-center">
                <span className="text-5xl bg-slate-100 dark:bg-slate-700 rounded-2xl p-4">📄</span>
              </div>
              <div>
                <p className="text-lg font-semibold text-slate-900 dark:text-slate-100">{selectedFile.name}</p>
                <p className="text-sm text-slate-500 dark:text-slate-400 font-medium">
                  {formatFileSize(selectedFile.size)}
                </p>
              </div>
              <button
                onClick={(e) => {
                  e.stopPropagation()
                  setSelectedFile(null)
                  setAvailableSheets([])
                  setSelectedSheets([])
                  setUploadResult(null)
                }}
                className="text-red-600 dark:text-red-400 hover:text-red-700 dark:hover:text-red-300 text-sm font-medium hover:underline py-2 px-4 rounded-lg hover:bg-red-50 dark:hover:bg-red-900/20 transition-colors"
              >
                Удалить файл
              </button>
            </div>
          ) : (
            <label className="cursor-pointer block space-y-4">
              <div className="flex items-center justify-center">
                <span className="text-6xl text-slate-200 dark:text-slate-700">📤</span>
              </div>
              <div>
                <p className="text-lg font-medium text-slate-900 dark:text-slate-100">
                  Перетащите файл сюда
                </p>
                <p className="text-sm text-slate-500 dark:text-slate-400 mt-1">
                  или нажмите для выбора
                </p>
              </div>
              <input
                type="file"
                accept={FILE_UPLOAD.ALLOWED_EXTENSIONS.join(',')}
                onChange={(e) => handleFileSelect(e.target.files[0])}
                className="hidden"
              />
              <p className="text-xs text-slate-400 dark:text-slate-500">
                Поддерживаются {FILE_UPLOAD.ALLOWED_EXTENSIONS.join(', ')} до {FILE_UPLOAD.MAX_SIZE_MB}MB
              </p>
            </label>
          )}
        </div>

        {/* Настройки загрузки */}
        {selectedFile && (
          <div className="mt-8 space-y-6 pt-6 border-t border-slate-100 dark:border-slate-700">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {/* Выбор листов */}
              {availableSheets.length > 0 && (
                <div>
                  <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-text-2">
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
                    className="block w-full pl-3 pr-10 py-2 text-base border-slate-300 dark:border-slate-700 focus:outline-none focus:ring-primary-500 focus:border-primary-500 sm:text-sm rounded-lg h-32 bg-white dark:bg-slate-800 text-slate-900 dark:text-slate-100 transition-colors"
                  >
                    {availableSheets.map((sheet) => (
                      <option key={sheet} value={sheet} className="p-1">
                        {sheet}
                      </option>
                    ))}
                  </select>
                  <p className="text-xs text-slate-500 mt-1.5">
                    Удерживайте Ctrl/Cmd для выбора нескольких
                  </p>
                </div>
              )}

              {/* Пропуск дубликатов */}
              <div>
                <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">
                  Настройки импорта
                </label>
                <div className="flex items-start p-3 bg-slate-50 dark:bg-slate-900/30 rounded-lg border border-slate-200 dark:border-slate-700">
                  <div className="flex items-center h-5">
                    <input
                      id="skip-duplicates"
                      name="skip-duplicates"
                      type="checkbox"
                      checked={skipDuplicates}
                      onChange={(e) => setSkipDuplicates(e.target.checked)}
                      className="focus:ring-primary-500 h-4 w-4 text-primary-600 border-slate-300 rounded"
                    />
                  </div>
                  <div className="ml-3 text-sm">
                    <label htmlFor="skip-duplicates" className="font-medium text-slate-900 dark:text-slate-100 cursor-pointer">
                      Пропускать дубликаты
                    </label>
                    <p className="text-slate-500 dark:text-slate-400 mt-1">Товары с совпадающими названиями будут пропущены при импорте</p>
                  </div>
                </div>
              </div>
            </div>

            {/* Кнопка загрузки */}
            <button
              onClick={handleUpload}
              disabled={uploading}
              className="w-full bg-slate-900 text-white px-6 py-3.5 rounded-xl hover:bg-slate-800 disabled:bg-slate-300 disabled:cursor-not-allowed flex items-center justify-center font-medium shadow-lg shadow-slate-200 transition-all hover:translate-y-[-1px]"
            >
              {uploading ? (
                <>
                  <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white mr-3"></div>
                  Обработка данных...
                </>
              ) : (
                <>
                  <span className="mr-2">🚀</span>
                  Загрузить и обработать
                </>
              )}
            </button>
          </div>
        )}
      </div>

      {/* Результат загрузки */}
      {uploadResult && (
        <div className={`rounded-xl p-6 border transition-colors ${uploadResult.success
          ? 'bg-emerald-50 dark:bg-emerald-900/10 border-emerald-200 dark:border-emerald-900/20'
          : 'bg-red-50 dark:bg-red-900/10 border-red-200 dark:border-red-900/20'
          }`}>
          <div className="flex items-start">
            <span className="text-3xl mr-4 mt-0.5">
              {uploadResult.success ? '✅' : '❌'}
            </span>
            <div className="flex-1">
              <h3 className={`text-lg font-bold ${uploadResult.success ? 'text-emerald-900 dark:text-emerald-400' : 'text-red-900 dark:text-red-400'
                }`}>
                {uploadResult.success ? 'Загрузка успешно завершена' : 'Ошибка при загрузке'}
              </h3>

              {uploadResult.success ? (
                <div className="mt-4 space-y-4">
                  <p className="text-sm text-emerald-800 dark:text-emerald-300 font-medium">
                    {uploadResult.message}
                  </p>

                  {/* Статистика */}
                  {uploadResult.stats && (
                    <div className="bg-white/60 dark:bg-slate-800/60 rounded-lg p-4 border border-emerald-100 dark:border-emerald-900/30">
                      <h4 className="font-semibold text-emerald-900 dark:text-emerald-400 mb-3 text-sm uppercase tracking-wider">Статистика импорта</h4>
                      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                        <div className="bg-white dark:bg-slate-800 p-2 rounded border border-emerald-100/50 dark:border-emerald-900/20">
                          <span className="text-slate-500 dark:text-slate-400 block text-xs mb-1">Всего строк</span>
                          <span className="font-bold text-slate-900 dark:text-slate-100 text-lg">{uploadResult.stats.total_rows}</span>
                        </div>
                        <div className="bg-white dark:bg-slate-800 p-2 rounded border border-emerald-100/50 dark:border-emerald-900/20">
                          <span className="text-emerald-600 dark:text-emerald-400 block text-xs mb-1">Обработано</span>
                          <span className="font-bold text-emerald-700 dark:text-emerald-300 text-lg">{uploadResult.stats.processed}</span>
                        </div>
                        <div className="bg-white dark:bg-slate-800 p-2 rounded border border-emerald-100/50 dark:border-emerald-900/20">
                          <span className="text-blue-600 dark:text-blue-400 block text-xs mb-1">Создано</span>
                          <span className="font-bold text-blue-700 dark:text-blue-300 text-lg">{uploadResult.stats.created}</span>
                        </div>
                        <div className="bg-white dark:bg-slate-800 p-2 rounded border border-emerald-100/50 dark:border-emerald-900/20">
                          <span className="text-slate-500 dark:text-slate-400 block text-xs mb-1">Пропущено</span>
                          <span className="font-bold text-slate-700 dark:text-slate-300 text-lg">{uploadResult.stats.skipped}</span>
                        </div>
                      </div>

                      {(uploadResult.stats.duplicates > 0 || uploadResult.stats.errors > 0) && (
                        <div className="mt-2 grid grid-cols-2 gap-4 text-sm">
                          {uploadResult.stats.duplicates > 0 && (
                            <div className="text-yellow-700 bg-yellow-50 px-2 py-1 rounded text-xs font-medium">
                              ⚠️ Дубликатов: {uploadResult.stats.duplicates}
                            </div>
                          )}
                          {uploadResult.stats.errors > 0 && (
                            <div className="text-red-700 bg-red-50 px-2 py-1 rounded text-xs font-medium">
                              🔴 Ошибок: {uploadResult.stats.errors}
                            </div>
                          )}
                        </div>
                      )}
                    </div>
                  )}

                  {/* Ошибки */}
                  {uploadResult.errors && uploadResult.errors.length > 0 && (
                    <div className="mt-2">
                      <details className="cursor-pointer group">
                        <summary className="text-sm font-medium text-yellow-800 hover:text-yellow-900 transition-colors">
                          Показать предупреждения ({uploadResult.errors.length})
                        </summary>
                        <ul className="mt-2 text-xs text-yellow-800 bg-yellow-50/50 p-3 rounded-lg space-y-1">
                          {uploadResult.errors.map((error, index) => (
                            <li key={index} className="flex items-start">
                              <span className="mr-2">•</span>
                              {error}
                            </li>
                          ))}
                        </ul>
                      </details>
                    </div>
                  )}

                  <p className="text-sm text-emerald-700 mt-2 italic flex items-center">
                    <span className="animate-spin h-3 w-3 border-2 border-emerald-600 border-t-transparent rounded-full mr-2"></span>
                    Перенаправление на страницу товаров...
                  </p>
                </div>
              ) : (
                <div className="mt-3">
                  <p className="text-sm text-red-800 dark:text-red-300 font-medium">
                    {uploadResult.error || 'Произошла ошибка при обработке файла'}
                  </p>
                  {uploadResult.errors && uploadResult.errors.length > 0 && (
                    <div className="mt-3 bg-red-100/50 dark:bg-red-900/20 p-3 rounded-lg border border-red-200/50 dark:border-red-900/30">
                      <ul className="text-xs text-red-700 dark:text-red-400 space-y-1">
                        {uploadResult.errors.slice(0, 5).map((error, index) => (
                          <li key={index}>• {error}</li>
                        ))}
                        {uploadResult.errors.length > 5 && (
                          <li className="pt-1 font-medium italic">... и еще {uploadResult.errors.length - 5} ошибок</li>
                        )}
                      </ul>
                    </div>
                  )}
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Справка */}
      <div className="bg-slate-50 dark:bg-slate-800 rounded-xl p-6 border border-slate-200 dark:border-slate-700 transition-colors">
        <h3 className="font-semibold text-slate-900 dark:text-slate-100 mb-4 flex items-center">
          <span className="text-xl mr-2">ℹ️</span> Полезная информация
        </h3>
        <div className="text-sm text-slate-600 dark:text-slate-400 space-y-3 pl-1">
          <p><strong className="text-slate-900 dark:text-slate-200">Формат файла:</strong> Excel (.xlsx) с данными на первом листе</p>
          <p><strong className="text-slate-900 dark:text-slate-200">Обязательные столбцы:</strong> Название товара, Цена</p>
          <p><strong className="text-slate-900 dark:text-slate-200">Опциональные столбцы:</strong> Фото, Описание, Цена ($), Курс ($)</p>
          <p><strong className="text-slate-900 dark:text-slate-200">Изображения:</strong> Вставляйте картинки прямо в ячейки Excel</p>
          <p><strong className="text-slate-900 dark:text-slate-200">Категории:</strong> Определяются автоматически по ключевым словам</p>
          <p><strong className="text-slate-900 dark:text-slate-200">Дубликаты:</strong> Товары с одинаковыми названиями пропускаются (если включена опция)</p>
        </div>
      </div>
    </div>
  )
}

export default UploadPriceList