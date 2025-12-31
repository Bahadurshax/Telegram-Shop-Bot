import { useState } from 'react'
import { getSafeImageUrl, getOptimizedImageUrl } from '../../utils/imageKit'

const ImagePreview = ({
  images = [],
  onRemove,
  onCopy,
  size = 'medium',
  showControls = true,
  className = ""
}) => {
  const [loadingImages, setLoadingImages] = useState({})
  const [errorImages, setErrorImages] = useState({})

  const handleImageLoad = (imageId) => {
    setLoadingImages(prev => ({ ...prev, [imageId]: false }))
    setErrorImages(prev => ({ ...prev, [imageId]: false }))
  }

  const handleImageError = (imageId) => {
    setLoadingImages(prev => ({ ...prev, [imageId]: false }))
    setErrorImages(prev => ({ ...prev, [imageId]: true }))
  }

  const handleImageLoadStart = (imageId) => {
    setLoadingImages(prev => ({ ...prev, [imageId]: true }))
  }

  const copyToClipboard = async (url) => {
    try {
      await navigator.clipboard.writeText(url)
      if (onCopy) {
        onCopy(url)
      }
    } catch (error) {
      console.error('Ошибка копирования:', error)
    }
  }

  if (!images || images.length === 0) {
    return (
      <div className={`text-center py-8 text-gray-500 ${className}`}>
        <span className="text-4xl block mb-2">📷</span>
        <p>Нет загруженных изображений</p>
      </div>
    )
  }

  return (
    <div className={`grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4 ${className}`}>
      {images.map((image, index) => {
        const imageId = image.file_id || image.filename || index
        const imageUrl = image.url || image.file_path || ''
        const thumbnailUrl = getSafeImageUrl(imageUrl, size)
        const originalUrl = getOptimizedImageUrl(imageUrl, 'original')
        const isLoading = loadingImages[imageId]
        const hasError = errorImages[imageId]

        return (
          <div
            key={imageId}
            className="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden group hover:shadow-md transition-shadow"
          >
            <div className="relative aspect-square bg-gray-100">
              {isLoading && (
                <div className="absolute inset-0 flex items-center justify-center">
                  <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
                </div>
              )}

              {hasError ? (
                <div className="absolute inset-0 flex items-center justify-center bg-gray-100">
                  <div className="text-center">
                    <span className="text-3xl block mb-2">❌</span>
                    <p className="text-xs text-gray-500">Ошибка загрузки</p>
                  </div>
                </div>
              ) : (
                <img
                  src={thumbnailUrl}
                  alt={image.original_filename || image.name || `Image ${index + 1}`}
                  className="w-full h-full object-cover"
                  onLoadStart={() => handleImageLoadStart(imageId)}
                  onLoad={() => handleImageLoad(imageId)}
                  onError={() => handleImageError(imageId)}
                />
              )}

              {showControls && (
                <div className="absolute inset-0 bg-black bg-opacity-0 group-hover:bg-opacity-20 transition-all duration-200">
                  <div className="absolute top-2 right-2 opacity-0 group-hover:opacity-100 transition-opacity duration-200 space-x-1">
                    {/* Копировать URL */}
                    <button
                      onClick={() => copyToClipboard(originalUrl)}
                      className="bg-blue-600 text-white p-1.5 rounded-md text-xs hover:bg-blue-700 transition-colors"
                      title="Копировать URL"
                    >
                      📋
                    </button>

                    {/* Открыть в новой вкладке */}
                    <button
                      onClick={() => window.open(originalUrl, '_blank')}
                      className="bg-green-600 text-white p-1.5 rounded-md text-xs hover:bg-green-700 transition-colors"
                      title="Открыть в новой вкладке"
                    >
                      🔗
                    </button>

                    {/* Удалить */}
                    {onRemove && (
                      <button
                        onClick={() => onRemove(image, index)}
                        className="bg-red-600 text-white p-1.5 rounded-md text-xs hover:bg-red-700 transition-colors"
                        title="Удалить"
                      >
                        🗑️
                      </button>
                    )}
                  </div>
                </div>
              )}
            </div>

            {/* Информация об изображении */}
            <div className="p-3">
              <div className="text-sm">
                <p className="font-medium text-gray-900 truncate">
                  {image.original_filename || image.name || `Image ${index + 1}`}
                </p>
                <div className="text-xs text-gray-500 mt-1 space-y-1">
                  {image.size && (
                    <p>Размер: {(image.size / 1024).toFixed(1)} KB</p>
                  )}
                  {image.file_type && (
                    <p>Тип: {image.file_type}</p>
                  )}
                  <p className="truncate">
                    URL: {imageUrl.length > 30 ? '...' + imageUrl.slice(-30) : imageUrl}
                  </p>
                </div>
              </div>
            </div>
          </div>
        )
      })}
    </div>
  )
}

export default ImagePreview