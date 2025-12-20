// pages/history/history.js
const { drawApi, BASE_URL } = require('../../utils/api');

Page({
  data: {
    // 导航栏相关
    statusBarHeight: 20,
    navBarHeight: 44,
    menuButtonWidth: 87,
    // 数据
    records: [],
    loading: true,
    isEmpty: false,
    // 是否已加载过
    hasLoaded: false
  },

  onLoad() {
    this.getNavBarInfo();
    this.loadRecords();
  },

  onShow() {
    // 只有已经加载过才刷新，避免重复调用
    if (this.data.hasLoaded) {
      this.loadRecords();
    }
  },

  // 下拉刷新
  onPullDownRefresh() {
    this.loadRecords().then(() => {
      wx.stopPullDownRefresh();
    });
  },

  // 获取导航栏信息
  getNavBarInfo() {
    try {
      const systemInfo = wx.getSystemInfoSync();
      const statusBarHeight = systemInfo.statusBarHeight || 20;
      const menuButtonInfo = wx.getMenuButtonBoundingClientRect();
      const navBarHeight = (menuButtonInfo.top - statusBarHeight) * 2 + menuButtonInfo.height;
      const menuButtonWidth = systemInfo.windowWidth - menuButtonInfo.left;
      
      this.setData({
        statusBarHeight,
        navBarHeight,
        menuButtonWidth
      });
    } catch (e) {
      console.error('获取导航栏信息失败', e);
    }
  },

  // 加载抽取记录
  async loadRecords() {
    this.setData({ loading: true });
    
    try {
      const res = await drawApi.getRecords();
      console.log('抽取记录响应:', res);
      
      // 后端返回格式：{code: 0, data: {records: [...]}}
      if (res && res.code === 0 && res.data) {
        // 获取 records 数组，兼容两种格式
        let records = res.data.records || res.data;
        
        // 确保 records 是数组
        if (!Array.isArray(records)) {
          records = [];
        }
        
        // 处理图片URL并格式化时间
        records = records.map(item => {
          if (item.food && item.food.image_url && !item.food.image_url.startsWith('http')) {
            item.food.image_url = BASE_URL + item.food.image_url;
          }
          // 格式化时间
          if (item.drawn_at) {
            item.formattedTime = this.formatTime(item.drawn_at);
          }
          return item;
        });
        
        this.setData({
          records: records,
          loading: false,
          isEmpty: records.length === 0,
          hasLoaded: true
        });
      } else {
        this.setData({
          records: [],
          loading: false,
          isEmpty: true,
          hasLoaded: true
        });
      }
    } catch (e) {
      console.error('获取抽取记录失败', e);
      this.setData({
        records: [],
        loading: false,
        isEmpty: true,
        hasLoaded: true
      });
    }
  },

  // 格式化时间
  formatTime(timeStr) {
    const date = new Date(timeStr);
    const now = new Date();
    const diff = now - date;
    
    // 今天
    if (date.toDateString() === now.toDateString()) {
      const hours = date.getHours().toString().padStart(2, '0');
      const minutes = date.getMinutes().toString().padStart(2, '0');
      return `今天 ${hours}:${minutes}`;
    }
    
    // 昨天
    const yesterday = new Date(now);
    yesterday.setDate(yesterday.getDate() - 1);
    if (date.toDateString() === yesterday.toDateString()) {
      const hours = date.getHours().toString().padStart(2, '0');
      const minutes = date.getMinutes().toString().padStart(2, '0');
      return `昨天 ${hours}:${minutes}`;
    }
    
    // 今年
    if (date.getFullYear() === now.getFullYear()) {
      const month = (date.getMonth() + 1).toString().padStart(2, '0');
      const day = date.getDate().toString().padStart(2, '0');
      const hours = date.getHours().toString().padStart(2, '0');
      const minutes = date.getMinutes().toString().padStart(2, '0');
      return `${month}-${day} ${hours}:${minutes}`;
    }
    
    // 其他
    const year = date.getFullYear();
    const month = (date.getMonth() + 1).toString().padStart(2, '0');
    const day = date.getDate().toString().padStart(2, '0');
    return `${year}-${month}-${day}`;
  },

  // 获取餐类名称
  getMealTypeName(mealType) {
    const names = {
      1: '早餐',
      2: '午餐',
      3: '晚餐',
      4: '夜宵'
    };
    return names[mealType] || '美食';
  },

  // 返回上一页
  goBack() {
    wx.navigateBack();
  },

  // 图片加载失败
  onImageError(e) {
    const index = e.currentTarget.dataset.index;
    const key = `records[${index}].food.image_url`;
    this.setData({
      [key]: '/static/icons/gift.png'
    });
  },

  // 分享
  onShareAppMessage() {
    return {
      title: '吃啥盲盒 - 我的抽选历史',
      path: '/pages/login/login'
    };
  }
});