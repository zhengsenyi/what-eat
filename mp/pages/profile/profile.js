// pages/profile/profile.js
Page({
  data: {
    userInfo: {
      nickName: '美食探索家',
      avatarText: '👤',
      level: '黄金会员'
    },
    stats: {
      monthlyDraws: 12,
      newTries: 7,
      newTriesThisWeek: 3,
      favorites: 5,
      drawTrend: 15
    },
    currentMonth: '',
    version: '1.0.0',
    cacheSize: '计算中...'
  },

  onLoad() {
    this.loadUserInfo();
    this.loadStats();
    this.setCurrentMonth();
    this.calculateCacheSize();
  },

  onShow() {
    // 每次显示页面时刷新数据
    this.loadStats();
    this.calculateCacheSize();
  },

  // 加载用户信息
  loadUserInfo() {
    const userInfo = wx.getStorageSync('userInfo');
    if (userInfo) {
      this.setData({
        userInfo: {
          nickName: userInfo.nickName || '美食探索家',
          avatarText: userInfo.avatarText || '👤',
          level: userInfo.level || '黄金会员'
        }
      });
    }
  },

  // 加载统计数据
  loadStats() {
    const stats = wx.getStorageSync('userStats') || {};
    const favorites = wx.getStorageSync('favorites') || [];
    const history = wx.getStorageSync('drawHistory') || [];
    
    // 计算本月抽选次数
    const now = new Date();
    const monthStart = new Date(now.getFullYear(), now.getMonth(), 1);
    const monthlyDraws = history.filter(item => {
      const drawDate = new Date(item.drawTime);
      return drawDate >= monthStart;
    }).length;

    // 计算新尝试（去重的餐厅数量）
    const uniqueRestaurants = new Set(history.map(item => item.restaurant || item.name));
    
    this.setData({
      stats: {
        monthlyDraws: monthlyDraws || stats.totalDraws || 12,
        newTries: uniqueRestaurants.size || 7,
        newTriesThisWeek: 3,
        favorites: favorites.length || stats.favoriteCount || 5,
        drawTrend: 15
      }
    });
  },

  // 设置当前月份
  setCurrentMonth() {
    const now = new Date();
    const month = now.getMonth() + 1;
    this.setData({
      currentMonth: `${now.getFullYear()}年${month}月`
    });
  },

  // 计算缓存大小
  calculateCacheSize() {
    try {
      const res = wx.getStorageInfoSync();
      const usedSize = res.currentSize; // KB
      let sizeText = '';
      
      if (usedSize < 1024) {
        sizeText = `${usedSize} KB`;
      } else {
        sizeText = `${(usedSize / 1024).toFixed(2)} MB`;
      }
      
      this.setData({ cacheSize: sizeText });
    } catch (e) {
      this.setData({ cacheSize: '未知' });
    }
  },

  // 打开设置
  openSettings() {
    wx.showToast({
      title: '功能开发中',
      icon: 'none'
    });
  },

  // 编辑个人资料
  editProfile() {
    wx.showActionSheet({
      itemList: ['修改昵称', '修改头像'],
      success: (res) => {
        if (res.tapIndex === 0) {
          this.editNickname();
        } else if (res.tapIndex === 1) {
          this.editAvatar();
        }
      }
    });
  },

  // 修改昵称
  editNickname() {
    wx.showModal({
      title: '修改昵称',
      editable: true,
      placeholderText: '请输入新昵称',
      success: (res) => {
        if (res.confirm && res.content) {
          const userInfo = wx.getStorageSync('userInfo') || {};
          userInfo.nickName = res.content;
          wx.setStorageSync('userInfo', userInfo);
          
          this.setData({
            'userInfo.nickName': res.content
          });
          
          wx.showToast({
            title: '修改成功',
            icon: 'success'
          });
        }
      }
    });
  },

  // 修改头像
  editAvatar() {
    const avatars = ['👤', '😊', '🤗', '😎', '🥳', '🤩', '😋', '🍜'];
    wx.showActionSheet({
      itemList: avatars,
      success: (res) => {
        const userInfo = wx.getStorageSync('userInfo') || {};
        userInfo.avatarText = avatars[res.tapIndex];
        wx.setStorageSync('userInfo', userInfo);
        
        this.setData({
          'userInfo.avatarText': avatars[res.tapIndex]
        });
        
        wx.showToast({
          title: '修改成功',
          icon: 'success'
        });
      }
    });
  },

  // 查看抽选历史
  viewDrawHistory() {
    wx.showToast({
      title: '功能开发中',
      icon: 'none'
    });
  },

  // 查看新尝试
  viewNewTries() {
    wx.showToast({
      title: '功能开发中',
      icon: 'none'
    });
  },

  // 查看收藏
  viewFavorites() {
    this.goToFavorites();
  },

  // 跳转到收藏页
  goToFavorites() {
    wx.showToast({
      title: '功能开发中',
      icon: 'none'
    });
  },

  // 跳转到历史页
  goToHistory() {
    wx.showToast({
      title: '功能开发中',
      icon: 'none'
    });
  },

  // 跳转到偏好设置
  goToPreferences() {
    wx.showToast({
      title: '功能开发中',
      icon: 'none'
    });
  },

  // 跳转到意见反馈
  goToFeedback() {
    wx.showModal({
      title: '意见反馈',
      content: '如有问题或建议，请联系我们：\nfeedback@chisha.com',
      showCancel: false,
      confirmText: '知道了'
    });
  },

  // 跳转到关于我们
  goToAbout() {
    wx.showModal({
      title: '关于吃啥盲盒',
      content: '版本：1.0.0\n\n吃啥盲盒是一款帮助你解决"今天吃什么"难题的小程序。\n\n让美食选择变得有趣又简单！',
      showCancel: false,
      confirmText: '知道了'
    });
  },

  // 清除缓存
  clearCache() {
    wx.showModal({
      title: '清除缓存',
      content: '确定要清除所有缓存数据吗？这将清除历史记录和收藏，但不会影响登录状态。',
      confirmText: '确定清除',
      confirmColor: '#ef4444',
      success: (res) => {
        if (res.confirm) {
          // 保留用户信息
          const userInfo = wx.getStorageSync('userInfo');
          
          // 清除所有存储
          wx.clearStorageSync();
          
          // 恢复用户信息
          if (userInfo) {
            wx.setStorageSync('userInfo', userInfo);
          }
          
          // 刷新数据
          this.loadStats();
          this.calculateCacheSize();
          
          wx.showToast({
            title: '清除成功',
            icon: 'success'
          });
        }
      }
    });
  },

  // 退出登录
  logout() {
    wx.showModal({
      title: '退出登录',
      content: '确定要退出登录吗？',
      confirmText: '退出',
      confirmColor: '#ef4444',
      success: (res) => {
        if (res.confirm) {
          // 清除用户信息
          wx.removeStorageSync('userInfo');
          
          wx.showToast({
            title: '已退出登录',
            icon: 'none',
            duration: 1500
          });
          
          // 跳转到登录页
          setTimeout(() => {
            wx.reLaunch({
              url: '/pages/login/login'
            });
          }, 1500);
        }
      }
    });
  },

  // 分享
  onShareAppMessage() {
    return {
      title: '吃啥盲盒 - 解决你的选择困难症！',
      path: '/pages/login/login'
    };
  }
});
