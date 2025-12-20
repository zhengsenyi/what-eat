// pages/result/result.js
const { drawApi } = require('../../utils/api');

Page({
  data: {
    // 导航栏相关
    statusBarHeight: 20,
    navBarHeight: 44,
    menuButtonWidth: 87,
    // 抽取结果
    result: {
      id: 0,
      name: '',
      category: '',
      meal_type: null,
      description: '',
      price: '',
      image_url: ''
    },
    // 相似推荐（暂时为空，后端暂无此接口）
    similarItems: [],
    isFavorite: false,
    remainingTimes: 0
  },

  onLoad(options) {
    // 获取导航栏信息
    this.getNavBarInfo();
    
    // 获取传递的参数
    if (options.foodData) {
      try {
        const foodData = JSON.parse(decodeURIComponent(options.foodData));
        this.setData({
          result: {
            id: foodData.id,
            name: foodData.name,
            category: foodData.category || '美食',
            meal_type: foodData.meal_type,
            description: foodData.description || '这是一道美味的菜品，值得一试！',
            price: foodData.price || '未知',
            image_url: foodData.image_url || ''
          }
        });
      } catch (e) {
        console.error('解析食物数据失败', e);
      }
    }

    if (options.remainingTimes) {
      this.setData({
        remainingTimes: parseInt(options.remainingTimes)
      });
    }

    // 检查是否已收藏
    this.checkFavorite();
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

  // 检查是否已收藏
  checkFavorite() {
    const favorites = wx.getStorageSync('favorites') || [];
    const isFavorite = favorites.some(item => item.id === this.data.result.id);
    this.setData({ isFavorite });
  },

  // 返回上一页
  goBack() {
    wx.navigateBack();
  },

  // 重新抽选
  async reRoll() {
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

    wx.vibrateShort({ type: 'medium' });
    
    wx.showLoading({
      title: '重新抽选中...',
      mask: true
    });

    try {
      // 获取当前场景的meal_type
      const result = await drawApi.draw({});

      wx.hideLoading();

      if (result.success && result.food) {
        this.setData({
          result: {
            id: result.food.id,
            name: result.food.name,
            category: result.food.category || '美食',
            meal_type: result.food.meal_type,
            description: result.food.description || '这是一道美味的菜品，值得一试！',
            price: result.food.price || '未知',
            image_url: result.food.image_url || ''
          },
          remainingTimes: result.remaining_times
        });

        // 检查新结果的收藏状态
        this.checkFavorite();

        wx.showToast({
          title: '换了一个推荐',
          icon: 'none'
        });
      } else {
        wx.showToast({
          title: result.message || '抽取失败',
          icon: 'none'
        });
      }

    } catch (err) {
      wx.hideLoading();
      console.error('重新抽选失败', err);
      wx.showToast({
        title: err.detail || '抽取失败，请重试',
        icon: 'none'
      });
    }
  },

  // 切换收藏状态
  toggleFavorite() {
    wx.vibrateShort({ type: 'light' });
    
    const favorites = wx.getStorageSync('favorites') || [];
    const { result, isFavorite } = this.data;

    if (isFavorite) {
      const newFavorites = favorites.filter(item => item.id !== result.id);
      wx.setStorageSync('favorites', newFavorites);
      
      this.setData({ isFavorite: false });
      
      wx.showToast({
        title: '已取消收藏',
        icon: 'none'
      });
    } else {
      favorites.push({
        id: result.id,
        name: result.name,
        category: result.category,
        price: result.price,
        image_url: result.image_url,
        addTime: new Date().toISOString()
      });
      wx.setStorageSync('favorites', favorites);
      
      this.setData({ isFavorite: true });
      
      wx.showToast({
        title: '已添加到收藏',
        icon: 'success'
      });
    }
  },

  // 打开导航
  openNavigation() {
    wx.showActionSheet({
      itemList: ['高德地图', '百度地图', '腾讯地图'],
      success: (res) => {
        wx.showToast({
          title: '正在打开导航...',
          icon: 'none'
        });
      }
    });
  },

  // 分享
  onShare() {
    wx.showShareMenu({
      withShareTicket: true,
      menus: ['shareAppMessage', 'shareTimeline']
    });
  },

  // 选择相似推荐
  selectSimilar(e) {
    const item = e.currentTarget.dataset.item;
    
    wx.vibrateShort({ type: 'light' });
    
    this.setData({
      result: {
        id: item.id,
        name: item.name,
        category: item.category || '美食',
        meal_type: item.meal_type,
        description: item.description || '这是一道美味的菜品，值得一试！',
        price: item.price || '未知',
        image_url: item.image_url || ''
      }
    });

    this.checkFavorite();

    wx.pageScrollTo({
      scrollTop: 0,
      duration: 300
    });
  },

  // 确认选择
  confirmChoice() {
    wx.vibrateShort({ type: 'medium' });
    
    const { result } = this.data;
    
    // 保存到本地历史记录
    const history = wx.getStorageSync('drawHistory') || [];
    const newHistory = [
      {
        id: result.id,
        name: result.name,
        category: result.category,
        price: result.price,
        image_url: result.image_url,
        drawTime: new Date().toISOString()
      },
      ...history.filter(item => item.id !== result.id)
    ].slice(0, 20);
    
    wx.setStorageSync('drawHistory', newHistory);

    wx.showModal({
      title: '选择成功！',
      content: `已选择「${result.name}」\n祝您用餐愉快！🎉`,
      showCancel: false,
      confirmText: '好的',
      confirmColor: '#84cc16',
      success: () => {
        wx.navigateBack();
      }
    });
  },

  // 分享给朋友
  onShareAppMessage() {
    const { result } = this.data;
    return {
      title: `我在吃啥盲盒抽到了「${result.name}」，你也来试试！`,
      path: '/pages/login/login',
      imageUrl: result.image_url
    };
  },

  // 分享到朋友圈
  onShareTimeline() {
    const { result } = this.data;
    return {
      title: `吃啥盲盒推荐：${result.name}`,
      query: ''
    };
  }
});
