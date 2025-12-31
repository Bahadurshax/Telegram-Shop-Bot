const API_BASE_URL = '/admin/api'

class ApiService {
  constructor() {
    this.baseURL = API_BASE_URL
  }

  getHeaders() {
    const token = localStorage.getItem('admin_token')
    return {
      'Content-Type': 'application/json',
      ...(token && { 'Authorization': `Bearer ${token}` })
    }
  }

  async request(endpoint, options = {}) {
    const url = `${this.baseURL}${endpoint}`
    const config = {
      headers: this.getHeaders(),
      ...options
    }

    try {
      const response = await fetch(url, config)
      
      if (!response.ok) {
        if (response.status === 401) {
          localStorage.removeItem('admin_token')
          window.location.reload()
        }
        throw new Error(`HTTP error! status: ${response.status}`)
      }

      return await response.json()
    } catch (error) {
      console.error('API Error:', error)
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

  // Upload
  async uploadImages(files) {
    const formData = new FormData()

    // Добавляем файлы в FormData
    for (let i = 0; i < files.length; i++) {
      formData.append('files', files[i])
    }

    const token = localStorage.getItem('admin_token')

    return fetch(`${this.baseURL}/upload/images`, {
      method: 'POST',
      headers: {
        ...(token && { 'Authorization': `Bearer ${token}` })
      },
      body: formData
    }).then(response => {
      if (!response.ok) {
        if (response.status === 401) {
          localStorage.removeItem('admin_token')
          window.location.reload()
        }
        throw new Error(`HTTP error! status: ${response.status}`)
      }
      return response.json()
    })
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

    const token = localStorage.getItem('admin_token')

    return fetch(`${this.baseURL}/upload/pricelist`, {
      method: 'POST',
      headers: {
        ...(token && { Authorization: `Bearer ${token}` })
      },
      body: formData
    }).then(response => {
      if (!response.ok) {
        if (response.status === 401) {
          localStorage.removeItem('admin_token')
          window.location.reload()
        }
        throw new Error(`HTTP error! status: ${response.status}`)
      }
      return response.json()
    })
  }

  async getAvailableSheets(file) {
    const formData = new FormData()
    formData.append('file', file)

    const token = localStorage.getItem('admin_token')

    return fetch(`${this.baseURL}/upload/pricelist/sheets`, {
      method: 'POST',
      headers: {
        ...(token && { Authorization: `Bearer ${token}` })
      },
      body: formData
    }).then(response => {
      if (!response.ok) {
        if (response.status === 401) {
          localStorage.removeItem('admin_token')
          window.location.reload()
        }
        throw new Error(`HTTP error! status: ${response.status}`)
      }
      return response.json()
    })
  }
}

export const apiService = new ApiService()