import { useState, useRef } from 'react'
import { apiService } from '../../services/api'

const ImageUpload = ({
  onImagesUploaded,
  multiple = true,
  maxFiles = 10,
  className = ""
}) => {
  const [uploading, setUploading] = useState(false)
  const [dragActive, setDragActive] = useState(false)
  const [uploadProgress, setUploadProgress] = useState(null)
  const fileInputRef = useRef(null)

  const handleFileSelect = async (files) => {
    if (!files || files.length === 0) return

    // Проверяем количество файлов
    if (files.length > maxFiles) {
      alert(`Максимум ${maxFiles} файлов за раз`)
      return
    }

    // Проверяем типы файлов
    const validTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif', 'image/webp']
    const invalidFiles = Array.from(files).filter(file => !validTypes.includes(file.type))

    if (invalidFiles.length > 0) {
      alert(`Неподдерживаемые форматы файлов: ${invalidFiles.map(f => f.name).join(', ')}`)
      return
    }

    // Проверяем размеры файлов (макс 10MB)
    const maxSize = 10 * 1024 * 1024
    const oversizedFiles = Array.from(files).filter(file => file.size > maxSize)

    if (oversizedFiles.length > 0) {
      alert(`Файлы слишком большие (макс. 10MB): ${oversizedFiles.map(f => f.name).join(', ')}`)
      return
    }

    await uploadFiles(files)
  }

  const uploadFiles = async (files) => {
    setUploading(true)
    setUploadProgress({ current: 0, total: files.length })

    try {
      const result = await apiService.uploadImages(files)

      if (result.success) {
        // Вызываем callback с результатами загрузки
        onImagesUploaded(result.uploaded_files)

        // Очищаем input
        if (fileInputRef.current) {
          fileInputRef.current.value = ''
        }
      } else {
        alert('Ошибка загрузки изображений')
      }

      if (result.errors && result.errors.length > 0) {
        console.warn('Ошибки при загрузке:', result.errors)
        alert(`Некоторые файлы не удалось загрузить: ${result.errors.slice(0, 3).join(', ')}`)
      }

    } catch (error) {
      console.error('Ошибка загрузки:', error)
      alert('Ошибка загрузки изображений: ' + error.message)
    } finally {
      setUploading(false)
      setUploadProgress(null)
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

    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      handleFileSelect(e.dataTransfer.files)
    }
  }

  const handleClick = () => {
    if (fileInputRef.current) {
      fileInputRef.current.click()
    }
  }

  return (
    <div className={`relative ${className}`}>
      <div
        className={`border-2 border-dashed rounded-lg p-6 text-center transition-colors cursor-pointer ${
          dragActive
            ? 'border-blue-500 bg-blue-50'
            : uploading
            ? 'border-gray-300 bg-gray-50'
            : 'border-gray-300 hover:border-gray-400 hover:bg-gray-50'
        }`}
        onDragEnter={handleDrag}
        onDragLeave={handleDrag}
        onDragOver={handleDrag}
        onDrop={handleDrop}
        onClick={uploading ? undefined : handleClick}
      >
        {uploading ? (
          <div className="space-y-3">
            <div className="flex items-center justify-center">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
            </div>
            <p className="text-sm text-gray-600">
              Загрузка в облачное хранилище...
            </p>
            {uploadProgress && (
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div
                  className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                  style={{ width: `${(uploadProgress.current / uploadProgress.total) * 100}%` }}
                ></div>
              </div>
            )}
          </div>
        ) : (
          <div className="space-y-3">
            <div className="flex items-center justify-center">
              <span className="text-4xl">📸</span>
            </div>
            <div>
              <p className="text-base font-medium text-gray-900">
                {multiple
                  ? `Перетащите изображения сюда или нажмите для выбора`
                  : `Перетащите изображение сюда или нажмите для выбора`
                }
              </p>
              <p className="text-sm text-gray-500 mt-1">
                {multiple
                  ? `Поддерживаются: JPG, PNG, GIF, WebP (макс. ${maxFiles} файлов, до 10MB каждый)`
                  : `Поддерживаются: JPG, PNG, GIF, WebP (до 10MB)`
                }
              </p>
            </div>
          </div>
        )}
      </div>

      <input
        ref={fileInputRef}
        type="file"
        accept="image/*"
        multiple={multiple}
        onChange={(e) => handleFileSelect(e.target.files)}
        className="hidden"
      />
    </div>
  )
}

export default ImageUpload