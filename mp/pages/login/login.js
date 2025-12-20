// pages/login/login.js
Page({
  data: {
    isLoading: false
  },

  onLoad() {
    // 检查是否已登录
    const userInfo = wx.getStorageSync('userInfo');
    if (userInfo) {
      this.navigateToIndex();
    }
  },

  // 微信登录
  onLogin() {
    if (this.data.isLoading) return;
    
    this.setData({ isLoading: true });
    
    // 显示加载提示
    wx.showLoading({
      title: '登录中...',
      mask: true
    });

    // 模拟登录过程
    setTimeout(() => {
      // 模拟保存用户信息
      const userInfo = {
        nickName: '美食探索家',
        avatarUrl: '',
        level: '黄金会员',
        loginTime: new Date().toISOString()
      };
      
      wx.setStorageSync('userInfo', userInfo);
      
      wx.hideLoading();
      
      // 显示成功提示
      wx.showToast({
        title: '登录成功',
        icon: 'success',
        duration: 1500
      });

      // 延迟跳转
      setTimeout(() => {
        this.navigateToIndex();
      }, 1500);
      
    }, 1000);
  },

  // 手机号登录
  onPhoneLogin() {
    wx.showToast({
      title: '功能开发中',
      icon: 'none',
      duration: 2000
    });
  },

  // 跳转到首页
  navigateToIndex() {
    wx.redirectTo({
      url: '/pages/index/index',
    });
  },

  // 查看用户协议
  onViewAgreement() {
    wx.showModal({
      title: '用户协议',
      content: '这里是用户协议的详细内容...',
      showCancel: false,
      confirmText: '我知道了'
    });
  },

  // 查看隐私政策
  onViewPrivacy() {
    wx.showModal({
      title: '隐私政策',
      content: '这里是隐私政策的详细内容...',
      showCancel: false,
      confirmText: '我知道了'
    });
  }
});
