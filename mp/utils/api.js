// API服务模块
const BASE_URL = 'http://8.148.179.255:8000';

// 是否使用云函数代理（设置为 true 使用云函数，false 使用直接请求）
const USE_CLOUD_PROXY = true;

// 云函数请求封装
const cloudRequest = (options) => {
  return new Promise((resolve, reject) => {
    const token = wx.getStorageSync('token');
    
    wx.cloud.callFunction({
      name: 'apiProxy',
      data: {
        url: options.url,
        method: options.method || 'GET',
        data: options.data || {},
        headers: {
          'Content-Type': 'application/json',
          ...(token ? { 'Authorization': `Bearer ${token}` } : {}),
          ...options.header
        }
      },
      success: (res) => {
        console.log('云函数响应:', res);
        
        if (res.result) {
          const { success, statusCode, data, error } = res.result;
          
          if (statusCode >= 200 && statusCode < 300) {
            resolve(data);
          } else if (statusCode === 401) {
            // Token过期或无效，清除登录状态
            wx.removeStorageSync('token');
            wx.removeStorageSync('userInfo');
            wx.showToast({
              title: '登录已过期，请重新登录',
              icon: 'none'
            });
            setTimeout(() => {
              wx.reLaunch({
                url: '/pages/login/login'
              });
            }, 1500);
            reject(new Error('Unauthorized'));
          } else {
            reject(data || { error: error || '请求失败' });
          }
        } else {
          reject(new Error('云函数返回数据异常'));
        }
      },
      fail: (err) => {
        console.error('云函数调用失败:', err);
        wx.showToast({
          title: '网络请求失败',
          icon: 'none'
        });
        reject(err);
      }
    });
  });
};

// 直接请求封装（备用方案，用于开发调试）
const directRequest = (options) => {
  return new Promise((resolve, reject) => {
    const token = wx.getStorageSync('token');
    
    wx.request({
      url: BASE_URL + options.url,
      method: options.method || 'GET',
      data: options.data || {},
      header: {
        'Content-Type': 'application/json',
        ...(token ? { 'Authorization': `Bearer ${token}` } : {}),
        ...options.header
      },
      success: (res) => {
        if (res.statusCode >= 200 && res.statusCode < 300) {
          resolve(res.data);
        } else if (res.statusCode === 401) {
          // Token过期或无效，清除登录状态
          wx.removeStorageSync('token');
          wx.removeStorageSync('userInfo');
          wx.showToast({
            title: '登录已过期，请重新登录',
            icon: 'none'
          });
          setTimeout(() => {
            wx.reLaunch({
              url: '/pages/login/login'
            });
          }, 1500);
          reject(new Error('Unauthorized'));
        } else {
          reject(res.data);
        }
      },
      fail: (err) => {
        wx.showToast({
          title: '网络请求失败',
          icon: 'none'
        });
        reject(err);
      }
    });
  });
};

// 统一请求入口
const request = (options) => {
  if (USE_CLOUD_PROXY) {
    return cloudRequest(options);
  } else {
    return directRequest(options);
  }
};

// 用户相关API
const userApi = {
  // 用户注册
  register: (username, password) => {
    return request({
      url: '/api/user/register',
      method: 'POST',
      data: { username, password }
    });
  },

  // 用户登录
  login: (username, password) => {
    return request({
      url: '/api/user/login',
      method: 'POST',
      data: { username, password }
    });
  },

  // 获取用户信息
  getUserInfo: () => {
    return request({
      url: '/api/user/info',
      method: 'GET'
    });
  }
};

// 抽取美食相关API
const drawApi = {
  // 抽取美食
  // meal_type: 1=早餐, 2=午餐, 3=晚餐, 4=夜宵
  draw: (params = {}) => {
    const queryParams = [];
    if (params.meal_type) queryParams.push(`meal_type=${params.meal_type}`);
    if (params.min_price !== undefined) queryParams.push(`min_price=${params.min_price}`);
    if (params.max_price !== undefined) queryParams.push(`max_price=${params.max_price}`);
    if (params.category) queryParams.push(`category=${encodeURIComponent(params.category)}`);
    
    const queryString = queryParams.length > 0 ? '?' + queryParams.join('&') : '';
    
    return request({
      url: '/api/draw' + queryString,
      method: 'POST'
    });
  },

  // 获取抽取记录
  getRecords: () => {
    return request({
      url: '/api/draw/records',
      method: 'GET'
    });
  }
};

// 健康检查
const healthApi = {
  check: () => {
    return request({
      url: '/health',
      method: 'GET'
    });
  }
};

module.exports = {
  request,
  userApi,
  drawApi,
  healthApi,
  BASE_URL,
  USE_CLOUD_PROXY
};