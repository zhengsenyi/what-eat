// app.js
App({
  globalData: {
    userInfo: null,
    systemInfo: null,
    statusBarHeight: 0,
    navBarHeight: 44,
    menuButtonInfo: null
  },

  onLaunch() {
    // 获取系统信息
    this.getSystemInfo();
    
    // 获取胶囊按钮信息
    this.getMenuButtonInfo();
    
    // 检查更新
    this.checkUpdate();
    
    // 初始化用户数据
    this.initUserData();
  },

  // 获取系统信息
  getSystemInfo() {
    try {
      const systemInfo = wx.getSystemInfoSync();
      this.globalData.systemInfo = systemInfo;
      this.globalData.statusBarHeight = systemInfo.statusBarHeight || 20;
    } catch (e) {
      console.error('获取系统信息失败', e);
    }
  },

  // 获取胶囊按钮信息
  getMenuButtonInfo() {
    try {
      const menuButtonInfo = wx.getMenuButtonBoundingClientRect();
      this.globalData.menuButtonInfo = menuButtonInfo;
      
      // 计算导航栏高度
      const navBarHeight = (menuButtonInfo.top - this.globalData.statusBarHeight) * 2 + menuButtonInfo.height;
      this.globalData.navBarHeight = navBarHeight;
    } catch (e) {
      console.error('获取胶囊按钮信息失败', e);
    }
  },

  // 检查更新
  checkUpdate() {
    if (wx.canIUse('getUpdateManager')) {
      const updateManager = wx.getUpdateManager();
      
      updateManager.onCheckForUpdate((res) => {
        if (res.hasUpdate) {
          console.log('发现新版本');
        }
      });

      updateManager.onUpdateReady(() => {
        wx.showModal({
          title: '更新提示',
          content: '新版本已经准备好，是否重启应用？',
          confirmText: '立即更新',
          cancelText: '稍后更新',
          success: (res) => {
            if (res.confirm) {
              updateManager.applyUpdate();
            }
          }
        });
      });

      updateManager.onUpdateFailed(() => {
        wx.showToast({
          title: '更新失败，请稍后重试',
          icon: 'none'
        });
      });
    }
  },

  // 初始化用户数据
  initUserData() {
    // 检查是否有用户信息
    const userInfo = wx.getStorageSync('userInfo');
    if (userInfo) {
      this.globalData.userInfo = userInfo;
    }

    // 初始化统计数据
    const stats = wx.getStorageSync('userStats');
    if (!stats) {
      wx.setStorageSync('userStats', {
        favoriteCount: 0,
        totalDraws: 0
      });
    }

    // 初始化收藏列表
    const favorites = wx.getStorageSync('favorites');
    if (!favorites) {
      wx.setStorageSync('favorites', []);
    }

    // 初始化历史记录
    const history = wx.getStorageSync('drawHistory');
    if (!history) {
      wx.setStorageSync('drawHistory', []);
    }
  },

  // 设置用户信息
  setUserInfo(userInfo) {
    this.globalData.userInfo = userInfo;
    wx.setStorageSync('userInfo', userInfo);
  },

  // 获取用户信息
  getUserInfo() {
    return this.globalData.userInfo || wx.getStorageSync('userInfo');
  },

  // 检查登录状态
  checkLogin() {
    const userInfo = this.getUserInfo();
    return !!userInfo;
  },

  // 退出登录
  logout() {
    this.globalData.userInfo = null;
    wx.removeStorageSync('userInfo');
  }
});
