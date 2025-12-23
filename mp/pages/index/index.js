// pages/index/index.js
const { drawApi, userApi, BASE_URL } = require('../../utils/api');

Page({
  data: {
    scenes: [
      { id: 'breakfast', name: '早餐', icon: '🌅', mealType: 1 },
      { id: 'lunch', name: '午餐', icon: '☀️', mealType: 2 },
      { id: 'dinner', name: '晚餐', icon: '🌙', mealType: 3 },
      { id: 'supper', name: '夜宵', icon: '🌃', mealType: 4 }
    ],
    selectedScene: '',
    selectedMealType: 2,
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
    isOpening: false,
    showResult: false,
    resultAnimating: false,
    statusBarHeight: 20,
    navBarHeight: 44,
    menuButtonWidth: 87,
    menuButtonHeight: 32,
    // 用户信息
    remainingTimes: 3,
    // 滑块相关
    sliderWidth: 0,
    sliderLeft: 0,
    activeThumb: null,
    // 抽奖结果
    foodResult: null
  },

  onLoad() {
    // 获取系统信息，适配胶囊
    this.getNavBarInfo();
    
    // 检查登录状态
    const token = wx.getStorageSync('token');
    if (!token) {
      wx.reLaunch({
        url: '/pages/login/login'
      });
      return;
    }

    // 根据当前时间自动选择用餐场景
    this.autoSelectScene();

    // 初始化滑块位置
    this.initSliderPosition();

    // 获取用户信息
    this.fetchUserInfo();
  },

  onShow() {
    // 每次显示页面时重新判断用餐场景
    this.autoSelectScene();
    // 刷新用户信息
    this.fetchUserInfo();
  },

  onReady() {
    // 获取滑块容器信息
    this.getSliderInfo();
  },

  // 获取用户信息
  async fetchUserInfo() {
    try {
      const res = await userApi.getUserInfo();
      // 后端返回格式：{code: 0, data: {id, username, created_at, today_remaining_times}}
      if (res && res.code === 0 && res.data) {
        const userInfo = res.data;
        this.setData({
          remainingTimes: userInfo.today_remaining_times
        });
        // 更新本地存储
        const localUserInfo = wx.getStorageSync('userInfo') || {};
        localUserInfo.remainingTimes = userInfo.today_remaining_times;
        wx.setStorageSync('userInfo', localUserInfo);
      }
    } catch (e) {
      console.error('获取用户信息失败', e);
    }
  },

  // 根据当前北京时间自动选择用餐场景
  autoSelectScene() {
    const now = new Date();
    const utc = now.getTime() + (now.getTimezoneOffset() * 60000);
    const beijingTime = new Date(utc + (8 * 3600000));
    const currentHour = beijingTime.getHours();
    
    let selectedScene = 'lunch';
    let selectedMealType = 2;
    
    if (currentHour >= 6 && currentHour < 10) {
      selectedScene = 'breakfast';
      selectedMealType = 1;
    } else if (currentHour >= 10 && currentHour < 14) {
      selectedScene = 'lunch';
      selectedMealType = 2;
    } else if (currentHour >= 14 && currentHour < 17) {
      selectedScene = 'dinner';
      selectedMealType = 3;
    } else if (currentHour >= 17 && currentHour < 21) {
      selectedScene = 'dinner';
      selectedMealType = 3;
    } else {
      selectedScene = 'supper';
      selectedMealType = 4;
    }
    
    this.setData({ selectedScene, selectedMealType });
  },

  // 获取导航栏信息
  getNavBarInfo() {
    try {
      const systemInfo = wx.getSystemInfoSync();
      const statusBarHeight = systemInfo.statusBarHeight || 20;
      const menuButtonInfo = wx.getMenuButtonBoundingClientRect();
      const navBarHeight = (menuButtonInfo.top - statusBarHeight) * 2 + menuButtonInfo.height;
      const menuButtonWidth = systemInfo.windowWidth - menuButtonInfo.left;
      const menuButtonHeight = menuButtonInfo.height;
      
      this.setData({
        statusBarHeight,
        navBarHeight,
        menuButtonWidth,
        menuButtonHeight
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
    
    percent = Math.max(0, Math.min(100, percent));
    
    const { minValue, maxValue } = this.data;
    let { rangeLeft, rangeRight } = this.data;
    
    if (this.activeThumb === 'left') {
      rangeLeft = Math.min(percent, rangeRight - 5);
      rangeLeft = Math.max(0, rangeLeft);
    } else {
      rangeRight = Math.max(percent, rangeLeft + 5);
      rangeRight = Math.min(100, rangeRight);
    }
    
    const rangeWidth = rangeRight - rangeLeft;
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
    const scene = this.data.scenes.find(s => s.id === id);
    
    wx.vibrateShort({ type: 'light' });
    
    this.setData({ 
      selectedScene: id,
      selectedMealType: scene ? scene.mealType : 2
    });
  },

  // 盲盒按下
  onBoxTouchStart() {
    this.setData({ isPressed: true });
  },

  // 盲盒松开
  onBoxTouchEnd() {
    this.setData({ isPressed: false });
  },

  // 阻止触摸滚动
  preventTouchMove() {
    return false;
  },

  // 开始抽选
  async startDraw() {
    if (this.data.isShaking || this.data.showResult) return;

    // 检查剩余次数
    if (this.data.remainingTimes <= 0) {
      wx.showModal({
        title: '次数用完啦',
        content: '今日免费抽取次数已用完，明天再来吧！',
        showCancel: false,
        confirmText: '知道了'
      });
      return;
    }

    // 立即开始动画效果
    wx.vibrateShort({ type: 'medium' });
    this.setData({ isShaking: true });
    
    // 记录动画开始时间
    const animationStartTime = Date.now();
    const minAnimationDuration = 2000; // 最少动画时间2秒

    try {
      const { selectedMealType, budgetMin, budgetMax } = this.data;
      
      // 发起API请求
      const res = await drawApi.draw({
        meal_type: selectedMealType,
        min_price: budgetMin,
        max_price: budgetMax
      });

      // 后端返回格式：{code: 0, msg: "...", data: {food: {...}, remaining_times: 1}}
      console.log('抽取响应:', res);
      if (res && res.code === 0 && res.data && res.data.food) {
        const result = res.data;
        const food = result.food;
        
        // 处理图片URL
        if (food.image_url && !food.image_url.startsWith('http')) {
          food.image_url = BASE_URL + food.image_url;
        }
        
        // 计算剩余需要等待的动画时间
        const elapsedTime = Date.now() - animationStartTime;
        const remainingAnimationTime = Math.max(0, minAnimationDuration - elapsedTime);
        
        // 等待动画完成后显示结果
        setTimeout(() => {
          // 开盒动画
          this.setData({ isOpening: true });
          
          // 震动反馈
          wx.vibrateShort({ type: 'heavy' });
          
          // 显示结果
          setTimeout(() => {
            this.setData({
              isShaking: false,
              isOpening: false,
              showResult: true,
              foodResult: food,
              remainingTimes: result.remaining_times
            });
            
            // 更新本地存储的剩余次数
            const localUserInfo = wx.getStorageSync('userInfo') || {};
            localUserInfo.remainingTimes = result.remaining_times;
            wx.setStorageSync('userInfo', localUserInfo);
            
            // 触发结果卡片动画
            setTimeout(() => {
              this.setData({ resultAnimating: true });
            }, 50);
          }, 500);
        }, remainingAnimationTime);
        
      } else {
        // 抽取失败，停止动画
        this.setData({ isShaking: false });
        // 静默失败，不显示提示
        console.error('抽取失败:', res);
      }

    } catch (err) {
      this.setData({ isShaking: false });
      console.error('抽取失败', err);
      // 静默失败，不显示提示
    }
  },

  // 重置抽奖，再抽一次
  resetDraw() {
    this.setData({
      showResult: false,
      resultAnimating: false,
      foodResult: null
    });
  },

  // 接受结果
  acceptResult() {
    wx.showToast({
      title: '好的，就吃这个！',
      icon: 'success',
      duration: 1500
    });
    
    // 可以跳转到详情页或其他操作
    setTimeout(() => {
      this.resetDraw();
    }, 1500);
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

  // 图片加载失败处理
  onImageError(e) {
    console.error('图片加载失败', e);
    // 可以设置默认图片
    this.setData({
      'foodResult.image_url': '/static/icons/gift.png'
    });
  },

  // 分享
  onShareAppMessage() {
    return {
      title: '选餐侠 - 解决你的选择困难症！',
      path: '/pages/login/login'
    };
  },

  onShareTimeline() {
    return {
      title: '选餐侠 - 解决你的选择困难症！',
      query: ''
    };
  }
});
