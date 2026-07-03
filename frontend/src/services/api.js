import { API_CONFIG } from '../utils/constants'

class ApiService {
  constructor() {
    this.baseURL = API_CONFIG.BASE_URL
  }

  getAuthToken() {
    return localStorage.getItem(API_CONFIG.TOKEN_KEY)
  }

  async handleResponse(response) {
    if (!response.ok) {
      if (response.status === 401) {
        localStorage.removeItem(API_CONFIG.TOKEN_KEY)
        window.location.reload()
      }

      // Попробуем распарсить JSON ошибки, если он есть
      try {
        const errorData = await response.json()
        throw new Error(errorData.detail || errorData.message || `HTTP error! status: ${response.status}`)
      } catch (e) {
        // Если не JSON, выбрасываем статус
        throw new Error(`HTTP error! status: ${response.status}`)
      }
    }
    return response.json()
  }

  async request(endpoint, options = {}) {
    const url = `${this.baseURL}${endpoint}`

    const headers = {
      'Content-Type': 'application/json',
      ...options.headers
    }

    const token = this.getAuthToken()
    if (token) {
      headers['Authorization'] = `Bearer ${token}`
    }

    const config = {
      ...options,
      headers
    }

    try {
      const response = await fetch(url, config)
      return await this.handleResponse(response)
    } catch (error) {
      console.error(`API Error (${endpoint}):`, error)
      throw error
    }
  }

  async upload(endpoint, formData) {
    const url = `${this.baseURL}${endpoint}`

    const headers = {}
    const token = this.getAuthToken()
    if (token) {
      headers['Authorization'] = `Bearer ${token}`
    }

    try {
      const response = await fetch(url, {
        method: 'POST',
        headers,
        body: formData
      })
      return await this.handleResponse(response)
    } catch (error) {
      console.error(`Upload Error (${endpoint}):`, error)
      throw error
    }
  }

  // Auth
  async login(username, password) {
    return this.request('/auth/login', {
      method: 'POST',
      body: JSON.stringify({ username, password })
    })
  }

  async getCurrentUser() {
    return this.request('/auth/me')
  }

  // Dashboard
  async getDashboardStats() {
    return this.request('/dashboard/stats')
  }

  // Products
  async getProducts(params = {}) {
    const queryString = new URLSearchParams(params).toString()
    return this.request(`/products?${queryString}`)
  }

  async getProductsCount(params = {}) {
    const queryString = new URLSearchParams(params).toString()
    return this.request(`/products/count?${queryString}`)
  }

  async getProduct(id) {
    return this.request(`/products/${id}`)
  }

  async createProduct(productData) {
    return this.request('/products', {
      method: 'POST',
      body: JSON.stringify(productData)
    })
  }

  async updateProduct(id, productData) {
    return this.request(`/products/${id}`, {
      method: 'PUT',
      body: JSON.stringify(productData)
    })
  }

  async deleteProduct(id) {
    return this.request(`/products/${id}`, {
      method: 'DELETE'
    })
  }

  async getCategories() {
    return this.request('/products/categories/list')
  }

  async uploadProductImage(file) {
    const formData = new FormData()
    formData.append('file', file)
    return this.upload('/products/upload-image', formData)
  }

  async enrichProduct(id) {
    return this.request(`/products/${id}/enrich`, {
      method: 'POST'
    })
  }

  // Orders
  async getOrders(params = {}) {
    const queryString = new URLSearchParams(params).toString()
    return this.request(`/orders?${queryString}`)
  }

  async getOrdersCount(params = {}) {
    const queryString = new URLSearchParams(params).toString()
    return this.request(`/orders/count?${queryString}`)
  }

  async getOrder(id) {
    return this.request(`/orders/${id}`)
  }

  async updateOrderStatus(id, status) {
    return this.request(`/orders/${id}/status`, {
      method: 'PUT',
      body: JSON.stringify({ status })
    })
  }

  async getOrdersStats() {
    return this.request('/orders/stats/summary')
  }


  async uploadPricelist(file, sheetNames = [], skipDuplicates = true) {
    const formData = new FormData()
    formData.append('file', file)
    formData.append('skip_duplicates', skipDuplicates ? 'true' : 'false')

    if (Array.isArray(sheetNames)) {
      sheetNames.forEach((name) => {
        formData.append('sheet_names', name)
      })
    }

    return this.upload('/upload/pricelist', formData)
  }

  async getAvailableSheets(file) {
    const formData = new FormData()
    formData.append('file', file)
    return this.upload('/upload/pricelist/sheets', formData)
  }
}

export const apiService = new ApiService()