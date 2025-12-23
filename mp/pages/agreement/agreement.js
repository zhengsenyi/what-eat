// pages/agreement/agreement.js
Page({
  data: {
    type: 'user', // 'user' 用户协议, 'privacy' 隐私政策
    title: '用户协议'
  },

  onLoad(options) {
    const type = options.type || 'user';
    this.setData({
      type: type,
      title: type === 'privacy' ? '隐私政策' : '用户协议'
    });
    
    wx.setNavigationBarTitle({
      title: type === 'privacy' ? '隐私政策' : '用户协议'
    });
  }
});