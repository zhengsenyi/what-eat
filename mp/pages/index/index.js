// pages/index/index.js
const app = getApp();

Page({
  data: {
    scenes: [
      { id: 'breakfast', name: '早餐', icon: '🌅' },
      { id: 'lunch', name: '午餐', icon: '☀️' },
      { id: 'dinner', name: '晚餐', icon: '🌙' },
      { id: 'supper', name: '夜宵', icon: '🌃' }
    ],
    selectedScene: 'lunch',
    // 预算范围
    budgetMin: 20,
    budgetMax: 80,
    minValue: 0,
    maxValue: 200,
    // 滑块位置百分比
    rangeLeft: 10,
    rangeRight: 40,
    rangeWidth: 30,
    // 状态
    isShaking: false,
    isPressed: false,
    statusBarHeight: 20,
    navBarHeight: 44,
    // 滑块相关
    sliderWidth: 0,
    sliderLeft: 0,
    activeThumb: null
  },

  onLoad() {
    // 获取系统信息，适配胶囊
    this.getNavBarInfo();
    
    // 检查登录状态
    const userInfo = wx.getStorageSync('userInfo');
    if (!userInfo) {
      wx.redirectTo({
        url: '/pages/login/login'
      });
      return;
    }

    // 初始化滑块位置
    this.initSliderPosition();
  },

  onReady() {
    // 获取滑块容器信息
    this.getSliderInfo();
  },

  // 获取导航栏信息
  getNavBarInfo() {
    try {
      const systemInfo = wx.getSystemInfoSync();
      const statusBarHeight = systemInfo.statusBarHeight || 20;
      const menuButtonInfo = wx.getMenuButtonBoundingClientRect();
      const navBarHeight = (menuButtonInfo.top - statusBarHeight) * 2 + menuButtonInfo.height;
      
      this.setData({
        statusBarHeight: statusBarHeight,
        navBarHeight: navBarHeight
      });
    } catch (e) {
      console.error('获取导航栏信息失败', e);
    }
  },

  // 获取滑块容器信息
  getSliderInfo() {
    const query = wx.createSelectorQuery();
    query.select('.range-slider').boundingClientRect((rect) => {
      if (rect) {
        this.sliderWidth = rect.width;
        this.sliderLeft = rect.left;
      }
    }).exec();
  },

  // 初始化滑块位置
  initSliderPosition() {
    const { budgetMin, budgetMax, minValue, maxValue } = this.data;
    const rangeLeft = ((budgetMin - minValue) / (maxValue - minValue)) * 100;
    const rangeRight = ((budgetMax - minValue) / (maxValue - minValue)) * 100;
    const rangeWidth = rangeRight - rangeLeft;
    
    this.setData({
      rangeLeft,
      rangeRight,
      rangeWidth
    });
  },

  // 滑块触摸开始
  onSliderTouchStart(e) {
    if (!this.sliderWidth) {
      this.getSliderInfo();
    }
    
    const touch = e.touches[0];
    const touchX = touch.clientX - this.sliderLeft;
    const percent = (touchX / this.sliderWidth) * 100;
    
    const { rangeLeft, rangeRight } = this.data;
    
    // 判断触摸的是左滑块还是右滑块
    const distToLeft = Math.abs(percent - rangeLeft);
    const distToRight = Math.abs(percent - rangeRight);
    
    if (distToLeft < distToRight) {
      this.activeThumb = 'left';
    } else {
      this.activeThumb = 'right';
    }
    
    wx.vibrateShort({ type: 'light' });
  },

  // 滑块触摸移动
  onSliderTouchMove(e) {
    if (!this.activeThumb || !this.sliderWidth) return;
    
    const touch = e.touches[0];
    const touchX = touch.clientX - this.sliderLeft;
    let percent = (touchX / this.sliderWidth) * 100;
    
    // 限制范围
    percent = Math.max(0, Math.min(100, percent));
    
    const { minValue, maxValue } = this.data;
    let { rangeLeft, rangeRight } = this.data;
    
    if (this.activeThumb === 'left') {
      // 左滑块不能超过右滑块
      rangeLeft = Math.min(percent, rangeRight - 5);
      rangeLeft = Math.max(0, rangeLeft);
    } else {
      // 右滑块不能低于左滑块
      rangeRight = Math.max(percent, rangeLeft + 5);
      rangeRight = Math.min(100, rangeRight);
    }
    
    const rangeWidth = rangeRight - rangeLeft;
    
    // 计算实际预算值
    const budgetMin = Math.round((rangeLeft / 100) * (maxValue - minValue) + minValue);
    const budgetMax = Math.round((rangeRight / 100) * (maxValue - minValue) + minValue);
    
    this.setData({
      rangeLeft,
      rangeRight,
      rangeWidth,
      budgetMin,
      budgetMax
    });
  },

  // 滑块触摸结束
  onSliderTouchEnd() {
    this.activeThumb = null;
  },

  // 选择场景
  selectScene(e) {
    const id = e.currentTarget.dataset.id;
    wx.vibrateShort({ type: 'light' });
    this.setData({ selectedScene: id });
  },

  // 盲盒按下
  onBoxTouchStart() {
    this.setData({ isPressed: true });
  },

  // 盲盒松开
  onBoxTouchEnd() {
    this.setData({ isPressed: false });
  },

  // 开始抽选
  startDraw() {
    if (this.data.isShaking) return;

    wx.vibrateShort({ type: 'medium' });
    this.setData({ isShaking: true });

    wx.showLoading({
      title: '正在抽选...',
      mask: true
    });

    setTimeout(() => {
      wx.hideLoading();
      
      const stats = wx.getStorageSync('userStats') || {
        favoriteCount: 0,
        totalDraws: 0
      };
      stats.totalDraws += 1;
      wx.setStorageSync('userStats', stats);

      this.setData({ isShaking: false });

      wx.navigateTo({
        url: `/pages/result/result?scene=${this.data.selectedScene}&budgetMin=${this.data.budgetMin}&budgetMax=${this.data.budgetMax}`,
      });
    }, 1200);
  },

  // 分享
  onShareAppMessage() {
    return {
      title: '吃啥盲盒 - 解决你的选择困难症！',
      path: '/pages/login/login'
    };
  },

  onShareTimeline() {
    return {
      title: '吃啥盲盒 - 解决你的选择困难症！',
      query: ''
    };
  }
});
