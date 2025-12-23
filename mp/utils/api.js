// API服务模块
// 由于域名未完成ICP备案，暂时使用IP地址
// 备案完成后请改回域名: http://zhengsenyi.xyz:8000
const BASE_URL = 'http://120.24.24.166:8000';

// HTTP请求封装
const request = (options) => {
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
  },

  // 微信授权登录
  wechatLogin: (code) => {
    return request({
      url: '/api/user/wechat/login',
      method: 'POST',
      data: { code }
    });
  },

  // 更新微信用户信息
  updateWechatUserInfo: (nickname, avatarUrl) => {
    return request({
      url: '/api/user/wechat/userinfo',
      method: 'PUT',
      data: {
        nickname: nickname,
        avatar_url: avatarUrl
      }
    });
  },

  // 上传头像
  uploadAvatar: (filePath) => {
    return new Promise((resolve, reject) => {
      const token = wx.getStorageSync('token');
      
      wx.uploadFile({
        url: BASE_URL + '/api/user/avatar/upload',
        filePath: filePath,
        name: 'file',
        header: {
          'Authorization': `Bearer ${token}`
        },
        success: (res) => {
          if (res.statusCode >= 200 && res.statusCode < 300) {
            try {
              const data = JSON.parse(res.data);
              resolve(data);
            } catch (e) {
              reject(new Error('解析响应失败'));
            }
          } else if (res.statusCode === 401) {
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
            try {
              const data = JSON.parse(res.data);
              reject(data);
            } catch (e) {
              reject(new Error('上传失败'));
            }
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
  BASE_URL
};