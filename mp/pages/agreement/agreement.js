// pages/agreement/agreement.js
Page({
  data: {
    type: 'user', // 'user' 用户协议, 'privacy' 隐私政策
    title: '用户协议',
    statusBarHeight: 20,
    navBarHeight: 44,
    menuButtonWidth: 87,
    menuButtonTop: 0,
    menuButtonHeight: 32
  },

  onLoad(options) {
    // 获取系统信息和胶囊按钮信息
    const systemInfo = wx.getSystemInfoSync();
    const menuButton = wx.getMenuButtonBoundingClientRect();
    
    this.setData({
      statusBarHeight: systemInfo.statusBarHeight,
      navBarHeight: menuButton.height + (menuButton.top - systemInfo.statusBarHeight) * 2,
      menuButtonWidth: systemInfo.windowWidth - menuButton.left,
      menuButtonTop: menuButton.top,
      menuButtonHeight: menuButton.height
    });
    
    const type = options.type || 'user';
    this.setData({
      type: type,
      title: type === 'privacy' ? '隐私政策' : '用户协议'
    });
  },

  // 返回上一页
  goBack() {
    wx.navigateBack({
      delta: 1,
      fail: () => {
        // 如果没有上一页，跳转到登录页
        wx.redirectTo({
          url: '/pages/login/login'
        });
      }
    });
  }
});