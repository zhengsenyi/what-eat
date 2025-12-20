// 云函数入口文件
const cloud = require('wx-server-sdk');
const axios = require('axios');

cloud.init({
  env: cloud.DYNAMIC_CURRENT_ENV
});

// 目标服务器地址
const TARGET_URL = 'http://8.148.179.255:8000';

// 云函数入口函数
exports.main = async (event, context) => {
  const { url, method = 'GET', data = {}, headers = {} } = event;
  
  console.log('收到请求:', { url, method, data });
  
  try {
    const config = {
      url: TARGET_URL + url,
      method: method.toUpperCase(),
      headers: {
        'Content-Type': 'application/json',
        ...headers
      },
      timeout: 30000
    };
    
    // GET 请求使用 params，其他请求使用 data
    if (method.toUpperCase() === 'GET') {
      config.params = data;
    } else {
      config.data = data;
    }
    
    console.log('转发请求配置:', config);
    
    const response = await axios(config);
    
    console.log('响应状态:', response.status);
    console.log('响应数据:', response.data);
    
    return {
      success: true,
      statusCode: response.status,
      data: response.data
    };
  } catch (error) {
    console.error('请求失败:', error.message);
    
    // 如果有响应，返回响应数据
    if (error.response) {
      return {
        success: false,
        statusCode: error.response.status,
        data: error.response.data,
        error: error.message
      };
    }
    
    // 网络错误等
    return {
      success: false,
      statusCode: 500,
      data: null,
      error: error.message
    };
  }
};