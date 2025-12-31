/**
 * Utility functions for working with ImageKit URLs
 */

/**
 * Check if URL is from ImageKit
 * @param {string} url - Image URL
 * @returns {boolean} - True if ImageKit URL
 */
export const isImageKitUrl = (url) => {
  return url && url.includes('ik.imagekit.io')
}

/**
 * Generate thumbnail URL for ImageKit images
 * @param {string} url - Original ImageKit URL
 * @param {object} options - Transformation options
 * @returns {string} - Thumbnail URL
 */
export const getImageKitThumbnail = (url, options = {}) => {
  if (!isImageKitUrl(url)) {
    return url // Return original URL if not ImageKit
  }

  const {
    width = 300,
    height = 300,
    quality = 80,
    crop = 'maintain_ratio'
  } = options

  // Extract the path from the URL
  const urlParts = url.split('/')
  const endpoint = urlParts.slice(0, 3).join('/')
  const filePath = '/' + urlParts.slice(3).join('/')

  // Build transformation string
  const transformations = [
    `w-${width}`,
    `h-${height}`,
    `q-${quality}`,
    `c-${crop}`
  ].join(',')

  // Construct new URL with transformations
  return `${endpoint}/tr:${transformations}${filePath}`
}

/**
 * Get optimized image URL for different use cases
 * @param {string} url - Original image URL
 * @param {string} size - Size preset ('thumbnail', 'medium', 'large', 'original')
 * @returns {string} - Optimized image URL
 */
export const getOptimizedImageUrl = (url, size = 'medium') => {
  if (!isImageKitUrl(url)) {
    return url
  }

  const sizePresets = {
    thumbnail: { width: 150, height: 150, quality: 70 },
    small: { width: 300, height: 300, quality: 80 },
    medium: { width: 600, height: 600, quality: 85 },
    large: { width: 1200, height: 1200, quality: 90 },
    original: null // No transformations
  }

  const preset = sizePresets[size]
  if (!preset) {
    return url // Return original if no preset
  }

  return getImageKitThumbnail(url, preset)
}

/**
 * Validate image URL
 * @param {string} url - Image URL to validate
 * @returns {boolean} - True if valid image URL
 */
export const isValidImageUrl = (url) => {
  if (!url || typeof url !== 'string') {
    return false
  }

  // Check for common image extensions
  const imageExtensions = /\.(jpg|jpeg|png|gif|webp|svg)(\?|$)/i

  // ImageKit URLs or local URLs with image extensions
  return isImageKitUrl(url) || imageExtensions.test(url)
}

/**
 * Get fallback image URL
 * @returns {string} - Fallback image URL
 */
export const getFallbackImageUrl = () => {
  return '/images/no-image-placeholder.png'
}

/**
 * Safe image URL getter with fallback
 * @param {string} url - Image URL
 * @param {string} size - Size preset
 * @returns {string} - Safe image URL
 */
export const getSafeImageUrl = (url, size = 'medium') => {
  if (!isValidImageUrl(url)) {
    return getFallbackImageUrl()
  }

  return getOptimizedImageUrl(url, size)
}