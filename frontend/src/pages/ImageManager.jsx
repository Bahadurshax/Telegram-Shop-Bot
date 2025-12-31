import { useState } from 'react'
import ImageUpload from '../components/Common/ImageUpload'
import ImagePreview from '../components/Common/ImagePreview'

const ImageManager = () => {
  const [uploadedImages, setUploadedImages] = useState([])
  const [showCopyAlert, setShowCopyAlert] = useState(false)

  const handleImagesUploaded = (newImages) => {
    setUploadedImages(prev => [...prev, ...newImages])
  }

  const handleRemoveImage = (image, index) => {
    if (confirm(`Удалить изображение "${image.original_filename || image.name}"?`)) {
      setUploadedImages(prev => prev.filter((_, i) => i !== index))
    }
  }

  const handleCopyUrl = (url) => {
    setShowCopyAlert(true)
    setTimeout(() => setShowCopyAlert(false), 2000)
  }

  const clearAllImages = () => {
    if (confirm('Очистить все загруженные изображения?')) {
      setUploadedImages([])
    }
  }

  return (
    <div className="space-y-6">
      {/* Заголовок */}
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold text-gray-900">Управление изображениями</h1>
        {uploadedImages.length > 0 && (
          <button
            onClick={clearAllImages}
            className="px-4 py-2 text-red-600 border border-red-200 rounded-md hover:bg-red-50 hover:border-red-300 transition-colors"
          >
            🗑️ Очистить все
          </button>
        )}
      </div>

      {/* Информация */}
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
        <h3 className="font-medium text-blue-900 mb-2">📸 Хранилище изображений</h3>
        <ul className="text-sm text-blue-800 space-y-1">
          <li>• Изображения автоматически загружаются в облачное хранилище (Supabase)</li>
          <li>• Поддерживаются оптимизированные публичные URL для использования в товарах</li>
          <li>• Быстрая доставка контента через CDN Supabase</li>
          <li>• Надёжное и безопасное хранение файлов</li>
        </ul>
      </div>

      {/* Уведомление о копировании */}
      {showCopyAlert && (
        <div className="fixed top-4 right-4 bg-green-100 border border-green-200 text-green-800 px-4 py-2 rounded-md shadow-lg z-50 animate-pulse">
          ✅ URL скопирован в буфер обмена
        </div>
      )}

      {/* Загрузка изображений */}
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">Загрузка изображений</h2>
        <ImageUpload
          onImagesUploaded={handleImagesUploaded}
          multiple={true}
          maxFiles={20}
        />
      </div>

      {/* Статистика */}
      {uploadedImages.length > 0 && (
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Статистика</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="bg-blue-50 rounded-lg p-4">
              <h3 className="text-sm font-medium text-blue-900">Всего изображений</h3>
              <p className="text-2xl font-bold text-blue-600">{uploadedImages.length}</p>
            </div>
            <div className="bg-green-50 rounded-lg p-4">
              <h3 className="text-sm font-medium text-green-900">Общий размер</h3>
              <p className="text-2xl font-bold text-green-600">
                {uploadedImages.reduce((sum, img) => sum + (img.size || 0), 0) > 0
                  ? `${(uploadedImages.reduce((sum, img) => sum + (img.size || 0), 0) / (1024 * 1024)).toFixed(1)} MB`
                  : '—'
                }
              </p>
            </div>
            <div className="bg-purple-50 rounded-lg p-4">
              <h3 className="text-sm font-medium text-purple-900">Публичные URL</h3>
              <p className="text-2xl font-bold text-purple-600">
                {uploadedImages.filter(img => !!img.url).length}
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Загруженные изображения */}
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">
          Загруженные изображения ({uploadedImages.length})
        </h2>

        <ImagePreview
          images={uploadedImages}
          onRemove={handleRemoveImage}
          onCopy={handleCopyUrl}
          size="medium"
          showControls={true}
        />
      </div>

      {/* Инструкции */}
      <div className="bg-gray-50 rounded-lg p-6">
        <h3 className="font-medium text-gray-900 mb-3">💡 Как использовать</h3>
        <div className="text-sm text-gray-700 space-y-2">
          <p><strong>1. Загрузка:</strong> Перетащите изображения в область загрузки или нажмите для выбора файлов</p>
          <p><strong>2. Копирование URL:</strong> Наведите на изображение и нажмите кнопку 📋 для копирования URL</p>
          <p><strong>3. Просмотр:</strong> Нажмите 🔗 для открытия изображения в полном размере</p>
          <p><strong>4. Удаление:</strong> Нажмите 🗑️ для удаления изображения из списка (файл останется в облачном хранилище)</p>
          <p><strong>5. В товарах:</strong> Скопированные URL можно использовать при создании/редактировании товаров</p>
        </div>
      </div>
    </div>
  )
}

export default ImageManager